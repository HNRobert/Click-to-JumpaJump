import RPi.GPIO as GPIO
import time
from multiprocessing import Process

# 设置GPIO模式为BCM编号方式
GPIO.setmode(GPIO.BCM)


def detect_level():
    print("GPIO 13: ")
    # 读取GPIO 13的电位
    for i in range(200):
        time.sleep(0.1)
        if GPIO.input(13):
            print("-", end="")
        else:
            print("_", end="")
    """
    while not GPIO.input(13):
        pass
    print("BOOM!")
    """
    print("\n检测完成")


def set_21_output():
    for i in range(10):
        # 将GPIO 21设为高电平（点亮LED或控制设备）
        GPIO.output(21, GPIO.HIGH)

        # 等待1秒
        time.sleep(1)

        # 将GPIO 21设为低电平（关闭LED或停止设备）
        GPIO.output(21, GPIO.LOW)
        time.sleep(1)
    print("GPIO 21 输出完成")


# 设置任意GPIO（如GPIO 21）为输出模式
GPIO.setup(21, GPIO.OUT)
GPIO.setup(20, GPIO.OUT)
GPIO.setup(19, GPIO.OUT)
# 设置GPIO 13为输入模式（假设它连接到了一个开关或信号源）
GPIO.setup(13, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

GPIO.output(19, GPIO.LOW)
GPIO.output(20, GPIO.HIGH)

# 创建并启动进程
p1 = Process(target=detect_level)
p2 = Process(target=set_21_output)

p1.start()
p2.start()

# 等待进程完成
p1.join()
p2.join()

# 清理GPIO设置
GPIO.cleanup()
