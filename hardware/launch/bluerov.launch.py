from ament_index_python.packages import get_package_share_path
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    GroupAction,
    IncludeLaunchDescription,
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node, PushRosNamespace

from hippo_common.launch_helper import (
    PassLaunchArguments,
    declare_vehicle_name_and_sim_time,
)


def declare_launch_args(launch_description: LaunchDescription):
    declare_vehicle_name_and_sim_time(launch_description=launch_description)

    package_path = get_package_share_path('hippo_control')
    default_path = str(package_path /
                       'config/actuator_mixer/bluerov_normalized_default.yaml')
    action = DeclareLaunchArgument(
        name='mixer_path',
        default_value=default_path,
        description='Path to mixer configuration .yaml file')
    launch_description.add_action(action)


def include_mixer():
    package_path = get_package_share_path('hippo_control')
    path = str(package_path / 'launch/node_actuator_mixer.launch.py')
    source = PythonLaunchDescriptionSource(path)
    args = PassLaunchArguments()
    args.add_vehicle_name_and_sim_time()
    args.add(['mixer_path'])
    mixer = IncludeLaunchDescription(source, launch_arguments=args.items())
    return mixer


def add_camera_node():
    action = Node(executable='v4l2_camera_node',
                  package='v4l2_camera',
                  name='front_camera',
                  namespace='front_camera',
                  parameters=[
                      {
                          'image_size': [640, 480],
                      },
                  ])
    return action


def add_jpeg_camera_node():
    action = Node(executable='mjpeg_cam_node',
                  package='mjpeg_cam',
                  name='front_camera',
                  namespace='front_camera',
                  parameters=[
                      {
                          'device_id': 0,
                          'discrete_size': 3,
                      },
                  ])
    return action


def add_newton_gripper_node():
    args = PassLaunchArguments()
    args.add_vehicle_name_and_sim_time()
    action = Node(executable='newton_gripper_node',
                  package='hardware',
                  name='newton_gripper',
                  parameters=[args])
    return action


def add_esc_node():
    args = PassLaunchArguments()
    args.add_vehicle_name_and_sim_time()
    action = Node(executable='teensy_commander_node',
                  package='esc',
                  name='esc_commander',
                  parameters=[args])
    return action


def add_camera_servo_node():
    args = PassLaunchArguments()
    args.add_vehicle_name_and_sim_time()
    action = Node(executable='camera_servo_node',
                  package='hardware',
                  name='camera_servo',
                  parameters=[args])
    return action


def add_spotlight_node():
    args = PassLaunchArguments()
    args.add_vehicle_name_and_sim_time()
    action = Node(executable='spotlight_node',
                  package='hardware',
                  name='spotlight',
                  parameters=[args])
    return action


def add_micro_ros_agent():
    action = Node(
        executable='micro_ros_agent',
        package='micro_ros_agent',
        name='dds_agent',
        arguments=['serial', '--dev', '/dev/fcu_data', '-b', '921600'])
    return action


def generate_launch_description():
    launch_description = LaunchDescription()
    declare_launch_args(launch_description=launch_description)

    actions = [
        include_mixer(),
        # add_camera_node(),
        add_jpeg_camera_node(),
        add_newton_gripper_node(),
        add_camera_servo_node(),
        add_spotlight_node(),
        add_esc_node(),
    ]
    group = GroupAction(
        [PushRosNamespace(LaunchConfiguration('vehicle_name'))] + actions)
    launch_description.add_action(group)

    launch_description.add_action(add_micro_ros_agent())

    return launch_description
