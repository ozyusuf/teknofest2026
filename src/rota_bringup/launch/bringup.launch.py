import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration

def generate_launch_description():
    profile_arg = DeclareLaunchArgument(
        'profile',
        default_value='sim',
        description='Parametre profili: sim veya real'
    )

    return LaunchDescription([
        profile_arg,
        # Node'lar ileriki adimlarda eklenir
    ])
