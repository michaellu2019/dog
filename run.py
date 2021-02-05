import time
import math
import curses

import RPi.GPIO as GPIO

import vector
from movement import move_ik, write_servo
from constants import *

run_program = True
mode = "standing"
walking_mode = "none"

screen = curses.initscr()
curses.noecho()
curses.cbreak()
screen.keypad(True)
screen.nodelay(1)

def setup():
    curses_log("Configuring all servos...")
    for i in range(NUM_LEGS):
        for j in range(NUM_LEG_SERVOS):
            curses_log("Configuring Servo " + str(i) + " " + str(j))
            write_servo(servo_channels[i][j], servo_neutral_vals[i][j])
            time.sleep(1.0)
    curses_log("Servo configuration complete...")
    time.sleep(1.0)
    screen.clear()
    screen.refresh()

def loop(interval):
    global pos
    global rot
    global mode
    global walking_mode
    global gait_pos
    global gait_states

    time.sleep(interval)
    
    char = screen.getch()
    speed = 0.5
    if char > 0:
        screen.clear()
        
        if char == ord("q"):
            curses_log("Escape")
            move("pos", [-pos[0], -pos[1], -pos[2] + DEFAULT_HEIGHT])
            move("rot", [-rot[0], -rot[1], -rot[2]])
            return False
        
        if char == ord(" "):
            mode = "standing"
            walking_mode = "none"
            curses_log("Reset")
            move("pos", [-pos[0], -pos[1], -pos[2] + DEFAULT_HEIGHT])
            move("rot", [-rot[0], -rot[1], -rot[2]])
        
        if mode == "standing":
            if char == ord("o"):
                curses_log("Pitch Up")
                move("rot", [0.0, -speed, 0.0])
            elif char == ord("l"):
                curses_log("Pitch Down")
                move("rot", [0.0, speed, 0.0])
            if char == ord("k"):
                curses_log("Yaw Left")
                move("rot", [0.0, 0.0, speed])
            elif char == ord(";"):
                curses_log("Yaw Right")
                move("rot", [0.0, 0.0, -speed])
            if char == ord("i"):
                curses_log("Roll Up")
                move("rot", [speed, 0.0, 0.0])
            if char == ord("p"):
                curses_log("Roll Down")
                move("rot", [-speed, 0.0, 0.0])
                
            if char == ord("w"):
                curses_log("Move Forward")
                move("pos", [speed, 0.0, 0.0])
            elif char == ord("s"):
                curses_log("Move Backward")
                move("pos", [-speed, 0.0, 0.0])
            if char == ord("a"):
                curses_log("Move Left")
                move("pos", [0.0, -speed, 0.0])
            elif char == ord("d"):
                curses_log("Move Right")
                move("pos", [0.0, speed, 0.0])
            if char == ord("r"):
                curses_log("Move Up")
                move("pos", [0.0, 0.0, speed])
            if char == ord("f"):
                curses_log("Move Down")
                move("pos", [0.0, 0.0, -speed])
        
        if mode == "walking":
            if char == ord("w"):
                walking_mode = "forward"
                curses_log("Walk Forward")
                
            elif char == ord("s"):
                curses_log("Walk Backward")
            if char == ord("a"):
                curses_log("Walk Left")
            elif char == ord("d"):
                curses_log("Walk Right")
        
        if char == curses.KEY_ENTER or char == 10 or char == 13:
            mode = "walking" if mode == "standing" else "standing"
            walking_mode = "none"
            curses_log("Changed Mode to " + mode[0].upper() + mode[1:])
            curses_log("Reset")
            move("pos", [-pos[0], -pos[1], -pos[2] + 89.0])
            move("rot", [-rot[0], -rot[1], -rot[2]])

    gait_grounded = all([gait_pos[i][2] == DEFAULT_HEIGHT for i in range(NUM_LEGS)])
    curses_log(str(gait_grounded) + " GAIT GROUNDED " + str([gait_pos[i][2] == DEFAULT_HEIGHT for i in range(NUM_LEGS)]) + "--" + str([gait_pos[i][2] for i in range(NUM_LEGS)]))
    curses_log(walking_mode)
    if walking_mode == "forward":
    	curses_log("Walking Forward")
        for i in range(NUM_LEGS):
            if vector.eq(gait_pos[i], gait_dest[i]):
                gait_pos[i] = gait_dest[i]
                gait_states[i] = gait_states[i] + 1 if gait_states[i] + 1 < len(gait) else 0
                gait_src[i] = gait_dest[i]
                gait_dest[i] = gait[gait_states[i]]
            
            gait_vel = vector.scalar_div(vector.sub(gait_dest[i], gait_src[i]), gait_divs)
            gait_pos[i] = vector.add(gait_pos[i], gait_vel)
            move_ik(i, gait_pos[i], rot)
    	curses_log(str(gait_pos))      

    return True

def move(move_type, vel):
    prev_pos = pos
    prev_rot = rot
    
    if move_type == "pos":
        pos[0] += float(vel[0])
        pos[1] += float(vel[1])
        pos[2] += float(vel[2])
    elif move_type == "rot":
        rot[0] += float(vel[0])
        rot[1] += float(vel[1])
        rot[2] += float(vel[2])
    
    curses_log("Position: " + str(tuple(pos)))
    curses_log("Rotation: " + str(tuple(rot)))
    
    error = False
    for i in range(NUM_LEGS):
        move_ik(i, pos, rot)
        
    """
        This code still caused a fire so maybe don't use it?
        try:
            move_ik(i, pos, rot)
        except ValueError:
            curses_log("Error! Dangerous orientation for servos! Fire!!!")
            error = True
            break
        
    if error:
        curses_log("Returning to previous orientation!")
        for i in range(NUM_LEGS):
            try:
                move_ik(i, prev_pos, prev_rot)
            except ValueError:
                curses_log("Error! Dangerous orientation for servos! Fire!!!")
                break
    """

def curses_log(msg):
    screen.addstr(msg + "\n")
    screen.refresh()

try:
	setup()
	while run_program:
		run_program = loop(0.05)
finally:
	print("EXIT")
	GPIO.cleanup()
	curses.nocbreak()
	screen.keypad(0)
	curses.echo()
	curses.endwin()