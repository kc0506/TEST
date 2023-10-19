import serial
import time
import sys
import pygame
 
COM_PORT = 'com3'  # 請自行修改序列埠名稱
BAUD_RATES = 9600
ser = serial.Serial(COM_PORT, BAUD_RATES)
if ser.is_open is True:
    print("Serial port is open!")
music_state = 0

fixed_volume = 1
threshold = 0.5

try:
    file=r'D:\\zoets\Desktop\\NTU\\112-1\\計算機系統實驗\\112-1_CSL\\LAB02\\you-belong-with-me.mp3' # 播放音樂的路徑
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
                if v > threshold:
                    pygame.mixer.music.unpause()
                    print("Turn on music\n")
                else:
                    pygame.mixer.music.pause()
                    print("Turn off music\n")
 
except KeyboardInterrupt:
    ser.close()
    print('exit')

