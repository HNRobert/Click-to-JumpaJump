from picamera2 import Picamera2
import time
import os

DATABASE_NAME = "i_database"

if not os.path.isdir(DATABASE_NAME):
    os.makedirs(DATABASE_NAME)


def file_path(num):
    return f"{DATABASE_NAME}/{num}.jpg"

# 创建Picamera2对象
camera = Picamera2()

controls = {
    "AeEnable": False,  # 禁用自动曝光
    "AnalogueGain": 1.0,  # 增益控制
    "ExposureTime": 50000  # 曝光时间，单位微秒
}
camera.set_controls(controls)

print(camera.camera_configuration())  # 查看当前摄像头的配置

# 配置相机
camera.configure(camera.create_still_configuration())

# 启动相机
camera.start()
# 捕捉图像并保存

img_num = 1

cmd="NONE"
while cmd!="q":
    if cmd=="a" or not cmd:
        while os.path.exists(file_path(img_num)):
            print(f"File exists:{file_path(img_num)}")
            img_num += 1
        camera.capture_file(file_path(img_num))
        print(f"\nImage saved as: {file_path(img_num)}")
    elif cmd=="r":
        camera.capture_file(file_path(img_num))
        print(f"\nImage saved as: {file_path(img_num)}")
    else:
        pass
    cmd=input("GEN_DATA >> ")

# 停止相机
camera.stop()


