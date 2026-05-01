# ============================================================
# MSKÜ-ROTA Robotaksi ROS 2 Humble Geliştirme Container'ı
# Hedef: Bee 1 hazır araç (Ubuntu 20.04 host) + geliştirme PC'leri
# ============================================================
FROM osrf/ros:humble-desktop

ENV DEBIAN_FRONTEND=noninteractive
ENV ROS_DOMAIN_ID=42
ENV RMW_IMPLEMENTATION=rmw_cyclonedds_cpp

# Temel paketler + ROS 2 ekleri
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    git \
    curl \
    wget \
    vim \
    nano \
    htop \
    python3-pip \
    python3-colcon-common-extensions \
    python3-rosdep \
    python3-vcstool \
    ros-humble-rmw-cyclonedds-cpp \
    ros-humble-navigation2 \
    ros-humble-nav2-bringup \
    ros-humble-robot-localization \
    ros-humble-behaviortree-cpp-v3 \
    ros-humble-tf2-tools \
    ros-humble-rqt \
    ros-humble-rqt-common-plugins \
    ros-humble-rviz2 \
    python3-numpy \
    python3-scipy \
    python3-matplotlib \
    && rm -rf /var/lib/apt/lists/*

# Python paketleri (apt'ta olmayanlar)
RUN pip3 install --no-cache-dir osqp

# Workspace
RUN mkdir -p /root/ros2_ws/src
WORKDIR /root/ros2_ws

# Shell yapılandırması
RUN echo "source /opt/ros/humble/setup.bash" >> /root/.bashrc \
    && echo "[ -f /root/ros2_ws/install/setup.bash ] && source /root/ros2_ws/install/setup.bash" >> /root/.bashrc \
    && echo "export ROS_DOMAIN_ID=42" >> /root/.bashrc \
    && echo "export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp" >> /root/.bashrc

CMD ["bash"]
