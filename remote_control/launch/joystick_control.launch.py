import launch
import launch_ros


def generate_launch_description():
    use_sim_time = launch.substitutions.LaunchConfiguration('use_sim_time')
    vehicle_name = launch.substitutions.LaunchConfiguration('vehicle_name')

    vehicle_name_arg = launch.actions.DeclareLaunchArgument(
        name='vehicle_name', description='Vehicle name used as namespace.')
    use_sim_time_arg = launch.actions.DeclareLaunchArgument(
        name='use_sim_time', description='decide if simulation time is used.')

    launch_args = [vehicle_name_arg, use_sim_time_arg]

    composable_nodes = [
        launch_ros.descriptions.ComposableNode(
            package='joy',
            plugin='joy::Joy',
            name='joystick',
            parameters=[{
                'device_id': 0,
                'device_name': '',
                'deadzone': 0.5,
                'autorepeat_rate': 20.0,
                'sticky_buttons': False,
                'coalesce_interval_ms': 1,
            }],
            parameters=[{
                'use_sim_time': use_sim_time,
                'vehicle_name': vehicle_name,
            }],
            extra_arguments=[
                {
                    'use_intra_process_comms': True
                },
            ]),
        launch_ros.descriptions.ComposableNode(
            package='remote_control',
            plugin='remote_control::joystick::JoyStick',
            name='joystick_mapper',
            parameters=[{
                'use_sim_time': use_sim_time,
                'vehicle_name': vehicle_name,
            }],
            extra_arguments=[
                {
                    'use_intra_process_comms': True
                },
            ]),
    ]
    container = launch_ros.actions.ComposableNodeContainer(
        name='joystick_container',
        namespace='',
        package='rclcpp_components',
        executable='component_container',
        composable_node_descriptions=composable_nodes,
        output='screen')

    nodes_group = launch.actions.GroupAction([
        launch_ros.actions.PushRosNamespace(vehicle_name),
        container,
    ])

    return launch.LaunchDescription(launch_args + [
        nodes_group,
    ])
