from launch import LaunchDescription
from launch.actions import ExecuteProcess, TimerAction, DeclareLaunchArgument, LogInfo
from launch_ros.actions import Node
from launch.substitutions import LaunchConfiguration, Command
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    # 获取包路径
    pkg_path = get_package_share_directory('ackermann_car')

    # 默认 world 文件路径
    default_world_file = os.path.join(pkg_path, 'worlds', 'ackermann_world.sdf')

    # Xacro 文件路径（已修复连接结构）
    xacro_file_path = '/home/wcy/ros2_ws/src/ackermann_car/urdf/ackermann_car.xacro'

    # 定义 launch 参数
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    world_file = LaunchConfiguration('world_file', default=default_world_file)

    # 使用 xacro 命令生成 URDF
    robot_description = Command(['xacro ', xacro_file_path])

    # 启动 Gazebo 服务器
    gazebo_server = ExecuteProcess(
        cmd=['ign', 'gazebo', '-v', '4', '-r', world_file],
        output='screen',
        shell=True,
        name='gazebo_server',
        additional_env={
            'IGN_GAZEBO_SYSTEM_PLUGIN_PATH': '/usr/lib/x86_64-linux-gnu/ign-gazebo-6/plugins:/opt/ros/humble/lib/ros_gz_sim',
            'IGN_GAZEBO_RESOURCE_PATH': os.path.join(pkg_path, 'meshes')
        },
    )

    # 发布 robot_description
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[
            {'use_sim_time': use_sim_time},
            {'robot_description': robot_description}
        ]
    )

    # spawn机器人（类型 urdf，确保加载成功）
    spawn_entity_node = Node(
        package='ros_gz_sim',
        executable='create',
        name='spawn_entity',
        output='screen',
        arguments=[
            '--type', 'urdf',
            '-world', 'ackermann_world',
            '-topic', '/robot_description',
            '-name', 'ackermann_car',
            '-x', '5', '-y', '5', '-z', '0.3'
        ],
        parameters=[{'use_sim_time': use_sim_time}]
    )

    # 桥接节点
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

    # 世界控制器节点
    world_controller_node = Node(
        package='ackermann_car',
        executable='world_controller',
        name='world_controller',
        output='screen',
        arguments=['--ros-args', '--log-level', 'debug'],
        emulate_tty=True,
        parameters=[{'use_sim_time': use_sim_time}]
    )

    # 延迟启动
    delayed_launch = TimerAction(
        period=3.0,
        actions=[
            LogInfo(msg='⏳ Waiting 3s before launching bridge, robot_state_publisher, spawn_entity, and world_controller...'),
            robot_state_publisher_node,
            spawn_entity_node,
            obstacle_bridge_node,
            world_controller_node
        ]
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            name='use_sim_time',
            default_value='true',
            description='Use simulation (Gazebo) clock if true'
        ),
        DeclareLaunchArgument(
            name='world_file',
            default_value=default_world_file,
            description='Path to the Gazebo world file (.sdf)'
        ),
        gazebo_server,
        delayed_launch
    ])
