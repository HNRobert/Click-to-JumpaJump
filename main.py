import math
import os
import re
import socket
import struct
import time
from multiprocessing import Event, Process, Queue, Manager, Value

import cv2
import numpy as np
import RPi.GPIO as GPIO
from picamera2 import Picamera2


def newest_cascade_file(directory):
    pattern = re.compile(r"cascade(\d+)\.xml")
    largest_number = -1
    largest_file = None
    for filename in os.listdir(directory):
        if (match := pattern.match(filename)) and (number := int(match.group(1))) and number > largest_number:
            largest_number = number
            largest_file = filename
    if largest_file:
        return os.path.join(directory, largest_file)
    else:
        return None


def get_average_position(sample_list, min_sample=10, calc_sample_count=5):
    sample_count = len(sample_list)
    if sample_count < min_sample:
        return None
    if not calc_sample_count:
        calc_sample_count = sample_count

    avg_x = sum([p[0] for p in sample_list[-calc_sample_count:]]
                ) / calc_sample_count
    avg_y = sum([p[1] for p in sample_list[-calc_sample_count:]]
                ) / calc_sample_count
    return (avg_x, avg_y)


def get_average_distance(sample_list, min_sample=1, calc_sample_count=0):
    sample_count = len(sample_list)
    if sample_count < min_sample:
        return None
    if not calc_sample_count:
        calc_sample_count = sample_count

    return sum(sample_list[-calc_sample_count:]) / calc_sample_count


def current_i_position(i_pst):
    while not i_pst:
        time.sleep(0.1)
    return list(i_pst)


def calculate_distance(pos1, pos2):  # 勾股
    return math.sqrt((pos2[0] - pos1[0])**2 + (pos2[1] - pos1[1])**2)


