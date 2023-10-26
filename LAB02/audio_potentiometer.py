import serial
import time
import sys
import pygame
 
COM_PORT = '/dev/cu.usbmodem11201'  # 請自行修改序列埠名稱
BAUD_RATES = 9600
ser = serial.Serial(COM_PORT, BAUD_RATES)
if ser.is_open is True:
    print("Serial port is open!")
music_state = 0

fixed_volume = 1
threshold = 0.5

try:
    file=r'/Users/lijiacian/2023 fall/計算機系統實驗/112-1_CSL/LAB02/you-belong-with-me.mp3' # 播放音樂的路徑
    pygame.mixer.init()
    track = pygame.mixer.music.load(file)
    pygame.mixer.music.play()
    pygame.mixer.music.set_volume(fixed_volume)
    pygame.mixer.music.pause()
    
    while True:
        while ser.in_waiting:
            res = ser.read_until().decode()
            if res == "v\n":
                v = int(ser.read_until().decode()) / 1024
                if v > threshold and not music_state:
                    music_state = 1
                    pygame.mixer.music.unpause()
                    print("Play\n")
                elif v <= threshold and music_state:
                    music_state = 0
                    pygame.mixer.music.pause()
                    print("Pause\n")
 
except KeyboardInterrupt:
    ser.close()
    print('exit')

