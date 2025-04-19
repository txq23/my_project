#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import Float64
import math

class MotionController(Node):
    def __init__(self):
        super().__init__('motion_controller')
        
        # 箱子控制参数
        self.box_speed = 0.5  # m/s
        self.box_direction = 1
        
        # 圆柱体正弦运动参数
        self.amplitude = 2.0   # 振幅 (m)
        self.period = 5.0      # 周期 (秒)
        
        # 创建发布者
        self.box_pub = self.create_publisher(
            Twist, 
            '/model/moving_box/cmd_vel', 
            10
        )
        
        self.cylinder_pub = self.create_publisher(
            Float64, 
            '/model/moving_cylinder/joint/sliding_joint/cmd_vel', 
            10
        )
        
        # 定时器 (50Hz)
        self.timer = self.create_timer(0.02, self.timer_callback)
        self.start_time = self.get_clock().now().nanoseconds / 1e9

    def timer_callback(self):
        # 控制箱子自动往返
        self.control_box()
        
        # 控制圆柱体正弦运动
        self.control_cylinder()

    def control_box(self):
        """箱子自动往返控制"""
        msg = Twist()
        msg.linear.x = self.box_speed * self.box_direction
        
        # 每5秒反转方向
        if (self.get_clock().now().nanoseconds / 1e9 - self.start_time) % 10 < 5:
            self.box_direction = 1
        else:
            self.box_direction = -1
        
        self.box_pub.publish(msg)

    def control_cylinder(self):
        """圆柱体正弦速度控制"""
        t = self.get_clock().now().nanoseconds / 1e9 - self.start_time
        velocity = self.amplitude * (2 * math.pi / self.period) * math.cos(2 * math.pi * t / self.period)
        
        msg = Float64()
        msg.data = velocity
        self.cylinder_pub.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    controller = MotionController()
    rclpy.spin(controller)
    controller.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()