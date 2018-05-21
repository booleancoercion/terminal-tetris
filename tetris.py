#!/usr/bin/env python3

import matrix, blocks, sys, time, random, os, traceback, threading

from termcolor import colored
from blocks import Ghost, IBlock, OBlock, TBlock, SBlock, ZBlock, LBlock, JBlock
from blocks import CLOCKWISE, COUNTERCLOCKWISE
from pynput import keyboard

msg = """Welcome to Tetris!
1. Play
2. Exit"""

print(msg)

while True:
    try:
        inp = input("Your choice: ")
    except EOFError:
        print("<exiting>")
        sys.exit()
    else:
        if(inp == '1'):
            break
        elif(inp == '2'):
            sys.exit()
        else:
            print("Invalid choice.")

locked = False
score = 0
lines = 0
grid = matrix.blank(22, 10)
active = None
fall_timer = None
active_ghost = None
hold = None
bag = []
level = 1
linesleft = 5
delay = 1
b2b = 0
noexceptions = True
holdlock = False

block_classes = [IBlock, JBlock, LBlock, TBlock, SBlock, ZBlock, OBlock]

disp = {
    IBlock:{'pixels':[[0, 0], [1, 0], [2, 0], [3, 0]], 'width':4, 'height':1},
    JBlock:{'pixels':[[0, 0], [0, 1], [1, 1], [2, 1]], 'width':3, 'height':2},
    LBlock:{'pixels':[[2, 0], [0, 1], [1, 1], [2, 1]], 'width':3, 'height':2},
    TBlock:{'pixels':[[1, 0], [0, 1], [1, 1], [2, 1]], 'width':3, 'height':2},
    SBlock:{'pixels':[[1, 0], [2, 0], [0, 1], [1, 1]], 'width':3, 'height':2},
    ZBlock:{'pixels':[[0, 0], [1, 0], [1, 1], [2, 1]], 'width':3, 'height':2},
    OBlock:{'pixels':[[0, 0], [1, 0], [0, 1], [1, 1]], 'width':2, 'height':2}
}

def printa(s):
    print(s.replace('.', '\033['), end='')

def printgrid(mat, nl=True):
    global bag

    g = mat.rows[2:]
    out = '\n┌'+'─'*20+'┐\n'
    for r in g:
        out += '│'
        for e in r:
            if(e == 0):
                out += '  '
            elif(e < 8):
                out += colored('██', blocks.colors[e])
            elif(e == 8):
                out += "##"
        out += '│\n'
    out += '└'+'─'*20+'┘'
    print(out, end='')

    printa('.21A.C.s')
    slen = max(len(str(score)), 6)
    print('┌─'+'─'*slen+'─┬────────┬──────────┬───────┐', end='')
    printa('.u.B')
    print('│ Score:' + ' '*max(slen-6, 0) + ' │ Level: │ Cleared: │ Goal: │', end='')
    printa('.u.2B')
    print('│ '+str(score)+' '*max(slen-len(str(score)), 0)+' │ '+str(level)+' '*(6-len(str(level)))+' │ ', end='')
    print(str(lines) + ' '*(8-len(str(lines))) + ' │ ' + str(linesleft) + ' '*(5-len(str(linesleft))) + ' │', end='')
    printa('.u.3B')
    print('└─'+'─'*slen+'─┴────────┴──────────┴───────┘', end='')


    printa('.u.5B')
    print('Next:', end='')
    if(len(bag) < 3):
        temp = block_classes[:]
        random.shuffle(temp)
        bag = temp + bag
    nxt = bag[-1]
    nxtd = disp[nxt]
    nxt2 = bag[-2]
    nxt2d = disp[nxt2]

    height = max(nxtd['height'], nxt2d['height'])

    nxtm = matrix.blank(height, nxtd['width'])
    nxt2m = matrix.blank(height, nxt2d['width'])

    for p in nxtd['pixels']:
        nxtm[p[1]][p[0]] = nxt.col
    
    for p in nxt2d['pixels']:
        nxt2m[p[1]][p[0]] = nxt2.col
    
    printa('.u.6B')
    print('┌─'+'─'*nxtd['width']*2+'─┬─'+'─'*nxt2d['width']*2+'─┐', end='')
    printa('.K')
    for r in range(height):
        printa('.u.'+str(7+r)+'B')
        print('│ ', end='')
        for c in range(nxtd['width']):
            e = nxtm[r][c]
            if(e > 0):
                print(colored('██', blocks.colors[e]), end='')
            else:
                print('  ', end='')
        
        print(' │ ', end='')
        
        for c in range(nxt2d['width']):
            e = nxt2m[r][c]
            if(e > 0):
                print(colored('██', blocks.colors[e]), end='')
            else:
                print('  ', end='')
        
        print(' │', end='')
        printa('.K')
    printa('.u.'+str(7+height)+'B')
    print('└─'+'─'*nxtd['width']*2+'─┴─'+'─'*nxt2d['width']*2+'─┘', end='')
    printa('.K')

    printa('.u.21B.D')

    if(hold != None):
        cc = hold.__class__
        h = disp[cc]['height']
        w = disp[cc]['width']
        m = matrix.blank(h, w)
        for p in disp[cc]['pixels']:
            m[p[1]][p[0]] = cc.col
        
        printa('.'+str(h+3)+'A.C.K.B.s')
        print('Hold:', end='')
        printa('.K.u.B')
        print('┌─'+'─'*w*2+'─┐', end='')
        printa('.K')
        for r in range(h):
            printa('.u.'+str(r+2)+'B')
            print('│ ', end='')
            for c in range(w):
                e = m[r][c]
                if(e > 0):
                    print(colored('██', blocks.colors[e]), end='')
                else:
                    print('  ', end='')
            
            print(' │', end='')
            printa('.K')
        
        printa('.u.'+str(h+2)+'B')
        print('└─'+'─'*w*2+'─┘', end='')
        printa('.K')

    if(nl):
        print()

