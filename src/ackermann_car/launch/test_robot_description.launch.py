from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import Command

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{
                'robot_description': Command([
                    'xacro ', '/home/wcy/ros2_ws/src/ackermann_car/urdf/ackermann_car.xacro'
                ])
            }]
        )
    ])
