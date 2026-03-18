import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.conditions import IfCondition
from launch_ros.substitutions import FindPackageShare
from launch_ros.actions import Node

def generate_launch_description():

    laser_filter_config_path = PathJoinSubstitution(
        [FindPackageShare("linorobot2_navigation"), "config", "angular_filter_config.yaml"]
    )

    return LaunchDescription([
        #test laser filter
        Node(
            package="laser_filters",
            executable="scan_to_scan_filter_chain",
            remappings=[('scan','scan_unfiltered'), ('scan_filtered','scan')]
            parameters=[
                laser_filter_config_path,
                ]),

    ])
