# Robot Project — Raspberry Pi 4B

실험실 환경 실내 자율주행 로봇 프로젝트.  
현재는 원격 조종 단계이며, ROS2 + SLAM 기반 자율주행으로 마이그레이션 예정.

---

## 하드웨어

| 항목 | 사양 |
|------|------|
| 메인보드 | Raspberry Pi 4 Model B Rev 1.5 |
| CPU | ARM Cortex-A72 4코어 1.8GHz (aarch64) |
| RAM | 8GB |
| 저장소 | 64GB SD카드 |
| OS | Raspbian GNU/Linux 11 (Bullseye) → Ubuntu 22.04로 마이그레이션 예정 |

### 연결 센서 / 장치

| 장치 | 연결 방식 | 비고 |
|------|-----------|------|
| MCU (Arduino 등) | UART `/dev/ttyS0` 115200bps | 모터 드라이버 제어 |
| GPS 모듈 | UART `/dev/serial0` 38400bps | NMEA `$GNGLL` |
| MPU6050 (IMU) | I2C `0x68` | 자이로 + 가속도계 |
| TOF 거리센서 | I2C `0x52` | 전방 거리 측정 |
| USB 카메라 | `/dev/video0` | RTSP 스트리밍 |
| LiDAR | — | 추후 SLAM용 연결 예정 |

---

## 아키텍처

### 현재 (원격 조종)

```
[Mac 브라우저] ──WiFi──→ [robot_server.py :8010] ──시리얼──→ [MCU] ──→ 모터
                              ↑
                         웹 UI (templates/index.html)
                         온스크린 조이스틱 + 키보드
```

### 서버 기반 원격 조종 (기존 설계)

```
[웹/앱] ──→ [Socket.IO 서버 :8010] ──→ [PI_io_receive_test1.py] ──시리얼──→ [MCU] ──→ 모터
                                              ↑
                                   robot_gps_socketio.py (GPS/IMU 역송신)
                                   streaming.py (RTSP 영상)
```

### 목표 (자율주행)

```
[월드모델 컴퓨터]
  → /danger_zones (ROS2 토픽)
                    ──→ [Pi: ROS2 Humble + slam_toolbox]
                              A* 경로계획 (위험구역 반영)
                              Pure Pursuit 추종
                              시리얼 브릿지
                                   ──→ [MCU] ──→ 모터
```

---

## 파일 구조

```
robot_project/
├── README.md
├── robot_server.py          # Pi 웹서버 (Socket.IO) — 원격 조종용
├── gamepad_controller.py    # 로컬 게임패드 직접 조종 (서버 없이)
├── PI_io_receive_test1.py   # 외부 서버 기반 조종 클라이언트 (기존 설계)
├── robot_gps_socketio.py    # GPS + IMU 데이터 → 서버 송신
├── shock_module_socketio_test.py  # GPS + IMU 통합 테스트
├── distance_io.py           # TOF 거리센서 처리
├── streaming.py             # RTSP 카메라 스트리밍 (GStreamer)
├── mac_controller.py        # Mac용 게임패드 → Socket.IO 클라이언트
├── vpn_connect.sh           # OpenVPN 연결 (key005)
└── templates/
    └── index.html           # 웹 조종 UI (온스크린 조이스틱 + 키보드)
```

---

## 실행 방법

### 웹 기반 원격 조종 (현재 메인)

```bash
# Pi에서
sg tty -c "python3 robot_server.py"

# Mac 브라우저에서
# http://192.168.0.64:8010
```

### 로컬 게임패드 조종

```bash
sg tty -c "python3 gamepad_controller.py"
```

### RTSP 카메라 스트리밍

```bash
python3 streaming.py
# 접속: rtsp://192.168.0.64:8554/test
```

### VPN 연결

```bash
sudo ./vpn_connect.sh
```

---

## MCU 시리얼 프로토콜

CSV 형식, 개행 종료: `mode,A,B,FB,LR,FLB\n`

| mode | 의미 |
|------|------|
| `0` | 리셋 / 정지 |
| `1` | 수동 원격 조종 |
| `3` | 라인트레이싱 ON |
| `4` | 라인트레이싱 OFF / 비상정지 |
| `5` | 자율주행 신호 (×400 배율) |

- `FB`: 전진/후진 (−1.0 ~ 1.0) × 100 → 정수
- `LR`: 좌/우 (−1.0 ~ 1.0) × 100 → 정수
- `FLB`: 회전 (−1.0 ~ 1.0) × 100 → 정수

---

## 네트워크

| 항목 | 값 |
|------|-----|
| Pi WiFi IP | `192.168.0.64` |
| VPN 서버 | `119.195.220.90:42334` (OpenVPN UDP) |
| VPN 내부 서버 | `10.8.0.10:8010` |

---

## 의존성

```bash
pip3 install flask-socketio eventlet python-socketio pygame pyserial
```

---

## 마이그레이션 계획 (Ubuntu 22.04 + ROS2)

1. Ubuntu 22.04 Server (arm64) SD카드 재설치
2. ROS2 Humble 설치
3. slam_toolbox — 실험실 지도 생성 및 위치추정
4. 커스텀 A* 경로계획 노드 — `/danger_zones` 토픽 구독
5. Pure Pursuit 경로 추종 노드
6. 시리얼 브릿지 노드 (`/cmd_vel` → 기존 MCU 프로토콜)
