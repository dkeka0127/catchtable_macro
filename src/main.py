# 1. 서브모니터 - 캐치테이블 화면 비율 100%
# 2. 전역 변수 설정
# 3. 캘린더 오픈 & 아무 날짜 클릭해둔 상태
# 4. 파이썬 가상환경 활성화: python3 -m venv venv && source venv/bin/activate
# 5. 실행 : python src/main.py

# test url: https://app.catchtable.co.kr/ct/shop/sakawoo?date=241220

import tkinter as tk
import pyautogui
import time
import webbrowser
from PIL import ImageGrab
import cv2
import numpy as np
import pytesseract
from screeninfo import get_monitors
import requests
from datetime import datetime, timezone, timedelta

# 전역 변수 설정
RESERVE_DATE = (1079, 632) # 예약 날짜 좌표 (형식: x, y)
TARGET_TIME = "15:00"  # 예약 시간 (형식: "HH:MM")
URL = "https://app.catchtable.co.kr"  # 서버 시간 확인용 URL
RESERVE_TIME_SLOT = 1  # 예약 시간대 선택 (1, 2, 3, 4 중 선택)

# 고정 좌표 변수 선언
SUB_MONITOR_X = 2240
SUB_MONITOR_Y = 50

reserve_start = (1010 + SUB_MONITOR_X, 985 + SUB_MONITOR_Y) # [예약하기] 버튼
reserve_date = (RESERVE_DATE[0] + SUB_MONITOR_X, RESERVE_DATE[1] + SUB_MONITOR_Y)  # 예약 날짜
reserve_date_left = (reserve_date[0] - 60, reserve_date[1]) # 왼쪽 날짜
reserve_date_right = (reserve_date[0] + 60, reserve_date[1]) # 오른쪽 날짜
reserve_date_side = reserve_date_right if reserve_date[0] <= -(780 + SUB_MONITOR_X) else reserve_date_left # 사이드 날짜 택 1
reserve_time1 = (780 + SUB_MONITOR_X, 920 + SUB_MONITOR_Y) # 예약 타임 1            
reserve_time2 = (870 + SUB_MONITOR_X, 920 + SUB_MONITOR_Y) # 예약 타임 2
reserve_time3 = (960 + SUB_MONITOR_X, 920 + SUB_MONITOR_Y) # 예약 타임 3
reserve_time4 = (1050 + SUB_MONITOR_X, 920 + SUB_MONITOR_Y) # 예약 타임 4
reserve_confirm = (1070 + SUB_MONITOR_X, 980 + SUB_MONITOR_Y) # 예약금 안내 확인 좌표값
    
# RESERVE_TIME_SLOT에 따른 예약 시간 좌표 선택
reserve_selected_time = {
    1: reserve_time1,
    2: reserve_time2,
    3: reserve_time3,
    4: reserve_time4
}.get(RESERVE_TIME_SLOT, reserve_time1)  # 기본값은 reserve_time1

# 서버 시간 확인 함수
def get_server_time(url):
    KST = timezone(timedelta(hours=9))
    TIME_FORMAT = '%a, %d %b %Y %H:%M:%S %Z'
    
    try:
        response = requests.head(url)
        server_time = response.headers.get('date')
        
        if not server_time:
            return None
            
        # GMT -> KST 변환
        server_datetime = datetime.strptime(server_time, TIME_FORMAT)
        korea_time = (server_datetime
                     .replace(tzinfo=timezone.utc)
                     .astimezone(KST)
                     .replace(microsecond=datetime.now().microsecond))
        
        return korea_time
        
    except requests.RequestException as e:
        print(f"서버 연결 오류: {e}")
        return None
    except ValueError as e:
        print(f"시간 형식 변환 오류: {e}")
        return None

# 화면 텍스트 추출 함수
def check_text_on_screen():
    # 모니터 설정 관련
    monitors = get_monitors()
    if len(monitors) <= 1:
        print("서브 모니터를 찾을 수 없습니다!")
        return False
    
    # 두 번째 모니터 영역 설정
    second_monitor = monitors[1]
    monitor_region = (
        second_monitor.x,
        second_monitor.y,
        second_monitor.x + second_monitor.width,
        second_monitor.y + second_monitor.height
    )
    
    # 스크린샷 캡처 및 전처리
    screenshot = ImageGrab.grab(bbox=monitor_region)
    screenshot_np = np.array(screenshot)
    gray = cv2.cvtColor(screenshot_np, cv2.COLOR_BGR2GRAY)
    
    # OCR 설정 및 텍스트 감지
    pytesseract.pytesseract.tesseract_cmd = r'/opt/homebrew/bin/tesseract'
    detected_text = pytesseract.image_to_string(gray, lang='kor+eng')
    
    # 목표 텍스트 확인
    target_texts = ["예약금", "오후"]
    return any(text in detected_text for text in target_texts)

def main():
    # 예약 날짜 좌표 추출
    root = tk.Tk()
    root.state('zoomed')
    root.bind('<Button-1>', lambda event: print(f"({event.x}, {event.y})"))
    root.mainloop()

    # 목표 시간 설정
    def setup_target_time():
        kst = timezone(timedelta(hours=9))
        now = datetime.now(kst)
        target_hour, target_minute = map(int, TARGET_TIME.split(':'))
        return datetime(now.year, now.month, now.day, target_hour, target_minute, 0, tzinfo=kst)

    # 서버 시간이 목표 시간이 될 때까지 대기
    def wait_until_target_time(target_time):
        print(f"목표 시간: {target_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("서버 시간 체크 중...")
        
        while True:
            server_time = get_server_time(URL)
            if server_time:
                print(f"\r서버 시간: {server_time.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}", end='')
                if server_time >= target_time:
                    print("\n목표 시간에 도달했습니다. 예약을 시작합니다.")
                    break
            time.sleep(0.1)

    # 예약 시도 실행
    def attempt_reservation():
        max_attempts = 4
        attempt = 0
        
        # 초기 예약 시도
        execute_reservation_click()
        
        # 예약 확인 및 재시도
        while attempt < max_attempts:
            if check_text_on_screen():
                pyautogui.click(reserve_confirm)
                break
            else:
                execute_alternative_reservation_click()
                attempt += 1

    # 예약 클릭 실행
    def execute_reservation_click():
        pyautogui.click(reserve_date)
        pyautogui.click(reserve_date)
        time.sleep(0.1)
        pyautogui.click(reserve_selected_time)
        time.sleep(0.1)

    # 대체 예약 클릭 실행
    def execute_alternative_reservation_click():
        pyautogui.click(reserve_date_side)
        pyautogui.click(reserve_date)
        time.sleep(0.1)
        pyautogui.click(reserve_selected_time)
        time.sleep(0.1)

    # 메인 실행 로직
    target_time = setup_target_time()
    wait_until_target_time(target_time)
    attempt_reservation()

if __name__ == "__main__":
    main()
