#!/usr/bin/env python3
"""Bee 1 sensor frame'lerini TF agacina yayinlar.

Referans: hazir_arac_bilgilendirme.pdf, Sensor ve Arac Bilgisayari
Yerlesimleri tablosu. Tum olculer 'on aks merkezi' referansli;
base_link = on aks merkezi varsayimi.
"""

import rclpy
from geometry_msgs.msg import TransformStamped
from rclpy.node import Node
from tf2_ros import StaticTransformBroadcaster


class StaticTFPublisher(Node):
    def __init__(self):
        super().__init__('static_tf_publisher')
        self.broadcaster = StaticTransformBroadcaster(self)

        # PDF teyitli ofsetler (metre)
        sensors = [
            {'frame': 'velodyne',           'x': -0.177, 'y':  0.000, 'z': 0.620},
            {'frame': 'zed2_left',          'x': -0.205, 'y': -0.060, 'z': 0.685},
            {'frame': 'zed2_right',         'x': -0.205, 'y':  0.060, 'z': 0.685},
            {'frame': 'zed2_camera_center', 'x': -0.205, 'y':  0.000, 'z': 0.685},
            {'frame': 'gps_imu',            'x':  1.440, 'y':  0.000, 'z': 1.390},
        ]

        transforms = []
        for s in sensors:
            t = TransformStamped()
            t.header.stamp = self.get_clock().now().to_msg()
            t.header.frame_id = 'base_link'
            t.child_frame_id = s['frame']
            t.transform.translation.x = s['x']
            t.transform.translation.y = s['y']
            t.transform.translation.z = s['z']
            t.transform.rotation.x = 0.0
            t.transform.rotation.y = 0.0
            t.transform.rotation.z = 0.0
            t.transform.rotation.w = 1.0
            transforms.append(t)

        self.broadcaster.sendTransform(transforms)
        self.get_logger().info(f'{len(transforms)} static transform yayinlandi')
        for s in sensors:
            self.get_logger().info(
                f'  base_link -> {s["frame"]}: '
                f'x={s["x"]:.3f} y={s["y"]:.3f} z={s["z"]:.3f}'
            )


def main(args=None):
    rclpy.init(args=args)
    node = StaticTFPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
