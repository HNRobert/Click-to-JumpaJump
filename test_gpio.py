import sys
import time
import threading
import RPi.GPIO as GPIO

# 设置GPIO模式为BCM编号方式
GPIO.setmode(GPIO.BCM)

# 设置GPIO引脚为输入模式和输出模式
GPIO.setup(21, GPIO.OUT)
GPIO.setup(20, GPIO.OUT)
GPIO.setup(19, GPIO.OUT)
GPIO.setup(13, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)


GPIO.output(19, GPIO.LOW)
GPIO.output(20, GPIO.HIGH)

cmd = "NULL"

def is_num(value):
    try:
        float(value)
        return True
    except:
        return False

def monitor_gpio():
    global cmd
    """ 定期监测 GPIO 13 的电位并输出 """
    while cmd != "q":
        level = GPIO.input(13)
        # 将 GPIO 状态显示在终端最后一行
        sys.stdout.write(
            f"\rGPIO 13 Level: {'-' if level else '_'} ; GPIO_MANUAL_TEST >> ")
        sys.stdout.flush()
        time.sleep(0.1)  # 每隔0.1秒更新一次电位状态


def handle_input():
    """ 处理用户输入的命令 """
    global cmd
    state21 = False
    GPIO.output(21, GPIO.LOW)

    while cmd != "q":
        cmd = input("")

        if cmd == "l":
            state21 = False
            GPIO.output(21, GPIO.LOW)
        elif cmd == "h":
            state21 = True
            GPIO.output(21, GPIO.HIGH)
        elif cmd == "s" or cmd == "":
            state21 = not state21
            GPIO.output(21, GPIO.HIGH if state21 else GPIO.LOW)
        elif is_num(cmd):
            state21 = True
            GPIO.output(21, GPIO.HIGH)
            print("pressd")
            time.sleep(float(cmd))
            state21 = False
            GPIO.output(21, GPIO.LOW)
            print("released")

"""
# 创建并启动监控 GPIO 的线程
gpio_thread = threading.Thread(target=monitor_gpio)
gpio_thread.daemon = True  # 设置为守护线程，这样主线程结束后它也会自动结束
gpio_thread.start()
"""

# 主线程处理用户输入
handle_input()

# 清理GPIO设置
GPIO.cleanup()
