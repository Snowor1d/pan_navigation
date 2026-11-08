import smbus
import time
import json
import numpy as np
import multiprocessing as mp
import socketio
import threading
import zlib
from tokenize import String
import time
import serial

ser = serial.Serial('/dev/ttyS0', 115200)

class mainStreamClass:
    def __init__(self):
        # 상태 관련 속성 초기화
        self.server_message = ""
        self.connected = False
        self.mode_lock = threading.Lock()

        # Socket.IO 클라이언트 초기화 및 서버에 연결
        self.sio = socketio.Client()
        self.register_handlers()
        self.sio.connect('http://192.168.66.134:8010')
        

    def register_handlers(self):
        @self.sio.event
        def connect():
            print("Connected to the server")
            self.connected = True
            #self.send_message("Client connected", "client_UI")

        @self.sio.event
        def disconnect():
            print("Disconnected from the server")
            self.connected = False

        # @self.sio.event
        # def response(data):
        #     print('Server said:', data)

        # 수신 이벤트 핸들러
        @self.sio.on("drive_start")
        def handle_drivestart_mode(data):
            self.update_drivestart_mode(data)

        @self.sio.on("remote_mode_select_web")
        def handle_remote_mode(data):
            self.update_remote_mode(data)

        @self.sio.on("auto_mode_select_web")
        def handle_auto_mode(data):
            self.update_auto_mode(data)

        @self.sio.on("auto_mode_on")
        def handle_auto_on(data):
            self.update_auto_on(data)

        @self.sio.on("auto_mode_off")
        def handle_auto_off(data):
            self.update_auto_off(data)

        @self.sio.on("remote_signal")
        def handle_remote_signal(data):
            self.update_remote_signal(data)

        @self.sio.on("emergency_stop_start")
        def handle_emergency_stop(data):
            self.update_emergency_stop(data)

        @self.sio.on("emergency_evacuation_start")
        def handle_emergency_evacuation(data):
            self.update_emergency_evacuation(data)

        @self.sio.on("joy_controller")
        def handle_joy_controller(data):
            self.update_joy_controller(data)

        @self.sio.on("g29_controller")
        def handle_g29_controller(data):
            self.update_g29_controller(data)



if __name__ == "__main__":
    msc = mainStreamClass()
    try:
        # 프로그램을 계속 실행 상태로 유지
        while True:
            time.sleep(1)  # CPU 사용을 줄이기 위해 대기
    except KeyboardInterrupt:
        print("프로그램을 종료합니다.")
        msc.sio.disconnect()


# I2C 인스턴스 생성 및 센서 주소 설정
bus = smbus.SMBus(1)  # 대부분의 라즈베리 파이에서 I2C 버스 번호는 1입니다.
ADDRESS = 0x52  # 센서의 I2C 주소입니다. 데이터시트를 확인하세요.

def read_distance():
    # TOF 센서에서 거리 데이터 읽기
    # 이 함수는 센서와의 통신 방식에 따라 달라질 수 있습니다. 데이터시트를 참고하여 수정해야 할 수도 있습니다.
    data = bus.read_i2c_block_data(ADDRESS, 0x00, 2)  # 센서로부터 2바이트 데이터 읽기
    # 데이터 변환 (예: 두 바이트를 합쳐서 거리 값 계산)
    distance = data[0] << 8 | data[1]
    return distance

try:
    while True:
        distance = read_distance()
        if distance < 100:
            print("Distance: {}cm".format(distance))
        else :
            distance_m = distance / 100
            #print("Distance: {}m".format(distance_m))
            
            lane = int(distance_m)
            
            ser.write(lane.encode())
            
        time.sleep(1)  # 1초 대기
except KeyboardInterrupt:
    print("Measurement stopped by User")
    bus.close()
