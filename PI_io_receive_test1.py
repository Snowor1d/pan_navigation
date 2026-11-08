# import socketio

# sio = socketio.Client()

# @sio.event
# def connect():
#     print("I'm connected!")
#     sio.emit('distance', {'data': 'Hello Server'})

# @sio.event
# def connect_error(data):
#     print("The connection failed!")

# @sio.event
# def disconnect():
#     print("I'm disconnected!")

# # @sio.event
# # def response(data):
# #     print('Server said:', data)

# # 수신 이벤트 핸들러
# @self.sio.on("location_info")
# def handle_location_info(data):
#     self.update_location_info(data)

# @self.sio.on("vehicle_info")
# def handle_vehicle_info(data):
#     self.update_vehicle_info(data)

    


#     def update_vehicle_info(self, data):
#         try:
#             # 데이터가 JSON 형식으로 파싱될 수 있는지 확인
#             if isinstance(data, str):
#                 vehicle_info_data = json.loads(data)
#             else:
#                 vehicle_info_data = data

#             # 'data' 필드에서 차량 정보 추출
#             vehicle_data = vehicle_info_data.get("data", {})
#             # 차량 정보를 문자열로 변환
#             vehicle_info_str = f"AutoDrivingStatus: {vehicle_data.get('AutoDrivingStatus', 'N/A')}, timestamp: {vehicle_data.get('timestamp', 'N/A')} degrees"
#             # 이 정보를 클래스 변수에 저장
#             self.vehicle_info = vehicle_info_str
#         except Exception as e:
#             print(f"Error updating vehicle information: {e}")

# if __name__ == '__main__':
#     sio.connect('http://192.168.17.25:8010')
#     sio.wait()


import smbus
import json
import numpy as np
import multiprocessing as mp
import socketio
import threading
import zlib
from tokenize import String
import time
import serial
import json

ser = serial.Serial('/dev/ttyS0', 115200)

