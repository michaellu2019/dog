import time
import math
import curses
import pygame
from mutagen.mp3 import MP3

import RPi.GPIO as GPIO

import vector
from movement import move_ik, write_servo
from constants import *

run_program = True
mode = "standing"
walking = {
	"direction": "none",
	"starting": False
}
speaking = {
    "duration": 0,
    "play": False,
    "start_time": 0,
    "current_time": 0,
    "file_name": ""
}

screen = curses.initscr()
curses.noecho()
curses.cbreak()
screen.keypad(True)
screen.nodelay(1)

pygame.mixer.init()
pygame.mixer.music.set_volume(2.0)

def setup():
    curses_log("Configuring all servos...")
    for i in range(len(servo_channels)):
        for j in range(len(servo_channels[i])):
            curses_log("Configuring Servo " + str(i) + " " + str(j))
            write_servo(servo_channels[i][j], servo_neutral_vals[i][j])
            time.sleep(0.5)

    curses_log("Servo configuration complete...")
    time.sleep(0.5)
    screen.clear()
    screen.refresh()

def loop(interval):
    global pos
    global rot
    global mode
    global walking
    global speaking
    global gait_pos
    global gait_states
    global gait
    global forward_gait
    global reverse_gait
    global left_gait
    global right_gait
    global left_turn_gait
    global right_turn_gait

    time.sleep(interval)
    
    screen.clear()
    screen.refresh()
    char = screen.getch()
    if char > 0:
    	screen.clear()
        if char == ord("q"):
            curses_log("Escape")
            move("pos", [-pos[0], -pos[1], -pos[2] + DEFAULT_HEIGHT])
            move("rot", [-rot[0], -rot[1], -rot[2]])
            return False
        
        if char == ord(" "):
            mode = "standing"
            walking["direction"] = "none"
            walking["starting"] = False
            curses_log("Reset")
            move("pos", [-pos[0], -pos[1], -pos[2] + DEFAULT_HEIGHT])
            move("rot", [-rot[0], -rot[1], -rot[2]])
        
        if mode == "standing":
            if char == ord("o"):
                curses_log("Pitch Up")
                move("rot", [0.0, -STANDING_SPEED, 0.0])
            elif char == ord("l"):
                curses_log("Pitch Down")
                move("rot", [0.0, STANDING_SPEED, 0.0])
            if char == ord("k"):
                curses_log("Yaw Left")
                move("rot", [0.0, 0.0, STANDING_SPEED])
            elif char == ord(";"):
                curses_log("Yaw Right")
                move("rot", [0.0, 0.0, -STANDING_SPEED])
            if char == ord("i"):
                curses_log("Roll Up")
                move("rot", [STANDING_SPEED, 0.0, 0.0])
            if char == ord("p"):
                curses_log("Roll Down")
                move("rot", [-STANDING_SPEED, 0.0, 0.0])
                
            if char == ord("w"):
                curses_log("Move Forward")
                move("pos", [STANDING_SPEED, 0.0, 0.0])
            elif char == ord("s"):
                curses_log("Move Backward")
                move("pos", [-STANDING_SPEED, 0.0, 0.0])
            if char == ord("a"):
                curses_log("Move Left")
                move("pos", [0.0, -STANDING_SPEED, 0.0])
            elif char == ord("d"):
                curses_log("Move Right")
                move("pos", [0.0, STANDING_SPEED, 0.0])
            if char == ord("r"):
                curses_log("Move Up")
                move("pos", [0.0, 0.0, STANDING_SPEED])
            if char == ord("f"):
                curses_log("Move Down")
                move("pos", [0.0, 0.0, -STANDING_SPEED])

            if char == ord("1"):
                speak("gentrification")
            elif char == ord("2"):
                speak("sing")
            elif char == ord("3"):
                speak("boulder")
            elif char == ord("4"):
                speak("donkey")
            elif char == ord("5"):
                speak("die1")
            elif char == ord("6"):
                speak("die2")
        
        if mode == "walking":
            if char == ord("w"):
                walking["direction"] = "forward"
                walking["starting"] = True
                gait = forward_gait
                curses_log("Walk Forward")
            elif char == ord("s"):
                walking["direction"] = "backward"
                walking["starting"] = True
                gait = reverse_gait
                curses_log("Walk Backward")
            if char == ord("a"):
                walking["direction"] = "left"
                walking["starting"] = True
                gait = left_gait
                curses_log("Walk Left")
            elif char == ord("d"):
                walking["direction"] = "right"
                walking["starting"] = True
                gait = right_gait
                curses_log("Walk Right")
            elif char == curses.KEY_LEFT:
                walking["direction"] = "left_turn"
                walking["starting"] = True
                gait = left_turn_gait
                curses_log("Turn Left")
            elif char == curses.KEY_RIGHT:
                walking["direction"] = "right_turn"
                walking["starting"] = True
                gait = right_turn_gait
                curses_log("Turn Right")

        
        if char == curses.KEY_ENTER or char == 10 or char == 13:
            mode = "walking" if mode == "standing" else "standing"
            walking["direction"] = "none"
            walking["starting"] = False
            curses_log("Changed Mode to " + mode[0].upper() + mode[1:])
            curses_log("Reset")
            move("pos", [-pos[0], -pos[1], -pos[2] + DEFAULT_HEIGHT])
            move("rot", [-rot[0], -rot[1], -rot[2]])

    else:
    	walking["direction"] = "none"
    	walking["starting"] = False

    gait_grounded = all([abs(gait_pos[i][2] - DEFAULT_HEIGHT) < EPSILON for i in range(NUM_LEGS)])
    # curses_log(str(gait_grounded) + " GAIT GROUNDED " + str([gait_pos[i][2] == DEFAULT_HEIGHT for i in range(NUM_LEGS)]) + "--" + str([gait_pos[i][2] for i in range(NUM_LEGS)]))
    if walking["direction"] != "none" or (not gait_grounded or walking["starting"]):
    	curses_log("Walking")
        for i in range(NUM_LEGS):
            if vector.eq(gait_pos[i], gait_dest[i]):
                gait_pos[i] = gait_dest[i]
                gait_src[i] = gait_dest[i]
                gait_states[i] = gait_states[i] + 1 if gait_states[i] + 1 < len(gait[i]) else 0
                gait_dest[i] = gait[i][gait_states[i]]
            
            gait_vel = vector.scalar_div(vector.sub(gait_dest[i], gait_src[i]), gait_divs)
            gait_pos[i] = vector.add(gait_pos[i], gait_vel)
            move_ik(i, gait_pos[i], rot)
    	curses_log(str(gait_pos))      

    if speaking["play"] and speaking["current_time"] - speaking["start_time"] < speaking["duration"]:
        speaking["current_time"] = time.time()
        curses_log("Playing: \"" + speaking["file_name"] + "\"")
        curses_log("Duration: " + str(speaking["duration"]))

        for i in range(NUM_HEAD_SERVOS):
            if abs(speaking_animation_pos[i] - speaking_animation_dest[i]) < EPSILON:
                speaking_animation_pos[i] = speaking_animation_dest[i]
                speaking_animation_src[i] = speaking_animation_dest
                speaking_animation_states[i] = speaking_animation_states[i] + 1 if speaking_animation_states[i] + 1 < len(speaking_animation) else 0 
                speaking_animation_dest = speaking_animation[speaking_animation_states[i]]

            speaking_animation_vel = (speaking_animation_dest[i] - speaking_animation_src[i])/speaking_animation_divs
            speaking_animation_pos[i] += speaking_animation_vel
            write_servo(servo_channels[-1][i], speaking_animation_pos[i])
    elif speaking["play"] speaking["current_time"] - speaking["start_time"] > speaking["duration"]:
        speaking["play"] = False
        speaking["start_time"] = 0
        speaking["current_time"] = 0
        speaking["duration"] = 0

        for i in range(NUM_HEAD_SERVOS):
            write_servo(servo_channels[-1][i], servo_neutral_vals[-1][i])

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
        
def speak(file_name):
    pygame.mixer.music.load("audio/" + file_name + ".mp3")
    pygame.mixer.music.play()
    speaking["duration"] = MP3("audio/" + file_name + ".mp3").info.length
    speaking["start_time"] = time.time()
    speaking["current_time"] = time.time()
    speaking["play"] = True
    speaking["file_name"] = file_name + ".mp3"

    curses_log("Playing: \"" + speaking["file_name"] + "\"")
    curses_log("Duration: " + str(speaking["duration"]))

def curses_log(msg):
    screen.addstr(msg + "\n")
    screen.refresh()

try:
	setup()
	while run_program:
		run_program = loop(0.01)
finally:
	print("EXIT")
	GPIO.cleanup()
	curses.nocbreak()
	screen.keypad(0)
	curses.echo()
	curses.endwin()