# MSKÜ-ROTA Geliştirme Ortamı Kurulum Rehberi

Bu rehber **geliştirme PC'leri** içindir. Bee 1 hazır araç host'u Ubuntu
20.04 olsa da, container yaklaşımı sayesinde aynı image her iki ortamda
çalışır.

## Gereksinimler

| Bileşen | Sürüm |
|---------|-------|
| OS | Ubuntu 20.04 / 22.04 / 24.04 |
| NVIDIA Driver | ≥ 525 (CUDA 12.x desteği için) |
| Docker Engine | ≥ 24 |
| Docker Compose | ≥ v2 |
| nvidia-container-toolkit | en güncel |
| Git | ≥ 2.30 |
| GitHub erişimi | gh CLI HTTPS token VEYA SSH key |

## İlk kurulum (sıfırdan)

### 1) NVIDIA Container Toolkit

```bash
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | \
  sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg

curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
  sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
  sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

sudo systemctl stop packagekit  # apt lock'u tutuyorsa
sudo apt update
sudo apt install -y nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker

# Doğrulama
docker run --rm --gpus all nvidia/cuda:12.2.0-base-ubuntu22.04 nvidia-smi
```

### 2) Repo + submodule

```bash
git clone https://github.com/ozyusuf/teknofest2026.git
cd teknofest2026
git submodule update --init --recursive
```

### 3) Container'ı build et ve başlat

```bash
cd docker
docker compose build       # ilk seferde 5–15 dk
docker compose up -d
```

### 4) Container içinde workspace build

```bash
docker exec -it rota-dev bash
# container içinde:
source /opt/ros/humble/setup.bash
cd /root/ros2_ws
colcon build
source install/setup.bash
```

## Doğrulama Testleri

Container içinde:

```bash
# Test 1: GPU görünüyor mu
nvidia-smi

# Test 2: ROS 2 talker
ros2 run demo_nodes_cpp talker          # Ctrl+C

# Test 3: Nav2 + BT.CPP paketleri kurulu mu
ros2 pkg list | grep -E "nav2|behaviortree" | head -10

# Test 4: rota_bringup launch
ros2 launch rota_bringup bringup.launch.py profile:=sim

# Test 5: vehicle_interface (mock CAN bridge)
ros2 run rota_vehicle_interface vehicle_interface_node &
ros2 topic pub --rate 10 /cmd_vel geometry_msgs/msg/Twist \
  '{linear: {x: 2.0}, angular: {z: 0.3}}' &
ros2 topic echo /vehicle_cmd

# Test 6: static TF
ros2 run rota_tf_publisher static_tf_node &
ros2 topic echo --once /tf_static | grep child_frame_id
# velodyne, zed2_left, zed2_right, zed2_camera_center, gps_imu

# Test 7: BT.CPP
ros2 run rota_bt rota_bt_node
# "BT tick #50", "#100" loglarını görmelisin (50 Hz)
```

## Günlük Kullanım

```bash
# Container çalışıyor mu kontrol
docker ps | grep rota-dev

# Çalışmıyorsa başlat
cd <repo>/docker && docker compose up -d

# Container'a gir
docker exec -it rota-dev bash

# Workspace build
cd /root/ros2_ws && colcon build --symlink-install
source install/setup.bash
```

## Sık Karşılaşılan Sorunlar

### `apt update` "Could not get lock"

`packagekitd` arkaplanda apt lock'u tutuyor olabilir.

```bash
sudo systemctl stop packagekit
sudo apt update
```

### `docker run --gpus all` "no known GPU vendor"

`nvidia-container-toolkit` kurulu değil veya `nvidia-ctk runtime configure`
çalıştırılmamış. Kurulum bölümündeki 1. adımı tekrar uygula.

### `pip3 install --break-system-packages` hatası

Bu flag Python 3.11+ ile geldi. Dockerfile içinde Ubuntu 22.04 / Python
3.10 kullanıyoruz; gerekli paketleri **apt ile** (`python3-numpy`,
`python3-scipy`, `python3-matplotlib`) kuruyoruz; sadece `osqp` pip'ten
geliyor.

### Container içinde dosya sahipliği "root"

Container varsayılan olarak root kullanıcısıyla çalışıyor; bind-mounted
dosyalar root'a ait olarak yansıyor. Host'tan düzenleme yapmak için:

```bash
docker exec rota-dev chown -R $(id -u):$(id -g) /root/ros2_ws/src
```

(Yarışma sonrası `docker-compose.yml`'a kullanıcı mapping ekleyebiliriz.)

### Submodule eksik

```bash
git submodule update --init --recursive
```

## Bee 1 Host'unda Çalıştırma (yarışma günü)

Bee 1 host'u Ubuntu 20.04 üstünde çalışır. Adımlar farklı değildir:

1. Bee 1'de Docker + nvidia-container-toolkit kurulu olmalı (yarışma günü
   öncesi mutlaka test edilsin).
2. Repo + submodule clone.
3. `docker compose build && docker compose up -d`.
4. Container içinde aynı testler çalışır.

**Kritik:** İklimlendirme yok → uzun süreli yüksek yük öncesi GPU sıcaklığı
izlenmeli (`nvidia-smi -l 1`).
