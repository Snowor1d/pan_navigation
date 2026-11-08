import socketio
import eventlet
import eventlet.wsgi
import serial
import json
import os
import time

SERIAL_PORT   = '/dev/ttyS0'
BAUD_RATE     = 115200
SERVER_PORT   = 8010
WATCHDOG_SEC  = 0.5  # 이 시간 동안 신호 없으면 정지
TEMPLATE      = os.path.join(os.path.dirname(__file__), 'templates', 'index.html')

# 시리얼 포트
try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    print(f"[OK] 시리얼 연결: {SERIAL_PORT}")
except Exception as e:
    ser = None
    print(f"[경고] 시리얼 연결 실패: {e}")

def send_serial(mode, A, B, FB, LR, FLB):
    cmd = f"{mode},{A},{B},{int(FB*100)},{int(LR*100)},{int(FLB*100)}\n"
    if ser:
        ser.write(cmd.encode())
    print(f"  → {cmd.strip()}", end='\r')

# 워치독: 마지막 신호 시간 추적
last_signal_time = 0

def watchdog():
    global last_signal_time
    while True:
        eventlet.sleep(0.1)
        if last_signal_time > 0 and (time.time() - last_signal_time) > WATCHDOG_SEC:
            send_serial(0, 0, 0, 0, 0, 0)
            last_signal_time = 0

# Socket.IO 서버 (WebSocket 허용)
sio = socketio.Server(
    cors_allowed_origins='*',
    async_mode='eventlet',
    transports=['websocket', 'polling'],
)

@sio.event
def connect(sid, environ):
    print(f"\n[접속] {sid}")

@sio.event
def disconnect(sid):
    print(f"\n[끊김] {sid}")
    # 즉시 정지 대신 워치독이 처리

@sio.on('remote_signal')
def handle_remote_signal(sid, data):
    global last_signal_time
    try:
        d = data if isinstance(data, dict) else json.loads(data)
        d = d.get('data', d)
        A   = int(d.get('A', 0))
        B   = int(d.get('B', 0))
        FB  = round(float(d.get('FB', 0)), 3)
        LR  = round(float(d.get('LR', 0)), 3)
        FLB = round(float(d.get('FLB', 0)), 3)
        send_serial(1, A, B, FB, LR, FLB)
        last_signal_time = time.time()
    except Exception as e:
        print(f"\n[오류] {e}")

@sio.on('emergency_stop')
def handle_emergency_stop(sid, data):
    global last_signal_time
    print("\n[비상정지!]")
    last_signal_time = 0
    send_serial(4, 0, 0, 0, 0, 0)

# HTTP 핸들러
def simple_app(environ, start_response):
    path = environ.get('PATH_INFO', '/')
    if path == '/':
        with open(TEMPLATE, 'rb') as f:
            body = f.read()
        start_response('200 OK', [
            ('Content-Type', 'text/html; charset=utf-8'),
            ('Content-Length', str(len(body))),
        ])
        return [body]
    start_response('404 Not Found', [('Content-Type', 'text/plain')])
    return [b'Not Found']

app = socketio.WSGIApp(sio, simple_app)

if __name__ == '__main__':
    print(f"[Pi 로봇 서버 시작]")
    print(f"  Mac 브라우저: http://192.168.0.64:{SERVER_PORT}")
    print(f"  종료: Ctrl+C")
    eventlet.spawn(watchdog)
    eventlet.wsgi.server(eventlet.listen(('0.0.0.0', SERVER_PORT)), app)
