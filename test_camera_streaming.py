import os
import re
import socket
import struct

import cv2
import numpy as np
from picamera2 import Picamera2


def newest_cascade_file(directory):
    # 使用正则表达式匹配 "cascade" 后跟随数字的文件
    pattern = re.compile(r"cascade(\d+)\.xml")

    largest_number = -1
    largest_file = None

    # 遍历文件夹中的所有文件
    for filename in os.listdir(directory):
        match = pattern.match(filename)
        if match:
            # 提取数字并比较大小
            number = int(match.group(1))
            if number > largest_number:
                largest_number = number
                largest_file = filename

    print()
    if largest_file:
        return os.path.join(directory, largest_file)  # 返回相对路径
    else:
        return None  # 如果没有找到匹配的文件

# 初始化摄像头
picam2 = Picamera2()

# 获取最大分辨率的模式
max_resolution_mode = {
    "size": (1296, 972),  # 分辨率
    "format": "RGB888"  # 可选格式，默认使用 RGB
}
"""
Resolution: (640, 480) - FPS: 58.92
Resolution: (1296, 972) - FPS: 43.25
Resolution: (1920, 1080) - FPS: 30.62
Resolution: (2592, 1944) - FPS: 15.63
"""

# 配置摄像头为最大分辨率
video_config = picam2.create_video_configuration(main=max_resolution_mode)
picam2.configure(video_config)
picam2.start()

face_cascade = cv2.CascadeClassifier(newest_cascade_file("./cascade"))  # 替换为自训练的模型路径

# 创建UDP套接字
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('192.168.2.1', 5000)  # 替换为 MacBook 的 IP 地址

# 定义数据块大小
CHUNK_SIZE = 1024  # 发送的每个数据块大小

while True:
    # 捕获摄像头帧
    frame = picam2.capture_array()

    # 将图像转换为灰度图像以提高检测性能
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

    # 检测
    i_st = face_cascade.detectMultiScale(
        gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    # 在检测到的人脸上绘制矩形框
    for (x, y, w, h) in i_st:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)


    """
    # 圆形检测
    blurred_frame = cv2.GaussianBlur(gray_frame, (5, 5), 0)
    circles = cv2.HoughCircles(blurred_frame, cv2.HOUGH_GRADIENT, dp=1.2,
                               minDist=50, param1=50, param2=30, minRadius=10, maxRadius=100)

    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        for (x, y, r) in circles:
            cv2.circle(frame, (x, y), r, (0, 255, 0), 2)  # 绿色框表示圆形

    # 菱形检测
    contours, _ = cv2.findContours(
        blurred_frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        approx = cv2.approxPolyDP(
            contour, 0.04 * cv2.arcLength(contour, True), True)

        # 如果轮廓有四个顶点，判断是否是菱形
        if len(approx) == 4:
            cosines = []
            for i in range(4):
                p1, p2, p3 = approx[i][0], approx[(
                    i + 1) % 4][0], approx[(i + 2) % 4][0]
                v1 = (p1 - p2) / np.linalg.norm(p1 - p2)
                v2 = (p3 - p2) / np.linalg.norm(p3 - p2)
                cosine_angle = np.dot(v1, v2)
                cosines.append(cosine_angle)

            if max(cosines) < 0.1:  # 阈值判断是否接近 90 度
                cv2.drawContours(frame, [approx], 0, (0, 255, 0), 3)  # 绿色框表示菱形

    """
    # 压缩图像以减少带宽
    result, encoded_image = cv2.imencode(
        '.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 90])

    # 将编码后的图像数据分成多个块进行发送
    total_chunks = (len(encoded_image) // CHUNK_SIZE) + \
        (1 if len(encoded_image) % CHUNK_SIZE > 0 else 0)

    for i in range(total_chunks):
        start = i * CHUNK_SIZE
        end = min((i + 1) * CHUNK_SIZE, len(encoded_image))
        chunk_data = encoded_image[start:end]

        # 发送头部信息：chunk编号和总chunk数
        header = struct.pack("Q", i) + struct.pack("Q", total_chunks)

        # 将chunk_data转换为字节串并发送
        sock.sendto(header + chunk_data.tobytes(), server_address)
