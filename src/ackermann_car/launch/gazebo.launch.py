from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import ExecuteProcess, DeclareLaunchArgument, RegisterEventHandler, TimerAction, LogInfo
from launch.event_handlers import OnProcessStart, OnProcessExit
from launch.substitutions import LaunchConfiguration
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    # 获取 ackermann_car 包的共享目录
    pkg_path = get_package_share_directory('ackermann_car')
    # 设置 SDF 文件路径
    world_file = os.path.join(pkg_path, 'worlds', 'ackermann_world.sdf')

    # 声明启动参数
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')

    # 定义 clock_bridge 节点
    clock_bridge_node = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='clock_bridge',
        output='screen',
        arguments=[
            '/clock@rosgraph_msgs/msg/Clock@ignition.msgs.Clock'
        ],
        parameters=[{'use_sim_time': use_sim_time, 'qos': {'depth': 10, 'reliability': 'reliable'}}]
    )

    return LaunchDescription([
        # 声明 use_sim_time 参数
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use simulation (Gazebo) clock if true'
        ),

        # 启动 Ignition Gazebo（含 GUI，确保运行）
        ExecuteProcess(
            cmd=['ign', 'gazebo', '-v', '4', '-r', world_file],
            output='screen',
            name='gazebo_server',
            additional_env={'IGN_GAZEBO_SYSTEM_PLUGIN_PATH': '/usr/lib/x86_64-linux-gnu/ign-gazebo-6/plugins'},
            shell=True
        ),

        # 记录 Gazebo 启动日志
        LogInfo(
            msg='Starting Ignition Gazebo with world: ' + world_file
        ),

        # 发布仿真时钟
        clock_bridge_node,

        # 启动 ROS 2 与 Gazebo 的桥接器（ROS -> GZ）
        Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            name='chair_bridge',
            output='screen',
            arguments=[
                '/chair_cmd@geometry_msgs/msg/Twist@ignition.msgs.Twist'
            ],
            parameters=[{'use_sim_time': use_sim_time, 'qos': {'depth': 10, 'reliability': 'reliable'}}]
        ),
        Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            name='cart_bridge',
            output='screen',
            arguments=[
                '/cart_cmd@geometry_msgs/msg/Twist@ignition.msgs.Twist'
            ],
            parameters=[{'use_sim_time': use_sim_time, 'qos': {'depth': 10, 'reliability': 'reliable'}}]
        ),
        Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            name='box_bridge',
            output='screen',
            arguments=[
                '/box_cmd@geometry_msgs/msg/Twist@ignition.msgs.Twist'
            ],
            parameters=[{'use_sim_time': use_sim_time, 'qos': {'depth': 10, 'reliability': 'reliable'}}]
        ),

        # 等待 clock_bridge 启动后启动 world_controller
        RegisterEventHandler(
            event_handler=OnProcessStart(
                target_action=clock_bridge_node,
                on_start=[
                    TimerAction(
                        period=5.0,  # 增加延迟到 5 秒
                        actions=[
                            Node(
                                package='ackermann_car',
                                executable='world_controller',
                                name='world_controller',
                                output='screen',
                                parameters=[{'use_sim_time': use_sim_time}],
                                arguments=['--ros-args', '--log-level', 'debug'],
                                emulate_tty=True
                            )
                        ]
                    )
                ]
            )
        ),

        # 捕获 world_controller 退出事件
        RegisterEventHandler(
            event_handler=OnProcessExit(
                target_action=Node(
                    package='ackermann_car',
                    executable='world_controller',
                    name='world_controller'
                ),
                on_exit=[
                    LogInfo(
                        msg='world_controller process exited unexpectedly'
                    )
                ]
            )
        )
    ])