def delrows(rows):
    global locked, active, active_ghost
    locked = True

    def change(col):
        for i in rows:
            r = grid[i]
            for j, _ in enumerate(r):
                r[j] = col
    
    change(7)
    time.sleep(0.2)
    change(1)
    time.sleep(0.2)
    change(7)
    time.sleep(0.2)
    change(1)
    time.sleep(0.2)

    change(0)

    for row in sorted(rows):
        for i in range(row, 1, -1):
            r = grid[i]
            for j, _ in enumerate(r):
                r[j] = grid[i-1][j]

    locked = False

    active = newblock()
    active_ghost = Ghost(active)

def get_delay():
    global delay
    return delay

def newblock():
    global bag, fall_timer, holdlock

    if(fall_timer != None):
        fall_timer.cancel()

    reset_ldelay()

    if(len(bag) == 0):
        bag = block_classes[:]
        random.shuffle(bag)

    def func():
        global fall_timer
        if(active != None):
            try:
                move_down()
            except:
                pass
            fall_timer = threading.Timer(interval=get_delay(), function=func)
            fall_timer.start()

    fall_timer = threading.Timer(interval=get_delay(), function=func)
    fall_timer.start()
    holdlock = False
    return bag.pop()(grid)

def lock():
    global active, active_ghost, lines, score, level, linesleft, b2b, fall_timer, delay, noexceptions

    if(fall_timer != None):
        fall_timer.cancel()

    for p in active._pixels:
        if(p[1] < 2):
            print("Game Over!")
            noexceptions = False

    rows = set()

    for p in active._pixels:
        rows = rows | {p[1]}

    active_ghost.remself()
    active = None
    active_ghost = None

    completed = rows | set()

    for row in completed:
        for e in grid[row]:
            if e == 0:
                completed = completed - {row}

    if(len(completed) != 0):
        t = threading.Thread(target=delrows, args=(list(completed),))
        t.start()

        lines += 1
        cleared = len(completed)
        score += [100, 300, 500, 800][cleared-1]*level
        linesleft -= [1, 3, 5, 8][cleared-1]
        
        if(cleared == 4):
            b2b += 1
            if(b2b > 1):
                score += 600*level
        else:
            b2b = 0
        
        if(linesleft <= 0):
            level += 1
            delay = delay * (3/4)
            linesleft = level*5
    
    else:
        active = newblock()
        active_ghost = Ghost(active)

lock_delay = 0.3
lock_timer = None

def move_down():
    try:
        active.move(0, 1)
        if(active_ghost != None):
            active_ghost.update()
        reset_ldelay()
    except:
        def tmr():
            try:
                global lock_delay, lock_timer
                lock_delay -= 0.01
                if(lock_delay < 0):
                    lock()
                else:
                    lock_timer = threading.Timer(0.01, tmr)
                    lock_timer.start()
            except:
                pass
        
        lock_timer = threading.Timer(0.01, tmr)
        lock_timer.start()

