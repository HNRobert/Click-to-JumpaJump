from picamera2 import Picamera2

# 初始化摄像头
picam2 = Picamera2()

# 获取摄像头支持的模式
camera_modes = picam2.sensor_modes

# 打印支持的分辨率和其他可用信息
for mode in camera_modes:
    resolution = mode.get('size', 'Unknown resolution')
    fps_range = mode.get('fps', 'Unknown FPS')  # 尝试获取 fps 或提供默认值
    print(f"Resolution: {resolution} - FPS: {fps_range}")