def camera_process(init_done_event, stop_event, i_position):
    picam2 = Picamera2()
    max_resolution_mode = {
        "size": (1296, 972),
        "format": "RGB888"
    }
    video_config = picam2.create_video_configuration(main=max_resolution_mode)
    picam2.configure(video_config)
    picam2.start()

    face_cascade = cv2.CascadeClassifier(newest_cascade_file("./cascade"))

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = ('192.168.2.1', 5000)
    CHUNK_SIZE = 1024

    init_done_event.set()

    position_list = []  # 用于存储小人位置的队列

    while not stop_event.is_set():
        frame = picam2.capture_array()
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

        i_st = face_cascade.detectMultiScale(
            gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        if len(i_st) > 0:
            (x, y, w, h) = min(i_st, key=lambda rect: rect[2] * rect[3])
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

            # 计算竖直中轴线和最大正方形的中心点
            center_x = x + w // 2  # 框的水平中点
            square_side = w  # 正方形的边长等于框的宽度
            center_y = y + h - square_side // 2  # 正方形的中心点纵坐标

            # 绘制小人站立位置的点
            cv2.circle(frame, (center_x, center_y), radius=5,
                       color=(0, 255, 0), thickness=-1)

            # 将小人当前位置添加到列表
            position_list.append((center_x, center_y))

            # 计算位置的平均值并传入队列
            if average_position := get_average_position(position_list):
                i_position[:] = average_position

        else:
            # 当没有检测到小人时，清空位置列表
            if position_list:
                position_list.clear()
            if i_position:
                i_position[:] = []

        result, encoded_image = cv2.imencode(
            '.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 90])

        total_chunks = (len(encoded_image) // CHUNK_SIZE) + \
            (1 if len(encoded_image) % CHUNK_SIZE > 0 else 0)

        for i in range(total_chunks):
            start = i * CHUNK_SIZE
            end = min((i + 1) * CHUNK_SIZE, len(encoded_image))
            chunk_data = encoded_image[start:end]

            header = struct.pack("Q", i) + struct.pack("Q", total_chunks)
            sock.sendto(header + chunk_data.tobytes(), server_address)

    print("[Camera Process Completed]")


def calculate_time(_t2, _d2, _d3):
    _k = 25*_d2/6/_t2/(_t2/500+1)
    _t3 = (math.sqrt(0.0576*_k**2 + 0.00192*_d3*_k) - 6*_k/25)/_k*3125/3
    return _t3


def gpio_process(ready_event, click_to_jump_active_event, stop_event, i_position, _t2, _d2, cmd_queue: Queue):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(21, GPIO.OUT)
    GPIO.setup(20, GPIO.OUT)
    GPIO.setup(19, GPIO.OUT)
    GPIO.setup(13, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    GPIO.output(19, GPIO.LOW)
    GPIO.output(20, GPIO.HIGH)

    def is_num(s_value):
        try:
            float(s_value)
            return True
        except:
            return False

    def num_to_float(s_value):
        if is_num(s_value=s_value):
            return float(s_value)
        elif s_value == "":
            return 0.1
        else:
            return 0

    def press_for(time_sec):
        nonlocal state21
        time_left = num_to_float(time_sec)
        state21 = True
        GPIO.output(21, GPIO.HIGH)
        print("Pressing ", end="")
        while time_left >= 0.1:
            time.sleep(0.1)
            time_left -= 0.1
            print("-", end="")
        time.sleep(time_left)
        state21 = False
        GPIO.output(21, GPIO.LOW)
        print(" Released")

    prev_ds = []
    state21 = False
    GPIO.output(21, GPIO.LOW)

    while not stop_event.is_set():
        if cmd_queue.empty():
            time.sleep(0.1)
            continue
        cmd = cmd_queue.get()

        # 分割命令和参数
        cmd_parts = cmd.split()
        base_cmd = cmd_parts[0] if len(cmd_parts) > 0 else None
        arg = cmd_parts[1] if len(cmd_parts) > 1 else None

        if base_cmd == "q":
            print(
                f"Click-To-Jump mode {'already ' if not click_to_jump_active_event.is_set() else ''}quitted\n")
            click_to_jump_active_event.clear()

        elif base_cmd == "l":
            state21 = False
            GPIO.output(21, GPIO.LOW)

        elif base_cmd == "h":
            state21 = True
            GPIO.output(21, GPIO.HIGH)

        elif base_cmd == "s":
            state21 = not state21
            GPIO.output(21, GPIO.HIGH if state21 else GPIO.LOW)

        elif base_cmd == "p":
            print(
                f"Click-To-Jump mode {'already ' if click_to_jump_active_event.is_set() else ''}activated\n")
            click_to_jump_active_event.set()
        elif base_cmd == "sd":
            if arg and is_num(arg):
                _d2.value = float(arg)
            else:
                print("Invalid or missing time for 'sd' command")
        elif base_cmd == "td":
            # 处理"t"命令：按下0.1秒并记录位置变化
            init_position = current_i_position(i_position)

            press_for(0.1)

            time.sleep(0.5)

            distance = calculate_distance(
                init_position, current_i_position(i_position))
            prev_ds.append(distance)
            _d2.value = get_average_distance(prev_ds, 1, 0)

            print(f"按下前后位置移动距离: {distance:.2f} 像素 /navg: {_d2.value}")

        elif base_cmd == "cld":
            prev_ds = []
            _d2.value = 0

        elif base_cmd == "st":
            # 检查 st 后面是否有数字，并转换成 float
            if arg and is_num(arg):
                _t2.value = float(arg)
                prev_ds = []
                _d2.value = 0
                print(f"Default testing time set: {arg}s")
            else:
                print("Invalid or missing time for 'st' command")

        elif is_num(cmd) or cmd == "":
            press_time = num_to_float(cmd)
            press_for(press_time)

        ready_event.set()

    GPIO.cleanup()
    print("[GPIO Process Completed]")


def udp_listener(ready_event, click_to_jump_active_event, stop_event, i_position, _t2, _d2, cmd_queue):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('0.0.0.0', 5001))  # 绑定到任意IP和端口5001接收数据
    sock.settimeout(1)  # 1秒超时

    while not stop_event.is_set():
        try:
            data, _ = sock.recvfrom(1024)
            x, y = struct.unpack('ii', data)
            if not _d2.value or not _t2.value:
                print("Please run \"t\" to do a scale test first")
                print_input_prompt()
                continue
            if click_to_jump_active_event.is_set():
                print(f"Received click at: ({x}, {y}")
                jump_screen_dst = calculate_distance(
                    current_i_position(i_position), [x, y])
                jump_time = calculate_time(
                    _t2.value, _d2.value, jump_screen_dst)
                print(
                    f"{_t2.value}s Press = {_d2.value}pix Jump; Jumping {jump_screen_dst} = Pressing for: {jump_time}")
                ready_event.clear()
                cmd_queue.put(str(jump_time))
                while not ready_event.is_set():
                    time.sleep(0.1)
                print_input_prompt()

        except socket.timeout:
            continue
        time.sleep(0.1)

    sock.close()
    print("[UDP Listener Completed]")

def print_input_prompt():
    if click_to_jump_active_event.is_set():
        print("JumpaJump @ClickToJump >> ", end="")
    else:
        print("JumpaJump >> ", end="")


if __name__ == "__main__":
    mtp_manager = Manager()
    i_position = mtp_manager.list()
    nxt_cmd_ready_event = Event()
    click_to_jump_active_event = Event()
    stop_event = Event()
    d2 = Value("d", 0)
    t2 = Value("d", 0.1)
    cmd_queue = Queue()

    camera_proc = Process(target=camera_process,
                          args=(nxt_cmd_ready_event, stop_event, i_position))
    gpio_proc = Process(target=gpio_process, args=(
        nxt_cmd_ready_event, click_to_jump_active_event, stop_event, i_position, t2, d2, cmd_queue))
    udp_proc = Process(target=udp_listener, args=(
        nxt_cmd_ready_event, click_to_jump_active_event, stop_event, i_position, t2, d2, cmd_queue))

    camera_proc.start()
    gpio_proc.start()
    udp_proc.start()

    while not stop_event.is_set():

        while not nxt_cmd_ready_event.is_set():
            time.sleep(0.1)

        print_input_prompt()
        cmd = input()
        nxt_cmd_ready_event.clear()
        cmd_queue.put(cmd)
        if cmd == "exit":
            stop_event.set()
            break

    camera_proc.join()
    gpio_proc.join()
    udp_proc.join()

    print("[All processes completed]")
