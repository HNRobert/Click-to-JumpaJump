import socket
import cv2
import numpy as np
from picamera2 import Picamera2
import struct

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

# 加载自训练的人脸检测分类器
face_cascade = cv2.CascadeClassifier(
    "i_database/cascade.xml")  # 替换为自训练的模型路径

# 创建UDP套接字
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('192.168.2.1', 5000)  # 替换为 MacBook 的 IP 地址

# 定义数据块大小
CHUNK_SIZE = 1024  # 发送的每个数据块大小

while True:
    # 捕获摄像头帧
    frame = picam2.capture_array()

    # 将图像转换为灰度图像以提高人脸检测性能
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

    # 使用自训练的人脸分类器检测人脸
    faces = face_cascade.detectMultiScale(
        gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    # 在检测到的人脸上绘制矩形框
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h),
                      (255, 0, 0), 2)  # 在原图中画出人脸

    # 压缩图像以减少带宽
    result, encoded_image = cv2.imencode(
        '.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 90])  # 高质量压缩

    # 将编码后的图像数据分成多个块进行发送
    total_chunks = (len(encoded_image) // CHUNK_SIZE) + \
        (1 if len(encoded_image) % CHUNK_SIZE > 0 else 0)

    for i in range(total_chunks):
        start = i * CHUNK_SIZE
        end = min((i + 1) * CHUNK_SIZE, len(encoded_image))
        chunk_data = encoded_image[start:end]

        # 发送头部信息：chunk编号和总chunk数
        header = struct.pack("Q", i) + struct.pack("Q",
                                                   total_chunks)  # chunk编号和总块数

        # 将chunk_data转换为字节串并发送
        sock.sendto(header + chunk_data.tobytes(), server_address)
