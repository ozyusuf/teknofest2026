#!/usr/bin/env python3
"""cmd_vel -> vehicle_cmd mock CAN bridge (Bee 1)."""

import math

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray


class VehicleInterfaceNode(Node):
    def __init__(self):
        super().__init__('vehicle_interface_node')

        # Bee 1 fiziksel parametreleri (hazir arac bilgilendirme PDF)
        self.wheelbase = 1.86
        self.max_steering_angle = math.radians(32.5)
        self.max_accel = 2.5
        self.max_decel = -6.5
        self.deadband = 0.2

        self.cmd_vel_sub = self.create_subscription(
            Twist, '/cmd_vel', self.cmd_vel_callback, 10
        )
        self.vehicle_cmd_pub = self.create_publisher(
            Float64MultiArray, '/vehicle_cmd', 10
        )

        self.get_logger().info('Vehicle Interface Node baslatildi (MOCK CAN bridge)')
        self.get_logger().info(
            f'  Dingil: {self.wheelbase} m, '
            f'Max direksiyon: {math.degrees(self.max_steering_angle):.1f} deg'
        )

    def cmd_vel_callback(self, msg: Twist):
        v = msg.linear.x
        omega = msg.angular.z

        # Kinematic bicycle inverse: delta = atan2(L*omega, |v|)
        if abs(v) > 0.01:
            steering = math.atan2(self.wheelbase * omega, abs(v))
        else:
            steering = 0.0
        steering = max(
            -self.max_steering_angle, min(self.max_steering_angle, steering)
        )

        # Mock: linear.x'i ivme komutu kabul et. Gercek aracta hiz->PID->throttle/brake.
        accel_cmd = v
        if accel_cmd > self.deadband:
            throttle = min(accel_cmd / self.max_accel, 1.0)
            brake = 0.0
        elif accel_cmd < -self.deadband:
            throttle = 0.0
            brake = min(abs(accel_cmd) / abs(self.max_decel), 1.0)
        else:
            throttle = 0.0
            brake = 0.0

        out = Float64MultiArray()
        out.data = [throttle, brake, steering]
        self.vehicle_cmd_pub.publish(out)


def main(args=None):
    rclpy.init(args=args)
    node = VehicleInterfaceNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
