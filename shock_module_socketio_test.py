import RPi.GPIO as GPIO
import smbus
import time
import serial
import pynmea2
import socketio
import json
import zlib

# GPIO 설정
GPIO.setmode(GPIO.BCM)
GPIO.setup(27, GPIO.IN)

# MPU6050 설정
PWR_MGMT_1 = 0x6B
SMPLRT_DIV = 0x19
CONFIG = 0x1A
GYRO_CONFIG = 0x1B
INT_ENABLE = 0x38
ACCEL_XOUT_H = 0x3B
ACCEL_YOUT_H = 0x3D
ACCEL_ZOUT_H = 0x3F
GYRO_XOUT_H = 0x43
GYRO_YOUT_H = 0x45
GYRO_ZOUT_H = 0x47
Device_Address = 0x68  # MPU6050 기기 주소
gps_ser = serial.Serial("/dev/serial0", baudrate=38400, timeout=1)


# MPU6050 초기화 함수
def MPU_Init():
    bus.write_byte_data(Device_Address, SMPLRT_DIV, 7)
    bus.write_byte_data(Device_Address, PWR_MGMT_1, 1)
    bus.write_byte_data(Device_Address, CONFIG, 0)
    bus.write_byte_data(Device_Address, GYRO_CONFIG, 24)
    bus.write_byte_data(Device_Address, INT_ENABLE, 1)

# 가속도 및 자이로 데이터 읽기 함수
def read_raw_data(addr):
    high = bus.read_byte_data(Device_Address, addr)
    low = bus.read_byte_data(Device_Address, addr+1)
    value = ((high << 8) | low)
    if(value > 32768):
        value = value - 65536
    return value
    

# 자이로스코프 데이터 읽기
def read_gyro_data():
   gyro_x = read_raw_data(GYRO_XOUT_H) / 16384.0
   gyro_y = read_raw_data(GYRO_YOUT_H) / 16384.0
   gyro_z = read_raw_data(GYRO_ZOUT_H) / 16384.0
   return gyro_x, gyro_y, gyro_z

# GPS 데이터 읽기 함수
def read_gps():
    try:
        data = gps_ser.readline().decode('utf-8')
        if data.startswith('$GNGLL'):
            msg = pynmea2.parse(data)
            lat = round(msg.latitude, 6)
            lng = round(msg.longitude, 6)
            gps = ", Latitude=" + str(lat) + ", Longitude=" + str(lng)
            return gps
    except pynmea2.ParseError as e:
        print(f"GPS Parse Error: {e}")
        return None


# # 랜덤 GPS 데이터 생성 함수
# def generate_random_gps():
#     lat = round(random.uniform(-90.0, 90.0), 6)
#     lng = round(random.uniform(-180.0, 180.0), 6)
#     gps = "Latitude=" + str(lat) + ", Longitude=" + str(lng)
#     return gps

# 메시지 전송 함수
def send_message_with_crc_json(sio, message_data):
    msg = json.dumps(message_data, separators=(',', ':'))
    crc = zlib.crc32(msg.encode()) & 0xffffffff
    crc_msg_json = json.dumps({"crc": format(crc, 'x'), "type": "robot_location", "data": msg}, separators=(',', ':'))
    sio.emit("robot_location", crc_msg_json)

bus = smbus.SMBus(1) 	# or bus = smbus.SMBus(0) for older version boards
Device_Address = 0x68   # MPU6050 device address
MPU_Init()

# Socket.IO 클라이언트 설정 및 메인 로직
if __name__ == "__main__":
    sio = socketio.Client(logger=True, engineio_logger=True)
    
    @sio.event
    def connect():
        print("Connected to the server")
    @sio.event
    def disconnect():
        print("Disconnected from the server")

    sio.connect('http://192.168.28.134:8010')
    
    try:
        while True:
            gps_data = read_gps()
            gyro_x = read_raw_data(GYRO_XOUT_H)
            gyro_y = read_raw_data(GYRO_YOUT_H)
            gyro_z = read_raw_data(GYRO_ZOUT_H)
            Gx = round(gyro_x/131.0, 1)
            Gy = round(gyro_y/131.0, 1)
            Gz = round(gyro_z/131.0, 1)
            if gps_data is not None:
                message_data = {"data": f"{gps_data}, Gyro X={Gx}, Gyro Y={Gy}, Gyro Z={Gz}"}
                send_message_with_crc_json(sio, message_data)
                print (gps_data,"Gx=%.2f" %Gx, u'\u00b0'+ "/s", "\tGy=%.2f" %Gy, u'\u00b0'+ "/s", "\tGz=%.2f" %Gz, u'\u00b0')
            
    except KeyboardInterrupt:
        print("프로그램을 종료합니다.")
        sio.disconnect()
        GPIO.cleanup()




# import socketio
# import json
# import zlib
# import random
# import time

# # MPU6050 설정
# # 이 부분은 필요 없으니 제거했습니다.

# # 랜덤 GPS 데이터 생성 함수
# def generate_random_gps():
#     lat = round(random.uniform(-90.0, 90.0), 6)
#     lng = round(random.uniform(-180.0, 180.0), 6)
#     gps = "Latitude=" + str(lat) + ", Longitude=" + str(lng)
#     return gps

# # 메시지 전송 함수
# def send_message_with_crc_json(sio, message_data):
#     msg = json.dumps(message_data, separators=(',', ':'))
#     crc = zlib.crc32(msg.encode()) & 0xffffffff
#     crc_msg_json = json.dumps({"crc": format(crc, 'x'), "type": "location_info", "data": msg}, separators=(',', ':'))
#     sio.emit("location_info", crc_msg_json)

# # Socket.IO 클라이언트 설정 및 메인 로직
# if __name__ == "__main__":
#     sio = socketio.Client(logger=True, engineio_logger=True)
    
#     @sio.event
#     def connect():
#         print("Connected to the server")
#     @sio.event
#     def disconnect():
#         print("Disconnected from the server")

#     sio.connect('http://192.168.28.134:8010')
    
#     try:
#         while True:
#             gps_data = generate_random_gps()  # 랜덤 GPS 데이터 생성
#             gyro_x = random.randint(-1000, 1000)  # 임의의 자이로스코프 데이터 생성
#             gyro_y = random.randint(-1000, 1000)
#             gyro_z = random.randint(-1000, 1000)
#             Gx = round(gyro_x/131.0, 1)
#             Gy = round(gyro_y/131.0, 1)
#             Gz = round(gyro_z/131.0, 1)
#             message_data = {"data": f"{gps_data}, Gyro X={Gx}, Gyro Y={Gy}, Gyro Z={Gz}"}
#             send_message_with_crc_json(sio, message_data)
#             print(gps_data, "Gx=%.2f" % Gx, u'\u00b0' + "/s", "\tGy=%.2f" % Gy, u'\u00b0' + "/s", "\tGz=%.2f" % Gz, u'\u00b0')
#             time.sleep(1)  # 1초 대기
        
#     except KeyboardInterrupt:
#         print("프로그램을 종료합니다.")
#         sio.disconnect()
