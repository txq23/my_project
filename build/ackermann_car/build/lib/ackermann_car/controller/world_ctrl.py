#!/usr/bin/env python3
import rclpy
import math
from rclpy.node import Node
from geometry_msgs.msg import Twist
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy

class WorldController(Node):
    def __init__(self):
        super().__init__('world_controller')
        
        # 初始化发布者
        qos = QoSProfile(
            depth=10,
            reliability=ReliabilityPolicy.RELIABLE,
            history=HistoryPolicy.KEEP_LAST
        )
        self.chair_pub = self.create_publisher(Twist, '/chair_cmd', qos)
        self.cart_pub = self.create_publisher(Twist, '/cart_cmd', qos)
        self.box_pub = self.create_publisher(Twist, '/box_cmd', qos)

        # ========== 参数配置 ==========
        # 椅子控制参数
        self.chair_speed = 1.2      # 线速度提高至1.2 m/s
        self.chair_interval = 4.0   # 方向切换间隔延长至4秒
        
        # 箱子椭圆运动参数
        self.ellipse_x_amp = 1.5    # X轴振幅 (m/s)
        self.ellipse_y_amp = 0.8    # Y轴振幅 (m/s)
        self.ellipse_freq = 0.25    # 频率降低至0.25 Hz
        
        # 初始化变量
        self.start_time = self.get_clock().now().nanoseconds * 1e-9
        self.last_chair_switch = self.start_time
        self.chair_direction = 1.0
        
        self.create_timer(0.05, self.control_callback)
        self.get_logger().info("运动参数：椅子速度=%.1fm/s 箱子椭圆轨迹(%.1f,%.1f)" % (
            self.chair_speed, 
            self.ellipse_x_amp,
            self.ellipse_y_amp
        ))

    def control_callback(self):
        try:
            current_time = self.get_clock().now().nanoseconds * 1e-9
            elapsed = current_time - self.start_time

            # === 椅子控制 ===
            if current_time - self.last_chair_switch >= self.chair_interval:
                self.chair_direction *= -1
                self.last_chair_switch = current_time
                self.get_logger().info(f"椅子方向切换 → {self.chair_direction}")
            
            chair_cmd = Twist()
            chair_cmd.linear.x = self.chair_speed * self.chair_direction  # 提高速度

            # === 推车控制（保持原逻辑） ===
            cart_cmd = Twist()
            cart_cmd.linear.x = 0.3
            cart_cmd.angular.z = 0.4

            # === 箱子椭圆运动 ===
            box_cmd = Twist()
            omega = 2 * math.pi * self.ellipse_freq
            # X轴速度：相位0的正弦波
            box_cmd.linear.x = self.ellipse_x_amp * math.sin(omega * elapsed)
            # Y轴速度：相位差90度的正弦波（余弦）
            box_cmd.linear.y = self.ellipse_y_amp * math.cos(omega * elapsed)
            # 清除旋转分量
            box_cmd.angular.z = 0.0

            # 发布指令
            self.chair_pub.publish(chair_cmd)
            self.cart_pub.publish(cart_cmd)
            self.box_pub.publish(box_cmd)

        except Exception as e:
            self.get_logger().error(f"控制错误: {str(e)}")

def main(args=None):
    rclpy.init(args=args)
    controller = WorldController()
    try:
        rclpy.spin(controller)
    except KeyboardInterrupt:
        pass
    finally:
        rclpy.shutdown()

if __name__ == '__main__':
    main()