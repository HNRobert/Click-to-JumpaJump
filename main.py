import socket
import cv2
import numpy as np
import struct
import time

# 常量定义
CHUNK_SIZE = 1024  # 与发送端的块大小保持一致
PORT = 5000
BUFFER_SIZE = CHUNK_SIZE + 16  # 包括16字节的两个64位整数（头部信息）
RECEIVE_TIMEOUT = 2  # 等待所有块到达的超时时间 (秒)

# 设置UDP套接字
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('0.0.0.0', PORT))  # 绑定到任意IP地址，接收端口5000的数据
sock.settimeout(RECEIVE_TIMEOUT)  # 设置接收超时

# 用于发送点击坐标回服务端
send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('192.168.2.3', 5001)  # 替换为发送坐标的服务端 IP 和端口

# 存储重组的图像数据
image_chunks = {}
clicked_coords = None  # 用于存储鼠标点击的坐标

# 鼠标回调函数


def mark_point(event, x, y, flags, param):
    global clicked_coords
    if event == cv2.EVENT_LBUTTONDOWN:
        # 记录点击的坐标
        clicked_coords = (x, y)
        print(f"Mouse clicked at: {clicked_coords}")

        # 将坐标打包成 UDP 数据并发送回服务端
        data = struct.pack('ii', x, y)  # 打包为两个32位整数
        send_sock.sendto(data, server_address)


while True:
    try:
        while True:
            # 接收UDP数据
            data, addr = sock.recvfrom(BUFFER_SIZE)

            # 提取头部信息：chunk编号和总chunk数
            chunk_index = struct.unpack("Q", data[:8])[0]  # 前8字节是chunk编号
            total_chunks = struct.unpack("Q", data[8:16])[0]  # 接下来8字节是总chunk数

            # 提取数据块
            chunk_data = data[16:]

            # 将数据块存储在字典中，以chunk_index为键
            image_chunks[chunk_index] = chunk_data

            # 检查是否所有块都接收到
            if len(image_chunks) == total_chunks:
                break

    except socket.timeout:
        print("Timeout reached, missing chunks. Skipping this frame.")
        image_chunks.clear()  # 清空数据，准备接收下一帧
        continue

    # 重组所有块数据
    try:
        full_image_data = b''.join([image_chunks[i]
                                   for i in range(total_chunks)])
    except KeyError as e:
        print(f"Missing chunk: {e}. Skipping this frame.")
        image_chunks.clear()  # 清空数据，准备接收下一帧
        continue

    # 清空字典以便接收下一帧
    image_chunks.clear()

    # 使用OpenCV解码JPEG图像
    nparr = np.frombuffer(full_image_data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # 显示图像
    cv2.imshow('Received Image', img)

    # 设置鼠标点击回调
    cv2.setMouseCallback('Received Image', mark_point)

    # 按下'q'键退出循环
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 关闭窗口和套接字
cv2.destroyAllWindows()
sock.close()
send_sock.close()
