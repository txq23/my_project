#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
import random
import time

class WorldController(Node):
    def __init__(self):
        super().__init__('world_controller')
        self.get_logger().info('WorldController starting...')
        try:
            # 获取 use_sim_time 参数
            
            use_sim_time = self.get_parameter('use_sim_time').get_parameter_value().bool_value
            self.get_logger().info(f'use_sim_time: {use_sim_time}')

            # 创建发布者（使用可靠 QoS）
            qos = QoSProfile(depth=10, reliability=ReliabilityPolicy.RELIABLE, history=HistoryPolicy.KEEP_LAST)
            self.chair_pub = self.create_publisher(Twist, '/chair_cmd', qos)
            self.cart_pub = self.create_publisher(Twist, '/cart_cmd', qos)
            self.box_pub = self.create_publisher(Twist, '/box_cmd', qos)

            # 等待仿真时间开始更新
            if use_sim_time:
                self.get_logger().info("Waiting for simulated clock to start...")
                last_time = self.get_clock().now().nanoseconds
                while rclpy.ok():
                    now = self.get_clock().now().nanoseconds
                    if now > last_time:
                        break
                    rclpy.spin_once(self, timeout_sec=0.1)
                self.get_logger().info("Simulated clock detected.")

            # 初始化时间
            try:
                self.start_time = self.get_clock().now().to_msg().sec
            except Exception:
                self.get_logger().warn('Failed to get initial sim time, using 0')
                self.start_time = 0

            # 初始化控制变量
            self.chair_direction = 1.0  # 1.0 正向，-1.0 反向
            self.stuck_counter = 0

            # 创建定时器：20Hz
            self.timer = self.create_timer(0.05, self.timer_callback)

            self.get_logger().info('WorldController initialized')

        except Exception as e:
            self.get_logger().error(f'Initialization failed: {str(e)}')
            raise

    def timer_callback(self):
        try:
            current_time = 0
            try:
                current_time = self.get_clock().now().to_msg().sec
            except Exception:
                self.get_logger().warn('Failed to get current sim time, using 0')

            # 检测 chair 是否卡住
            if self.stuck_counter > 40:  # 2秒
                self.chair_direction *= -1.0
                self.stuck_counter = 0
                self.get_logger().info('Chair stuck, reversing direction')

            # 椅子：直线移动
            chair_cmd = Twist()
            chair_cmd.linear.x = 0.3 * self.chair_direction
            self.stuck_counter += 1

            # 小推车：绕圈
            cart_cmd = Twist()
            cart_cmd.linear.x = 0.2
            cart_cmd.angular.z = 0.5

            # 箱子：随机移动
            box_cmd = Twist()
            elapsed = current_time - self.start_time
            if elapsed % 4 < 2:
                box_cmd.linear.x = 0.2
                box_cmd.angular.z = random.uniform(-0.3, 0.3)
            else:
                box_cmd.linear.y = 0.2
                box_cmd.angular.z = random.uniform(-0.3, 0.3)

            # 发布消息
            self.chair_pub.publish(chair_cmd)
            self.cart_pub.publish(cart_cmd)
            self.box_pub.publish(box_cmd)

        except Exception as e:
            self.get_logger().error(f'Timer callback failed: {str(e)}')

def main(args=None):
    rclpy.init(args=args)
    try:
        controller = WorldController()
        rclpy.spin(controller)
    except Exception as e:
        print(f'Error in main: {str(e)}')
    finally:
        rclpy.shutdown()

if __name__ == '__main__':
    main()
