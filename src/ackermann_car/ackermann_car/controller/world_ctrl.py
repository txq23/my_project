#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import random

class WorldController(Node):
    def __init__(self):
        super().__init__('world_controller')
        self.get_logger().info('WorldController starting...')
        try:
            # 获取 use_sim_time 参数（不重复声明）
            self.get_logger().debug('Accessing use_sim_time parameter...')
            use_sim_time = self.get_parameter_or('use_sim_time', rclpy.Parameter('use_sim_time', rclpy.Parameter.Type.BOOL, True)).value
            self.get_logger().info(f'use_sim_time: {use_sim_time}')

            # 创建发布者
            self.get_logger().debug('Creating publishers...')
            self.chair_pub = self.create_publisher(Twist, '/chair_cmd', 10)
            self.cart_pub = self.create_publisher(Twist, '/cart_cmd', 10)
            self.box_pub = self.create_publisher(Twist, '/box_cmd', 10)
            self.get_logger().debug('Publishers created')

            # 检查仿真时间
            self.get_logger().debug('Checking clock...')
            try:
                self.get_clock().now()
                self.get_logger().debug('Clock accessible')
            except Exception as e:
                self.get_logger().error(f'Clock error: {str(e)}')

            # 定时器：20 Hz
            self.get_logger().debug('Creating timer...')
            self.timer = self.create_timer(0.05, self.timer_callback)
            self.get_logger().debug('Timer created')

            self.start_time = self.get_clock().now().to_msg().sec
            self.chair_direction = 1.0  # 1.0 正向，-1.0 反向
            self.stuck_counter = 0
            self.get_logger().info('WorldController initialized')
        except Exception as e:
            self.get_logger().error(f'Initialization failed: {str(e)}')
            raise

    def timer_callback(self):
        try:
            self.get_logger().debug('Timer callback triggered')
            current_time = self.get_clock().now().to_msg().sec
            self.get_logger().debug(f'Current sim time: {current_time}')

            # 检测 chair 是否卡住
            if self.stuck_counter > 40:  # 2秒
                self.chair_direction *= -1.0
                self.stuck_counter = 0
                self.get_logger().info('Chair stuck, reversing direction')

            # 椅子：直线移动
            chair_cmd = Twist()
            chair_cmd.linear.x = 0.3 * self.chair_direction
            self.get_logger().debug(f'Publishing chair_cmd: linear.x = {chair_cmd.linear.x}')
            self.stuck_counter += 1

            # 小推车：绕圈
            cart_cmd = Twist()
            cart_cmd.linear.x = 0.2
            cart_cmd.angular.z = 0.5
            self.get_logger().debug('Publishing cart_cmd: linear.x = 0.2, angular.z = 0.5')

            # 箱子：随机移动
            box_cmd = Twist()
            elapsed = current_time - self.start_time
            if elapsed % 4 < 2:
                box_cmd.linear.x = 0.2
                box_cmd.angular.z = random.uniform(-0.3, 0.3)
            else:
                box_cmd.linear.y = 0.2
                box_cmd.angular.z = random.uniform(-0.3, 0.3)
            self.get_logger().debug(f'Publishing box_cmd: linear.x = {box_cmd.linear.x}, linear.y = {box_cmd.linear.y}')

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