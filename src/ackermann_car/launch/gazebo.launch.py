from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import ExecuteProcess, DeclareLaunchArgument, RegisterEventHandler, LogInfo
from launch.event_handlers import OnProcessStart
from launch.substitutions import LaunchConfiguration
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    pkg_path = get_package_share_directory('ackermann_car')
    world_file = os.path.join(pkg_path, 'worlds', 'ackermann_world.sdf')
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')

    # 启动 Gazebo
    gazebo_server = ExecuteProcess(
        cmd=['ign', 'gazebo', '-v', '4', '-r', world_file],
        output='screen',
        name='gazebo_server',
        additional_env={
            'IGN_GAZEBO_SYSTEM_PLUGIN_PATH':
                '/usr/lib/x86_64-linux-gnu/ign-gazebo-6/plugins:/opt/ros/humble/lib/ros_gz_sim'
        },
        shell=True
    )

    # 桥接器（正确格式：@）
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

    # 控制器节点
    world_controller_node = Node(
        package='ackermann_car',
        executable='world_controller',
        name='world_controller',
        output='screen',
        # parameters=[{'use_sim_time': use_sim_time}],
        arguments=['--ros-args', '--log-level', 'debug'],
        emulate_tty=True
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use simulation (Gazebo) clock if true'
        ),

        gazebo_server,

        RegisterEventHandler(
            event_handler=OnProcessStart(
                target_action=gazebo_server,
                on_start=[
                    ExecuteProcess(
                        cmd=['bash', '-c', 'until ros2 topic list | grep -q "/clock"; do sleep 1; done'],
                        shell=True,
                        output='screen'
                    ),
                    LogInfo(msg='✅ Gazebo initialized. Launching bridges and controller...'),
                    obstacle_bridge_node,
                    world_controller_node
                ]
            )
        )
    ])
