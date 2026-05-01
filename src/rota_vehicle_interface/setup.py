from setuptools import find_packages, setup

package_name = 'rota_vehicle_interface'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='rota',
    maintainer_email='rota@msku.edu.tr',
    description='Mock CAN bridge: cmd_vel to vehicle commands',
    license='MIT',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'vehicle_interface_node = rota_vehicle_interface.vehicle_interface_node:main',
        ],
    },
)
