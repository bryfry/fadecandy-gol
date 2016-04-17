#!/usr/bin/env python

import RPi.GPIO as GPIO
import opc
import time
import random

# Define channel numbers for red, blue and green buttons
# Uses GPIO.BOARD numbering
GPIO.setmode(GPIO.BOARD)
BUTTON_RED = 11
BUTTON_GREEN = 12
BUTTON_BLUE = 13

# Define info for Fadecandy
LED_STRING_LEN = 192
FLASH_CHANNELS = [0]

# Setup GPIO
for button in [BUTTON_RED, BUTTON_BLUE, BUTTON_GREEN]:
    GPIO.setup(button, GPIO.IN, pull_up_down=GPIO.PUD_UP)

pixels = [(0, 0, 0)] * LED_STRING_LEN

leds = opc.Client('localhost:7890')

RED = (35,0,0)
GREEN = (0,35,0)
BLUE = (0,0,35)

LIFESPAN = 500

d = (8,24)

def zero_matrix():
   return [(0, 0, 0)] * LED_STRING_LEN

def max_matrix():
   return [(100, 100, 100)] * LED_STRING_LEN

def color_matrix(color):
    color = tuple(2*x for x in color)
    return [color] * LED_STRING_LEN


def board_to_array(dimensions,board,color):
    p = [(0, 0, 0)] * LED_STRING_LEN
    for i in board: 
        index = (dimensions[0]*i[0])+i[1]
        p[index] = color
                
    return p	

def random_board(dimensions):
    i,j = 0,0
    board = set([])
    for i in xrange(0,dimensions[1]):
        for j in xrange(0,dimensions[0]):
            if random.randint(0,1):
                board.add((i,j))
    return board

def neighbors(dimensions,cell):
    x, y = cell
    yield (x - 1) % dimensions[1], (y - 1) % dimensions[0]
    yield x       % dimensions[1], (y - 1) % dimensions[0]
    yield (x + 1) % dimensions[1], (y - 1) % dimensions[0]
    yield (x - 1) % dimensions[1], y       % dimensions[0]
    yield (x + 1) % dimensions[1], y       % dimensions[0]
    yield (x - 1) % dimensions[1], (y + 1) % dimensions[0]
    yield x       % dimensions[1], (y + 1) % dimensions[0]
    yield (x + 1) % dimensions[1], (y + 1) % dimensions[0]

def apply_iteration(dimensions, board):
    new_board = set([])
    candidates = board.union(set(n for cell in board for n in neighbors(dimensions,cell)))
    for cell in candidates:
        count = sum((n in board) for n in neighbors(dimensions,cell))
        if count == 3 or (count == 2 and cell in board):
            new_board.add((cell[0]%dimensions[1],cell[1]%dimensions[0]))
    return new_board

def add_arrays(alpha,beta):
    return [(a[0]+b[0], a[1]+b[1], a[2]+b[2]) for a,b in zip(alpha,beta)]


display_boards = []
glider = {(0,1), (1,2), (2,0), (2,1), (2,2)}
display_boards.append((glider,(100,100,100),1000000))
display_boards.append((random_board(d),RED,150))
display_boards.append((random_board(d),GREEN,300))
display_boards.append((random_board(d),BLUE,LIFESPAN))
while True:
    if random.randint(0,40) == 1: 
        spawn = random.randint(0,2)
        if spawn == 0: display_boards.append((random_board(d),RED,LIFESPAN))
        if spawn == 1: display_boards.append((random_board(d),GREEN,LIFESPAN))
        if spawn == 2: display_boards.append((random_board(d),BLUE,LIFESPAN))

    # Note that buttons are inverted: GPIO.input() returns 1 if the button
    # is not pressed, 0 if it is pressed
    if GPIO.input(BUTTON_RED) == 0:
        display_boards.append((random_board(d),RED,LIFESPAN))
    if GPIO.input(BUTTON_GREEN) == 0:
        display_boards.append((random_board(d),GREEN,LIFESPAN))
    if GPIO.input(BUTTON_BLUE) == 0:
        display_boards.append((random_board(d),BLUE,LIFESPAN))
    if GPIO.input(BUTTON_RED) == 0 and GPIO.input(BUTTON_BLUE) == 0 and GPIO.input(BUTTON_GREEN) == 0:
        print "all pressed, resetting"
        display_boards = []
        display_boards.append((glider,(100,100,100),1000000))
    
    display_array = zero_matrix()
    i = 0
    for db in display_boards:
        if db[2] < 0:
            display_boards.pop(i)
            continue
        if not bool(db[0]): 
            display_boards.pop(i)
            continue
        display_array = add_arrays(display_array,board_to_array(d,db[0],db[1]))
        display_boards[i] = (apply_iteration(d,db[0]), db[1], db[2]-1)
        i+=1
    leds.put_pixels(display_array,0)
    time.sleep(.2)
