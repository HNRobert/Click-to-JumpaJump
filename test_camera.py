from picamera2 import Picamera2
import time

# 创建Picamera2对象
camera = Picamera2()

print(camera.camera_configuration())  # 查看当前摄像头的配置

# 配置相机
camera.configure(camera.create_still_configuration())

# 启动相机
camera.start()
# 捕捉图像并保存
time.sleep(2)  # 等待相机自动调整
camera.capture_file("test_image.jpg")

# 停止相机
camera.stop()

print("图像已保存为 test_image.jpg")
