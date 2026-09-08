import os

import launch_ros
from ament_index_python.packages import get_package_share_directory
from launch_ros.actions import Node

from launch import LaunchDescription
from launch.actions import (DeclareLaunchArgument, ExecuteProcess,
                            IncludeLaunchDescription, SetEnvironmentVariable,
                            RegisterEventHandler, TimerAction)
from launch.conditions import IfCondition
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration, PythonExpression, PathJoinSubstitution


def generate_launch_description():
    """Launch file for Ignition Fortress (Gazebo) simulation."""

    robot_name = LaunchConfiguration("robot_name")
    use_sim_time = LaunchConfiguration("use_sim_time")
    headless = LaunchConfiguration("headless")
    ros_control_file = LaunchConfiguration("ros_control_file")
    world_init_x = LaunchConfiguration("world_init_x")
    world_init_y = LaunchConfiguration("world_init_y")
    world_init_z = LaunchConfiguration("world_init_z")
    world_init_heading = LaunchConfiguration("world_init_heading")
    gazebo_world = LaunchConfiguration("world")
    skip_robot_state_publisher = LaunchConfiguration("skip_robot_state_publisher")
    
    gz_pkg_share = launch_ros.substitutions.FindPackageShare(package="champ_gazebo").find(
        "champ_gazebo"
    )

    declare_robot_name = DeclareLaunchArgument("robot_name", default_value="go2")
    declare_use_sim_time = DeclareLaunchArgument("use_sim_time", default_value="True")
    declare_headless = DeclareLaunchArgument("headless", default_value="False")
    declare_skip_robot_state_publisher = DeclareLaunchArgument(
        "skip_robot_state_publisher", default_value="False",
        description="Skip robot_state_publisher if already launched elsewhere"
    )
    declare_ros_control_file = DeclareLaunchArgument(
        "ros_control_file",
        default_value=os.path.join(gz_pkg_share, "config/ros_control.yaml"),
    )
    declare_gazebo_world = DeclareLaunchArgument(
        "world", default_value=os.path.join(gz_pkg_share, "worlds/default.sdf")
    )
    declare_world_init_x = DeclareLaunchArgument("world_init_x", default_value="0.0")
    declare_world_init_y = DeclareLaunchArgument("world_init_y", default_value="0.0")
    declare_world_init_z = DeclareLaunchArgument("world_init_z", default_value="0.8")
    declare_world_init_heading = DeclareLaunchArgument(
        "world_init_heading", default_value="0.0"
    )

    pkg_share = launch_ros.substitutions.FindPackageShare(package="champ_description").find("champ_description")
    default_model_path = os.path.join(pkg_share, "urdf/champ.urdf.xacro")

    declare_description_path = DeclareLaunchArgument(
        name="description_path", 
        default_value=default_model_path, 
        description="Absolute path to robot urdf file"
    )

    declare_description_args = DeclareLaunchArgument(
        name="description_args",
        default_value="",
        description="Extra xacro arguments for the description, e.g. 'laser:=true'",
    )

    config_pkg_share = launch_ros.substitutions.FindPackageShare(
        package="champ_config"
    ).find("champ_config")
    
    links_config = os.path.join(config_pkg_share, "config/links/links.yaml")
    
    # Set ignition resource path for models
    ign_resource_path = SetEnvironmentVariable(
        name='IGN_GAZEBO_RESOURCE_PATH',
        value=[
            os.path.join(gz_pkg_share, 'worlds'), ':',
            os.path.join(gz_pkg_share, 'models'), ':',
            '/usr/share/ignition/ignition-gazebo6/worlds'
        ]
    )

    # Start Ignition Gazebo with the world file
    # Use 'ign gazebo' for Ignition Fortress, or 'gz sim' for newer versions
    start_ignition_cmd = ExecuteProcess(
        cmd=['ign', 'gazebo', '-r', gazebo_world,
             '--render-engine', 'ogre2'],
        output='screen',
        condition=IfCondition(PythonExpression(['not ', headless])),
    )
    
    start_ignition_headless_cmd = ExecuteProcess(
        cmd=['ign', 'gazebo', '-r', '-s', gazebo_world],
        output='screen',
        condition=IfCondition(headless),
    )

    # Robot description
    robot_description = {"robot_description": Command(["xacro ", LaunchConfiguration("description_path"), " ", LaunchConfiguration("description_args")])}

    # Robot state publisher (skip if already launched by parent launch file)
    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="screen",
        parameters=[robot_description, {"use_sim_time": use_sim_time}],
        condition=IfCondition(PythonExpression(['not ', skip_robot_state_publisher])),
    )

    # Spawn robot in Ignition using ros_gz_sim
    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-name', robot_name,
            '-allow_renaming', 'true',
            '-topic', '/robot_description',
            '-x', world_init_x,
            '-y', world_init_y,
            '-z', world_init_z,
            '-Y', world_init_heading,
        ],
        output='screen',
    )

    # Bridge for clock (Ignition -> ROS2)
    clock_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=['/clock@rosgraph_msgs/msg/Clock[ignition.msgs.Clock'],
        output='screen',
    )

    # Bridge for IMU data
    imu_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=['/imu/data@sensor_msgs/msg/Imu[ignition.msgs.IMU'],
        output='screen',
    )

    # Bridge for laser scan
    scan_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=['/scan@sensor_msgs/msg/LaserScan[ignition.msgs.LaserScan'],
        output='screen',
    )

    # Bridge for Velodyne point cloud (Ignition publishes to /velodyne_points/points)
    velodyne_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=['/velodyne_points/points@sensor_msgs/msg/PointCloud2[ignition.msgs.PointCloudPacked'],
        output='screen',
        remappings=[('/velodyne_points/points', '/velodyne_points')],
    )

    # Load joint state broadcaster (with delay to wait for controller_manager)
    load_joint_state_controller = TimerAction(
        period=5.0,
        actions=[ExecuteProcess(
            cmd=['ros2', 'control', 'load_controller', '--set-state', 'active',
                 'joint_states_controller'],
            output='screen',
        )],
    )

    # Load joint effort controller (with delay to wait for controller_manager)
    load_joint_trajectory_effort_controller = TimerAction(
        period=6.0,
        actions=[ExecuteProcess(
            cmd=['ros2', 'control', 'load_controller', '--set-state', 'active',
                 'joint_group_effort_controller'],
            output='screen'
        )],
    )

    return LaunchDescription(
        [
            declare_robot_name,
            declare_use_sim_time,
            declare_headless,
            declare_skip_robot_state_publisher,
            declare_ros_control_file,
            declare_gazebo_world,
            declare_world_init_x,
            declare_world_init_y,
            declare_world_init_z,
            declare_world_init_heading,
            declare_description_path,
            declare_description_args,
            ign_resource_path,
            start_ignition_cmd,
            start_ignition_headless_cmd,
            robot_state_publisher,
            spawn_robot,
            clock_bridge,
            imu_bridge,
            scan_bridge,
            velodyne_bridge,
            load_joint_state_controller,
            load_joint_trajectory_effort_controller,
        ]
    )
