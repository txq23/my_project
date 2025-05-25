from launch import LaunchDescription
from launch.actions import ExecuteProcess, TimerAction, DeclareLaunchArgument, LogInfo
from launch_ros.actions import Node
from launch.substitutions import LaunchConfiguration, Command
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    pkg_path = get_package_share_directory('ackermann_car')
    default_world_file = os.path.join(pkg_path, 'worlds', 'ackermann_world.sdf')
    xacro_file_path = os.path.join(pkg_path, 'urdf', 'ackermann_car.xacro')

    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    world_file = LaunchConfiguration('world_file', default=default_world_file)

    robot_description = Command(['xacro ', xacro_file_path])

    # ✅ 修改此处，添加 libgazebo_ros_init.so 插件加载
    gazebo_server = ExecuteProcess(
        cmd=[
            'gazebo', '--verbose',
            '-s', 'libgazebo_ros_factory.so',
            '-s', 'libgazebo_ros_init.so',
            world_file
        ],
        output='screen',
        additional_env={'GAZEBO_MODEL_PATH': os.path.join(pkg_path, 'meshes')},
    )

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

    spawn_entity_node = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        name='spawn_entity',
        output='screen',
        arguments=[
            '-entity', 'ackermann_car',
            '-topic', '/robot_description',
            '-x', '5', '-y', '5', '-z', '0.3'
        ],
        parameters=[{'use_sim_time': use_sim_time}]
    )

    world_controller_node = Node(
        package='ackermann_car',
        executable='world_controller',
        name='world_controller',
        output='screen',
        arguments=['--ros-args', '--log-level', 'debug'],
        parameters=[
            {'use_sim_time': use_sim_time},
            {'chair_speed': 1.2},
            {'box_trajectory_a': 1.5},
            {'box_trajectory_b': 0.8}
        ]
    )

    delayed_launch = TimerAction(
        period=10.0,
        actions=[
            LogInfo(msg='⏳ Waiting 10s before launching robot_state_publisher, spawn_entity, and world_controller...'),
            robot_state_publisher_node,
            spawn_entity_node,
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
