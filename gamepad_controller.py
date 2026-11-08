import pygame
import serial
import time
import sys

# 설정
SERIAL_PORT = '/dev/ttyS0'
BAUD_RATE = 115200
DEADZONE = 0.05       # 스틱 데드존 (드리프트 방지)
SEND_INTERVAL = 0.05  # 명령 전송 주기 (50ms = 20Hz)

# 버튼 매핑 (Logitech Extreme 3D)
BTN_A         = 0   # 트리거
BTN_B         = 1   # 엄지 버튼
BTN_ESTOP     = 2   # 비상정지

def apply_deadzone(val, dz=DEADZONE):
    if abs(val) < dz:
        return 0.0
    return val

def open_serial():
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print(f"[OK] 시리얼 연결: {SERIAL_PORT}")
        return ser
    except Exception as e:
        print(f"[경고] 시리얼 연결 실패 ({e}) - 드라이 런 모드로 실행")
        return None

def send_command(ser, mode, A, B, FB, LR, FLB):
    cmd = f"{mode},{A},{B},{int(FB*100)},{int(LR*100)},{int(FLB*100)}\n"
    if ser:
        ser.write(cmd.encode())
    print(f"  → 전송: {cmd.strip()}", end='\r')

def main():
    pygame.init()
    pygame.joystick.init()

    if pygame.joystick.get_count() == 0:
        print("[오류] 게임패드가 감지되지 않습니다.")
        sys.exit(1)

    js = pygame.joystick.Joystick(0)
    js.init()
    print(f"[OK] 조이스틱: {js.get_name()}")
    print()
    print("=== 조종 방법 ===")
    print("  스틱 앞/뒤  : 전진 / 후진")
    print("  스틱 좌/우  : 좌회전 / 우회전")
    print("  트리거(0번) : A 버튼")
    print("  엄지(1번)   : B 버튼")
    print("  버튼2       : 비상정지")
    print("  Ctrl+C      : 종료")
    print("=" * 30)
    print()

    ser = open_serial()
    last_send = 0

    try:
        while True:
            pygame.event.pump()

            # 축 읽기
            LR  =  apply_deadzone(js.get_axis(0))        # 좌우
            FB  = -apply_deadzone(js.get_axis(1))        # 전후 (반전: 앞으로 밀면 양수)
            FLB =  apply_deadzone(js.get_axis(2))        # 스틱 회전

            # 버튼 읽기
            A = int(js.get_button(BTN_A))
            B = int(js.get_button(BTN_B))

            # 비상정지
            if js.get_button(BTN_ESTOP):
                print("\n[비상정지!]")
                send_command(ser, 4, 0, 0, 0, 0, 0)
                time.sleep(0.1)
                continue

            # 주기적 전송
            now = time.time()
            if now - last_send >= SEND_INTERVAL:
                send_command(ser, 1, A, B, FB, LR, FLB)
                last_send = now

            time.sleep(0.01)

    except KeyboardInterrupt:
        print("\n\n[종료] 정지 명령 전송 중...")
        send_command(ser, 0, 0, 0, 0, 0, 0)
        if ser:
            ser.close()
        pygame.quit()
        print("[종료 완료]")

if __name__ == "__main__":
    main()
