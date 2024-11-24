import streamlit as st
import time
import random
import platform
import subprocess
import tempfile
import os
import sys
import psutil
from pynput.keyboard import Key, Controller
import requests
from io import BytesIO
from PIL import Image
import pyperclip

keyboard = Controller()

def get_system_info():
    return f"OS: {platform.system()} {platform.release()}, Python: {platform.python_version()}"

def create_typing_script(text, images, delay_min, delay_max):
    escaped_text = text.replace('"', '\\"').replace('\n', '\\n')
    image_list = ', '.join([f'"{img}"' for img in images])
    script = f"""
import time
import random
from pynput.keyboard import Key, Controller
import os
import platform
import requests
from io import BytesIO
from PIL import Image
import subprocess
import tempfile

keyboard = Controller()

def switch_language():
    keyboard.press(Key.caps_lock)
    time.sleep(0.1)
    keyboard.release(Key.caps_lock)
    time.sleep(0.1)

def type_text(text, delay_min, delay_max):
    korean_mode = False
    for char in text:
        if os.path.exists("pause_signal"):
            while os.path.exists("pause_signal"):
                time.sleep(0.1)
        if os.path.exists("stop_signal"):
            return
        
        if '가' <= char <= '힣' and not korean_mode:
            switch_language()
            korean_mode = True
        elif not ('가' <= char <= '힣') and korean_mode:
            switch_language()
            korean_mode = False
        
        keyboard.type(char)
        time.sleep(random.uniform(delay_min, delay_max))

    if korean_mode:
        switch_language()

def paste_image(image_url):
    try:
        # 이미지 다운로드
        response = requests.get(image_url)
        img = Image.open(BytesIO(response.content))
        
        # 이미지를 임시 파일로 저장
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
            img.save(temp_file, "PNG")
            temp_file_path = temp_file.name
        
        # 이미지를 클립보드에 복사
        subprocess.run(["osascript", "-e", f'set the clipboard to (read (POSIX file "{{temp_file_path}}") as JPEG picture)'])
        
        # 네이버 블로그 에디터에 붙여넣기
        keyboard.press(Key.cmd)
        keyboard.press('v')
        keyboard.release('v')
        keyboard.release(Key.cmd)
        
        time.sleep(2)  # 이미지 업로드 대기
        print(f"이미지 붙여넣기 완료: {{image_url}}")
        
        # 임시 파일 삭제
        os.unlink(temp_file_path)
    except Exception as e:
        print(f"이미지 붙여넣기 실패: {{str(e)}}")

type_text("{escaped_text}", {delay_min}, {delay_max})

images = [{image_list}]
for image in images:
    paste_image(image)
    time.sleep(2)

os.remove("stop_signal") if os.path.exists("stop_signal") else None
os.remove("pause_signal") if os.path.exists("pause_signal") else None
"""
    return script

def cleanup_files():
    for file in ["pause_signal", "stop_signal"]:
        if os.path.exists(file):
            os.remove(file)

def terminate_process(process):
    if process:
        try:
            parent = psutil.Process(process.pid)
            for child in parent.children(recursive=True):
                child.terminate()
            parent.terminate()
        except psutil.NoSuchProcess:
            pass

# 초기 정리
cleanup_files()
if 'process' in st.session_state and st.session_state.process:
    terminate_process(st.session_state.process)
    st.session_state.process = None

def start_posting(content, images, delay_min, delay_max):
    cleanup_files()
    script = create_typing_script(content, images, delay_min, delay_max)
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py', encoding='utf-8') as tmp:
        tmp.write(script)
        tmp_filename = tmp.name

    st.write("5초 후에 포스팅을 시작합니다. 네이버 블로그 글쓰기 페이지를 열어주세요.")
    for i in range(5, 0, -1):
        st.write(f"{i}초 남았습니다...")
        time.sleep(1)
    
    st.write("포스팅을 시작합니다...")
    
    python_executable = sys.executable
    process = subprocess.Popen([python_executable, tmp_filename])
    
    return process

def pause_posting():
    open("pause_signal", 'w').close()
    st.write("포스팅을 일시정지합니다.")

def resume_posting():
    if os.path.exists("pause_signal"):
        os.remove("pause_signal")
    st.write("포스팅을 재개합니다.")

def stop_posting(process):
    open("stop_signal", 'w').close()
    terminate_process(process)
    cleanup_files()
    st.write("포스팅을 정지했습니다.")