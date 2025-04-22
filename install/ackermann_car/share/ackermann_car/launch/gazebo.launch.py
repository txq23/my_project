from launch import LaunchDescription
from launch.actions import ExecuteProcess, TimerAction, DeclareLaunchArgument, LogInfo
from launch_ros.actions import Node
from launch.substitutions import LaunchConfiguration
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    pkg_path = get_package_share_directory('ackermann_car')
    world_file = os.path.join(pkg_path, 'worlds', 'ackermann_world.sdf')

    gazebo_server = ExecuteProcess(
        cmd=['ign', 'gazebo', '-v', '4', '-r', world_file],
        output='screen',
        shell=True,
        name='gazebo_server',
        additional_env={
            'IGN_GAZEBO_SYSTEM_PLUGIN_PATH':
                '/usr/lib/x86_64-linux-gnu/ign-gazebo-6/plugins:/opt/ros/humble/lib/ros_gz_sim'
        },
    )

    obstacle_bridge_node = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='obstacle_bridge',
        output='screen',
        arguments=[
            '/clock@rosgraph_msgs/msg/Clock@ignition.msgs.Clock',
            '/chair_cmd@geometry_msgs/msg/Twist@ignition.msgs.Twist',
            '/cart_cmd@geometry_msgs/msg/Twist@ignition.msgs.Twist',
            '/box_cmd@geometry_msgs/msg/Twist@ignition.msgs.Twist'
        ],
        parameters=[{'use_sim_time': use_sim_time}]
    )

    world_controller_node = Node(
        package='ackermann_car',
        executable='world_controller',
        name='world_controller',
        output='screen',
        # parameters=[{'use_sim_time': use_sim_time}],
        arguments=['--ros-args', '--log-level', 'debug'],
        emulate_tty=True
    )

    # 等 Gazebo 启动后，延迟3秒启动桥和控制器
    delayed_launch = TimerAction(
        period=3.0,
        actions=[
            LogInfo(msg='⏳ Waiting 3s before launching bridge and controller...'),
            obstacle_bridge_node,
            world_controller_node
        ]
    )

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        gazebo_server,
        delayed_launch
    ])
