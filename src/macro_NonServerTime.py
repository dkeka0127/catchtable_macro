## 사용 방법

# 캐치테이블 화면(서브모니터) 비율 100% 설정
# 예약 날짜(reserve_date =) 좌표값 설정
# 예약 시간(pyautogui.click(reserve_time) 설정

# root = tk.Tk() 주석 처리
# 캘린더 보이게 & 아무 날짜 눌러서 세팅

# 가상환경 활성화: python3 -m venv venv, source venv/bin/activate
# 실행 : python src/main.py

# test url: https://app.catchtable.co.kr/ct/shop/sakawoo?date=241220

## 로직 (* ex) 예약하고 싶은 날짜를 '20일'이라고 가정함)

# 1. '19일', '20일' 모니터 좌표 추출

# 2-1. '19일' 클릭 (* 19일 클릭 후 20일 클릭해야 화면 리로딩 됨)
# 2-2. '20일' 클릭

# 3. '예약시간(ex-19:30)' 클릭

# 4. 화면에 "오후" or "예약금" 단어 있는지 텍스트 추출
# 4-1. 텍스트 추출 O (예약 가능) > 5번으로
# 4-2. 텍스트 추출 X (예약 불가능) > 2-1번부터 반복

# 5. '예약버튼(확인)' 클릭

# 6. 결제 창 진입 및 성공 !  

import tkinter as tk
import pyautogui
import time
import webbrowser
from PIL import ImageGrab
import cv2
import numpy as np
import pytesseract
from screeninfo import get_monitors

def check_text_on_screen():
    monitors = get_monitors()
    
    # 두 번째 모니터(서브 모니터) 찾기
    if len(monitors) > 1:
        second_monitor = monitors[1]
        monitor_region = (
            second_monitor.x,      # 시작 x 좌표
            second_monitor.y,      # 시작 y 좌표
            second_monitor.x + second_monitor.width,  # 끝 x 좌표
            second_monitor.y + second_monitor.height  # 끝 y 좌표
        )
        
        # 특정 모니터 영역만 캡처
        screenshot = ImageGrab.grab(bbox=monitor_region)
    else:
        print("서브 모니터를 찾을 수 없습니다!")
        return False
    
    screenshot_np = np.array(screenshot)
    gray = cv2.cvtColor(screenshot_np, cv2.COLOR_BGR2GRAY)
    
    pytesseract.pytesseract.tesseract_cmd = r'/opt/homebrew/bin/tesseract'
    detected_text = pytesseract.image_to_string(gray, lang='kor+eng')

    # print(detected_text) # 서브 모니터 텍스트 추출
    
    target_texts = ["예약금", "오후"]
    return any(text in detected_text for text in target_texts)

def macro_NonServerTime():
    # 좌표값
    reserve_start = (1010 + 2240, 985 + 50) # [예약하기] 버튼
    
    reserve_date = (1079 + 2240, 632 + 50) # 예약을 원하는 날짜
    reserve_date_left = (reserve_date[0] - 60, reserve_date[1]) # 왼쪽 날짜
    reserve_date_right = (reserve_date[0] + 60, reserve_date[1]) # 오른쪽 날짜
    reserve_date_side = reserve_date_right if reserve_date[0] <= -(780 + 2240) else reserve_date_left # 사이드 날짜
    
    reserve_time1 = (780 + 2240, 920 + 50) # 예약 시간 1
    reserve_time2 = (870 + 2240, 920 + 50) # 예약 시간 2
    reserve_time3 = (960 + 2240, 920 + 50) # 예약 시간 3
    reserve_time4 = (1050 + 2240, 920 + 50) # 예약 시간 4
    
    reserve_confirm = (1070 + 2240, 980 + 50) # [예약 확인] 버튼

    # 1. 예약 하고싶은 날짜의 좌표 받기
    # root = tk.Tk()
    # root.title("Click Tracker")
    # root.state('zoomed')
    # root.mainloop()

    max_attempts = 4
    attempt = 0
    
    # 2. [캘린더 켜놓고 아무 날짜 클릭한 상태]부터 시작
    pyautogui.click(reserve_date)
    pyautogui.click(reserve_date)
    time.sleep(0.1)
    pyautogui.click(reserve_time1)
    time.sleep(0.1)
    
    while attempt < max_attempts:
        if check_text_on_screen():
            pyautogui.click(reserve_confirm)
            break
        else:
            pyautogui.click(reserve_date_side)
            pyautogui.click(reserve_date)
            time.sleep(0.1)
            pyautogui.click(reserve_time1)
            time.sleep(0.1)
            attempt += 1

if __name__ == "__macro_NonServerTime__":
    macro_NonServerTime()
