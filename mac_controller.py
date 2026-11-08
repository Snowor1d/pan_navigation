"""
Mac에서 실행하는 조종 스크립트
필요한 패키지 설치:
  pip3 install pygame python-socketio[client] eventlet
"""

import pygame
import socketio
import json
import time
import sys

PI_IP = '192.168.0.64'
PI_PORT = 8010
DEADZONE = 0.05
SEND_INTERVAL = 0.05  # 50ms

BTN_A     = 0  # 트리거
BTN_B     = 1  # 엄지 버튼
BTN_ESTOP = 2  # 비상정지

def apply_deadzone(val, dz=DEADZONE):
    if abs(val) < dz:
        return 0.0
    return val

def main():
    pygame.init()
    pygame.joystick.init()

    if pygame.joystick.get_count() == 0:
        print("[오류] 게임패드가 감지되지 않습니다. 연결 후 다시 실행하세요.")
        sys.exit(1)

    js = pygame.joystick.Joystick(0)
    js.init()
    print(f"[OK] 조이스틱: {js.get_name()}")

    sio = socketio.Client()

    @sio.event
    def connect():
        print(f"[OK] Pi 서버 연결됨: {PI_IP}:{PI_PORT}")

    @sio.event
    def disconnect():
        print("[끊김] Pi 서버 연결 종료")

    print(f"[연결 중] {PI_IP}:{PI_PORT} ...")
    try:
        sio.connect(f'http://{PI_IP}:{PI_PORT}')
    except Exception as e:
        print(f"[오류] 연결 실패: {e}")
        print("  → Pi 서버가 실행 중인지 확인하세요: python3 robot_server.py")
        sys.exit(1)

    print()
    print("=== 조종 방법 ===")
    print("  스틱 앞/뒤  : 전진 / 후진")
    print("  스틱 좌/우  : 좌/우 회전")
    print("  트리거(0번) : A 버튼")
    print("  엄지(1번)   : B 버튼")
    print("  버튼2       : 비상정지")
    print("  Ctrl+C      : 종료")
    print("=" * 30)

    last_send = 0

    try:
        while True:
            pygame.event.pump()

            LR  =  apply_deadzone(js.get_axis(0))
            FB  = -apply_deadzone(js.get_axis(1))
            FLB =  apply_deadzone(js.get_axis(2))
            A   = int(js.get_button(BTN_A))
            B   = int(js.get_button(BTN_B))

            if js.get_button(BTN_ESTOP):
                print("\n[비상정지!]")
                sio.emit('emergency_stop', {})
                time.sleep(0.1)
                continue

            now = time.time()
            if now - last_send >= SEND_INTERVAL:
                payload = json.dumps({
                    'data': {'A': A, 'B': B, 'FB': FB, 'LR': LR, 'FLB': FLB}
                })
                sio.emit('remote_signal', payload)
                print(f"  → A:{A} B:{B} FB:{FB:+.2f} LR:{LR:+.2f}", end='\r')
                last_send = now

            time.sleep(0.01)

    except KeyboardInterrupt:
        print("\n\n[종료 중...]")
        sio.emit('emergency_stop', {})
        time.sleep(0.2)
        sio.disconnect()
        pygame.quit()
        print("[종료 완료]")

if __name__ == '__main__':
    main()
