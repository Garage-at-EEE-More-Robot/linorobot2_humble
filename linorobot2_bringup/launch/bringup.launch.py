# Copyright (c) 2021 Juan Miguel Jimeno
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http:#www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution, PythonExpression
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch.conditions import IfCondition, UnlessCondition


def generate_launch_description():
    sensors_launch_path = PathJoinSubstitution(
        [FindPackageShare('linorobot2_bringup'), 'launch', 'sensors.launch.py']
    )

    joy_launch_path = PathJoinSubstitution(
        [FindPackageShare('linorobot2_bringup'), 'launch', 'joy_teleop.launch.py']
    )

    description_launch_path = PathJoinSubstitution(
        [FindPackageShare('linorobot2_description'), 'launch', 'description.launch.py']
    )

    ekf_config_path = PathJoinSubstitution(
        [FindPackageShare("linorobot2_base"), "config", "ekf.yaml"]
    )

    default_robot_launch_path = PathJoinSubstitution(
        [FindPackageShare('linorobot2_bringup'), 'launch', 'default_robot.launch.py']
    )

    custom_robot_launch_path = PathJoinSubstitution(
        [FindPackageShare('linorobot2_bringup'), 'launch', 'custom_robot.launch.py']
    )

    extra_launch_path = PathJoinSubstitution(
        [FindPackageShare('linorobot2_bringup'), 'launch', 'extra.launch.py']
    )

    #This node publishes the static transform between the robot's base and the IMU
    global_to_odom_node = Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='global_to_odom_static_publisher',
            arguments=[
                # Replace with your measured offsets from base_link to imu
                '--x', '0.0',      # in meters
                '--y', '0.0',      # in meters
                '--z', '0.0',      # in meters
                # Replace with your measured rotation (in radians)
                # '--roll', '1.57',
                # '--pitch', '0.0',
                # '--yaw', '1.57',
                '--qx', '0.5',
		        '--qy', '-0.5',
		        '--qz', '0.5',
		        '--qw', '0.5',
                # The parent frame
                '--frame-id', 'global',
                # The child frame
                '--child-frame-id', 'odom'
            ]
    )
    
    #This node publishes the static transform between the robot's base and the IMU
    base_to_imu_node = Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='base_to_imu_static_publisher',
            arguments=[
                # Replace with your measured offsets from base_link to imu
                '--x', '0.105',      # in meters
                '--y', '0.0',      # in meters
                '--z', '0.1',      # in meters
                # Replace with your measured rotation (in radians)
                '--roll', '0.0',
                '--pitch', '0.0',
                '--yaw', '0.0',
                # '--qx', '0.5',
		        # '--qy', '-0.5',
		        # '--qz', '0.5',
		        # '--qw', '0.5',

		        # The parent frame
                '--frame-id', 'base_footprint',
                # The child frame
                '--child-frame-id', 'ov_imu'
            ]
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            name='custom_robot', 
            default_value='false',
            description='Use custom robot'
        ),

        DeclareLaunchArgument(
            name='extra', 
            default_value='false',
            description='Launch extra launch file'
        ),

        DeclareLaunchArgument(
            name='base_serial_port', 
            default_value='/dev/ttyUSB0',
            description='Linorobot Base Serial Port'
        ),

        DeclareLaunchArgument(
            name='micro_ros_transport',
            default_value='serial',
            description='micro-ROS transport'
        ),

        DeclareLaunchArgument(
            name='micro_ros_port',
            default_value='8888',
            description='micro-ROS udp/tcp port number'
        ),

        DeclareLaunchArgument(
            name='odom_topic', 
            default_value='/odom',
            description='EKF out odometry topic'
        ),

        DeclareLaunchArgument(
            name='madgwick',
            default_value='false',
            description='Use madgwick to fuse imu and magnetometer'
        ),

        DeclareLaunchArgument(
            name='orientation_stddev',
            default_value='0.003162278',
            description='Madgwick orientation stddev'
        ),

        DeclareLaunchArgument(
            name='joy', 
            default_value='false',
            description='Use Joystick'
        ),

        Node(
            condition=IfCondition(LaunchConfiguration("madgwick")),
            package='imu_filter_madgwick',
            executable='imu_filter_madgwick_node',
            name='madgwick_filter_node',
            output='screen',
            parameters=[{
                'orientation_stddev' : LaunchConfiguration('orientation_stddev'),
                'publish_tf' : False
            }]
        ),

        #static tf publisher from base_footprint to imu
        # global_to_odom_node,
        # base_to_imu_node,

        Node(
            package='robot_localization',
            executable='ekf_node',
            name='ekf_filter_node',
            output='screen',
            parameters=[
                ekf_config_path
            ],
            remappings=[("odometry/filtered", LaunchConfiguration("odom_topic"))]
        ),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(default_robot_launch_path),
            condition=UnlessCondition(LaunchConfiguration("custom_robot")),
            launch_arguments={
                'base_serial_port': LaunchConfiguration("base_serial_port")
            }.items()
        ),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(extra_launch_path),
            condition=IfCondition(LaunchConfiguration("extra")),
        ),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(custom_robot_launch_path),
            condition=IfCondition(LaunchConfiguration("custom_robot")),
        ),

        
    ])