class mainStreamClass:
    def __init__(self):
        # 상태 관련 속성 초기화
        self.server_message = ""
        # self.location_info = "Initializing..."
        # self.vehicle_info = "Initializing..."
        self.connected = False

        self.mode_lock = threading.Lock()

        # Socket.IO 클라이언트 초기화 및 서버에 연결
        self.sio = socketio.Client()
        self.register_handlers()
        #self.sio.connect('http://192.168.0.200:8010')
        self.sio.connect('http://192.168.182.134:8010')
        
        
        # I2C 인스턴스 생성 및 센서 주소 설정
        self.bus = smbus.SMBus(1)  # I2C 인스턴스 생성
        self.ADDRESS = 0x52  # 센서의 I2C 주소
        

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
            # on_data = "1,0,0,0,0\n"
            # ser.write(on_data.encode())
            
        @self.sio.on("reset_mode_select_web")
        def handle_reset_mode(data):
            self.update_reset_mode(data)
            reset_data = "0,0,0,0,0,0\n"
            ser.write(reset_data.encode())
            print(reset_data)

        @self.sio.on("line_on")
        def handle_auto_on(data):
            self.update_line_on(data)
            on_data = "3,0,0,0,0,0\n"
            ser.write(on_data.encode())
            print(on_data)
                
        @self.sio.on("line_off")
        def handle_auto_off(data):
            self.update_line_off(data)
            off_data = "4,0,0,0,0,0\n"
            ser.write(off_data.encode())
            print(off_data)

        @self.sio.on("remote_signal")
        def handle_remote_signal(data):
            self.update_remote_signal(data)

        @self.sio.on("auto_signal")
        def handle_auto_signal(data):
            self.update_auto_signal(data)

        @self.sio.on("emergency_stop_start")
        def handle_emergency_stop(data):
            self.update_emergency_stop(data)
            stop_data = "4,0,0,0,0,0\n"
            ser.write(stop_data.encode())
            print(stop_data)


        #@self.sio.on("joy_controller")
        #def handle_joy_controller(data):
        #    self.update_joy_controller(data)

        #@self.sio.on("g29_controller")
        #def handle_g29_controller(data):
        #    self.update_g29_controller(data)

        

    def send_front_distance(self, distance):
        front_distance = {
            "data": distance,
            "type": "front_distance"
        }
        self.sio.emit('front_distance', front_distance)
    

    def update_drivestart_mode(self, data):
        print("drivestart data received:", data)

    def update_remote_mode(self, data):
        print("Remote mode data received:", data)
    # 여기에 수신된 데이터를 처리하는 로직을 구현하세요.
    # 예를 들어, 수신된 데이터를 기반으로 클래스 내 다른 작업을 수행하거나, 상태를 업데이트할 수 있습니다.

    def update_auto_mode(self, data):
        print("Auto mode data received:", data)
    def update_reset_mode(self, data):
        print("Reset mode data received:", data)
        

    # def update_remote_signal(self, data):
    #     print("Remote_signal data received:", data)

    # def handle_remote_signal(self, data):
        
    def update_remote_signal(self, data):
        try:
            data_dict = json.loads(data)
            print("Remote_signal data received:", data_dict)
            
            #추출
            m = '1'
            A = data_dict['data']['A']
            B = data_dict['data']['B']
            FB = data_dict['data']['FB']
            LR = data_dict['data']['LR']
            FLB = data_dict['data']['FLB']
            
            FB = round(float(FB), 3)
            LR = round(float(LR), 3)
            FLB = round(float(FLB), 3)
            FBLR = str(m)+','+str(A)+','+str(B)+','+str(int(FB * 100))+','+str(int(LR* 100))+','+str(int(FLB* 100))+'\n'
            ser.write(FBLR.encode())
            print(FBLR)
            
        except Exception as e:
            print(f"Error processing remote signal data: {e}")
            
        
    def update_auto_signal(self, data):
        try:
            data_dict = json.loads(data)
            print("Auto_signal data received:", data_dict)
            
            #추출
            m = '5'
            A = '0'
            B = '0'
            FB = data_dict['data']['FB']
            LR = data_dict['data']['LR']
            FLB = '0'
            FB = round(float(FB), 3)
            LR = round(float(LR), 3)
            FBLR = str(m)+','+str(A)+','+str(B)+','+str(int(FB * 400))+','+str(int(LR* 400))+','+str(int(FLB* 400))+'\n'
            ser.write(FBLR.encode())
            print(FBLR)
            
        except Exception as e:
            print(f"Error processing auto signal data: {e}")
            
            



    # def update_auto_on(self, data):
    #     print("auto_on data received:", data)

    # def update_auto_off(self, data):
    #     print("auto_off data received:", data)
    def update_line_on(self, data):
        try:
            # 수신된 데이터를 바로 출력
            print("line_on data received:", data)
            
        except Exception as e:
            # 오류가 발생한 경우 오류 메시지 출력
            print(f"Error processing auto_on data: {e}")

    def update_line_off(self, data):
        try:
            # 수신된 데이터를 바로 출력
            print("line_off data received:", data)
        except Exception as e:
            # 오류가 발생한 경우 오류 메시지 출력
            print(f"Error processing auto_off data: {e}")


    def update_emergency_stop(self, data):
        print("EMERGENCY:", data)

    # def update_emergency_evacuation(self, data):
    #     print("Emergency evacuation data received:", data)

    #def update_joy_controller(self, data):
    #    print("Joy controller data received:", data)

    #def update_g29_controller(self, data):
    #    print("G29_controller data received:", data)




    #def read_distance(self):
    #    data = self.bus.read_i2c_block_data(self.ADDRESS, 0x00, 2)
    #    distance = data[0] << 8 | data[1]
    #    return distance

    def main_loop(self):
        try: 
            while True:
    #            distance = self.read_distance()
    #            if distance < 10000:
    #                #distance_cm = distance  # Convert to centimeters
    #                print("Distance: {}cm".format(distance))
    #                self.send_front_distance(distance)
                time.sleep(0.5)
        except KeyboardInterrupt:
            print("Measurement stopped by User")
    #        self.bus.close()



if __name__ == "__main__":
    msc = mainStreamClass()
    try:
        msc.main_loop()
    except KeyboardInterrupt:
        print("프로그램을 종료합니다.")
        msc.sio.disconnect()