def reset_ldelay():
    global lock_delay, lock_timer
    if(lock_timer != None and lock_delay < 0.3):
        lock_timer.cancel()
        lock_delay = 0.3

left_t = None
right_t = None
down_t = None

left_f = True
right_f = True

left_p = False
right_p = False

rotlock = False

def on_press(key):
    global active, active_ghost, score, noexceptions, bag, hold, locked
    global left_t, right_t, down_t, left_p, right_p, rotlock, holdlock
    if(locked): return
    try:
        if(active != None):
            if(key == keyboard.Key.left):
                if(left_t == None):
                    left_p = True
                    def left():
                        global active, active_ghost, left_t, left_f, left_p
                        if(left_p == False):
                            return
                        try:
                            active.move(-1, 0)
                            active_ghost.update()
                            reset_ldelay()
                        except:
                            pass
                        if(left_f):
                            left_f = False
                            time.sleep(0.2)
                            if(left_p == False):
                                return
                        left_t = threading.Timer(0.05, left)
                        left_t.start()
                    
                    left_t = threading.Timer(0, left)
                    left_t.start()

            elif(key == keyboard.Key.right):
                if(right_t == None):
                    right_p = True
                    def right():
                        global active, active_ghost, right_t, right_f, right_p
                        if(right_p == False):
                            return
                        try:
                            active.move(1, 0)
                            active_ghost.update()
                            reset_ldelay()
                        except:
                            pass
                        if(right_f):
                            right_f = False
                            time.sleep(0.2)
                            if(right_p == False):
                                return
                        
                        right_t = threading.Timer(0.05, right)
                        right_t.start()
                    
                    right_t = threading.Timer(0, right)
                    right_t.start()

            elif(key == keyboard.Key.down):
                if(down_t == None):
                    def down():
                        global active, active_ghost, score, down_t
                        try:
                            move_down()
                            if(fall_timer != None):
                                fall_timer.cancel()
                            score += 1
                        except:
                            pass
                        down_t = threading.Timer(get_delay()/10, down)
                        down_t.start()
                    
                    down()

            elif(key == keyboard.Key.up):
                if(not rotlock):
                    try:
                        active.rot()
                        rotlock = True
                        reset_ldelay()
                    except:
                        pass

            elif(key == keyboard.Key.shift):
                if(holdlock == False):
                    holdlock = True
                    active.remself()
                    active_ghost.remself()
                    hold, active = active, hold
                    if(active != None):
                        active = active.__class__(active._grid)
                    
                    else:
                        active = newblock()
                    
                    reset_ldelay()
                    active_ghost = Ghost(active)
            
            active_ghost.update()
        
        if(key == keyboard.Key.space and active != None):
            try:
                while True:
                    active.move(0, 1)
                    score += 2
            except:
                pass
            lock()

    except (IndexError, blocks.OccupiedError, blocks.RotationError):
        pass
    except:
        print("Unexpected error.")
        traceback.print_exc()
        noexceptions = False
        raise

def on_release(key):
    global left_t, right_t, down_t, noexceptions, fall_timer, left_f, right_f, left_p, right_p, rotlock
    try:
        if(key == keyboard.Key.left and left_t != None):
            left_t.cancel()
            left_t = None
            left_f = True
            left_p = False
        
        elif(key == keyboard.Key.right and right_t != None):
            right_t.cancel()
            right_t = None
            right_f = True
            right_p = False
        
        elif(key == keyboard.Key.down and down_t != None):
            down_t.cancel()
            down_t = None
            def func():
                global fall_timer
                if(active != None):
                    try:
                        move_down()
                    except:
                        pass
                    fall_timer = threading.Timer(interval=get_delay(), function=func)
                    fall_timer.start()
            
            fall_timer = threading.Timer(interval=get_delay(), function=func)
            fall_timer.start()
        
        elif(key == keyboard.Key.up):
            rotlock = False
    except:
        print("Unexpected error.")
        traceback.print_exc()
        noexceptions = False
        raise


listener = keyboard.Listener(on_press=on_press, on_release=on_release)
listener.start()

active = newblock()
active_ghost = Ghost(active)

printa('.2J')
os.system('stty -echo')

try:
    while noexceptions:
        printa('.H')
        printgrid(grid, nl=False)
        time.sleep(0.03)
    raise KeyboardInterrupt()
except KeyboardInterrupt:
    listener.stop()
    if(fall_timer != None):
        fall_timer.cancel()
    if(lock_timer != None):
        lock_timer.cancel()
    os.system('stty echo')
    printa('.2E\n')