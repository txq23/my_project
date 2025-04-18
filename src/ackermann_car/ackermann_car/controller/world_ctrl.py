# launch/run_simulation.launch.py
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import ExecuteProcess
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    # 获取包路径
    pkg_path = get_package_share_directory('your_package_name')
    
    return LaunchDescription([
        # 1. 启动 Ignition Gazebo 服务器
        ExecuteProcess(
            cmd=['ign', 'gazebo', '-v', '4', 
                 os.path.join(pkg_path, 'worlds', 'your_world.sdf')],
            output='screen'
        ),

        # 2. 启动 Ignition Gazebo GUI 客户端
        ExecuteProcess(
            cmd=['ign', 'gazebo', '-g'],
            output='screen'
        ),

        # 3. 启动 ROS-Ignition 桥接
        Node(
            package='ros_ign_bridge',
            executable='parameter_bridge',
            name='bridge',
            output='screen',
            arguments=[
                # 箱子速度控制桥接
                '/model/moving_box/cmd_vel@geometry_msgs/msg/Twist[ignition.msgs.Twist',
                # 圆柱体关节控制桥接
                '/model/moving_cylinder/joint/sliding_joint/cmd_vel@std_msgs/msg/Float64[ignition.msgs.Double'
            ],
            parameters=[{'use_sim_time': True}]
        ),

        # 4. 启动运动控制节点
        Node(
            package='your_package_name',
            executable='motion_controller.py',
            name='motion_controller',
            output='screen'
        )
    ])