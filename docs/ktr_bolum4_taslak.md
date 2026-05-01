# Bölüm 4 — Hazır Araç Özellikleri ve Analizi (TASLAK)

> **Kapsam:** Bu bölüm, MSKÜ-ROTA takımının yarışmada kullanacağı **Bee 1**
> hazır araç platformunu (Beemobs L7e-CU) analiz eder. Geliştirme PC'leri
> bu bölümün kapsamı dışındadır; bunlar Ek/Setup Rehberi'nde belgelenir.
>
> **Kaynak:** `docs/reference/robotaksi_hazir_araç_bilgilendirme.pdf`
> (TEKNOFEST 2026 Robotaksi-Binek Otonom Araç Yarışması).

---

## 4.1 Fiziksel ve Dinamik Parametreler

| Parametre                    | Değer                          |
|------------------------------|--------------------------------|
| Üretici / Model              | Beemobs / Bee 1 (L7e-CU)       |
| Uzunluk                      | 2740 mm                        |
| Genişlik                     | 1060 mm                        |
| Yükseklik                    | 1785 mm                        |
| Dingil mesafesi              | 1860 mm                        |
| Ön iz / Arka iz genişliği    | 886 mm / 850 mm                |
| Boş ağırlık                  | 760 kg (Ön: 324, Arka: 436)    |
| Sürücülü ağırlık             | 835 kg                         |
| Maksimum yüklü ağırlık       | 1000 kg                        |
| Lastik                       | 145/70 R13 (155/65 R13 alternatif) |
| Max iç teker dönüş açısı     | 32.5°                          |
| Max dış teker dönüş açısı    | 30.0°                          |
| Dönüş yarıçapı (kald.)       | 4025 mm                        |
| Maksimum hız                 | 55 km/sa (yarışmada **30 km/sa** ile yazılım limiti) |
| Maksimum hızlanma ivmesi     | 2.5 m/s²                       |
| Maksimum yavaşlama ivmesi    | 6.5 m/s²                       |
| Çekiş tipi                   | Arkadan itişli (PMSM)          |
| Direksiyon tipi              | Kremayer, elektrik destekli    |

**Yorum.** Kinematik bicycle modelinde dingil L = 1.86 m; yarışmada
limitlenmiş tepe hızda ω_max ≈ v · tan(32.5°) / L = 8.33 · 0.637 / 1.86 ≈
**2.85 rad/s**. Bu, sıkı dönüşler dahil tüm yarışma manevraları için yeterli
yanal hareketliliği sağlar.

---

## 4.2 Fren Mesafesi Aritmetiği — 30 km/sa

Algı→karar→aktüatör zincirinde reaksiyon süresi tahmini:

| Aşama                                  | Süre (ms) |
|----------------------------------------|-----------|
| Sensör frame yakalama (LiDAR/Kamera)   | ~50–100   |
| Algılama (YOLO TensorRT FP16)          | ~50–80    |
| Behavior Tree karar                    | ~20       |
| CAN aktarımı + fren aktüatör tepkisi   | ~100–200  |
| **Toplam reaksiyon süresi**            | **≈ 400** |

v₀ = 30 km/sa = 8.33 m/s.

| Senaryo                | Reaksiyon mesafesi | Frenleme mesafesi (v²/2a) | **Toplam** |
|------------------------|--------------------|---------------------------|------------|
| Kuru asfalt (a = 6.5)  | 8.33·0.4 = **3.33 m** | 8.33² / (2·6.5) = **5.34 m** | **≈ 8.7 m** |
| Islak asfalt (a ≈ 3.7)¹| 3.33 m              | 8.33² / (2·3.7) = 9.38 m  | **≈ 12.7 m** |

¹ Lastik-zemin µ kuru→ıslak için ~0.85→0.55 oranıyla düşürüldü; Bee 1 için
gerçek pist testi sonrası kalibre edilecek.

**Yorum.** En kötü durumda (ıslak zemin) 13 m'lik durdurma mesafesi, BT
karar katmanında tehlike algılandığında **fren komutunu en az 13 m önce**
vermek gerektiğini söyler. Bu, planlama horizonu için alt sınırdır.

---

## 4.3 Otonom Donanım Paketi

| Bileşen          | Model                              |
|------------------|------------------------------------|
| LiDAR            | Velodyne **VLP16** (16 kanal, 360° yatay, ~15° dikey FoV) |
| Kamera           | **ZED2** Stereo (RGB + derinlik + VIO) |
| GPS/IMU          | XSENS **MTI-680-DK** (RTK **YOK**) |
| Araç Bilgisayarı | ADVANTECH 770H + MIC-75G20         |
| GPU              | **RTX 3060** (VRAM: PDF'de yazmıyor — **Beemobs/Advantech'e teyit ettirilecek**; muhtemel: 6 GB) |
| WiFi             | WAVLINK AC1200 (2.4 + 5 GHz, 1.2 Gbps) |
| Fren aktüatörü   | Enkoderli step motor 86BHH114-450p-40Mp + 1:5 sonsuz redüktör |
| İletişim         | CANBus                             |
| Host OS          | Ubuntu 20.04 (ROS1 veya ROS2)      |

### 4.3.1 Tek Hata Noktası (SPoF) Analizi

- **RADAR yok.** Kötü hava (sis/yoğun yağmur) durumunda kamera + LiDAR
  performansı düşer; redundancy yoktur.
- **RTK yok.** GPS/IMU çıkışı standart konumlamada metre seviyesi hata
  verebilir. Yarışma içinde NDT/AMCL ile LiDAR tabanlı yer-bağıntılı
  konumlama bu açığı kapatmalıdır.
- **LiDAR + Kamera birlikte SPoF.** İkisi de görüş hattı tabanlı; kapalı
  bagaj alanı veya direkt güneş yansıması her ikisini de etkileyebilir.
  BT katmanında **CheckLocalization** ve **CheckSensors** node'larıyla
  dejenerasyon tespit edilip SafeStop tetiklenmelidir.

---

## 4.4 VRAM Bütçesi — RTX 3060 (Konservatif: 6 GB)

> Bee 1 GPU'sunun VRAM'i PDF'de belirtilmemiştir. Aşağıdaki tablo **6 GB
> konservatif** varsayımına göredir; gerçek değer Beemobs/Advantech'ten
> teyit edildiğinde güncellenecektir.

| Bileşen                     | Min (MB) | Max (MB) |
|-----------------------------|---------:|---------:|
| CUDA context                |      300 |      500 |
| ZED2 SDK (HD720)            |     1500 |     2500 |
| YOLO TensorRT FP16          |      400 |      700 |
| NDT matching (LiDAR-harita) |      200 |      400 |
| ROS 2 + TRT workspace       |      100 |      300 |
| **Toplam**                  | **2500** | **4400** |

**Tampon:** 6 GB toplamda min 1.6 GB (max 3.5 GB) boş alan kalır → kabul
edilebilir. Eğer GPU 12 GB çıkarsa tampon iki katına çıkar; ek olarak SAM
benzeri ağır segmentasyon modülleri eklenebilir.

---

## 4.5 Güç ve Termal Bütçe

### 4.5.1 Güç

- Ana batarya: 76.8 V (60–88 V), LFP, 8 saat çalışma süresi (220 Vac /
  25 A / 5 saat şarj).
- Aksesuar gerilimi: 12 V (DC-DC dönüştürücü ile).
- Otonom paket tepe gücü tahmini:
  - Advantech 770H + MIC-75G20: ~150–200 W
  - RTX 3060: ~115–170 W
  - VLP16: ~8 W
  - ZED2: ~2 W (USB)
  - XSENS MTI-680-DK: ~1 W
  - **Toplam tepe**: ~300–400 W
- 12 V hattan çekiş: 400 W / 12 V ≈ 33 A → DC-DC dönüştürücü en az
  **40 A** kapasiteli olmalı (güvenlik payıyla).

### 4.5.2 Termal — Kritik Risk

- **Bee 1'de iklimlendirme YOK** (PDF, sayfa 3: "İklimlendirme Sistemi: --").
- Kapalı kasada GPU/CPU pasif soğutma yetersiz kalabilir → **thermal
  throttle** riski.
- **Mitigasyon planı:**
  1. Otonom kabin tarafında ek bir *forced-air* fan (12 V, ≥80 CFM).
  2. Yaz koşullarında batarya bölmesi havalandırma ızgaraları açık.
  3. `nvidia-smi` ile GPU sıcaklığı monitör edilip 85 °C üstünde BT'de
     **performans kademesi düşür** (örn. detection rate 30 → 15 Hz).
  4. Pist günü direkt güneş altında çalışmadan önce 10 dk düşük yük
     ısınma turu (sıcaklık trendini izlemek için).

---

## 4.6 Yazılım Uyumluluk Notu

- Bee 1 host OS = Ubuntu 20.04 (PDF teyitli).
- Geliştirme stack'ı = ROS 2 **Humble** (Ubuntu 22.04 isteyen).
- **Çözüm:** Tüm uygulama `osrf/ros:humble-desktop` Docker container'ında
  paketlenir. Bee 1 host'unda yalnızca:
  - Docker Engine
  - **nvidia-container-toolkit** (yarışma günü öncesi mutlaka kurulu/test
    edilmiş olmalı)
  - CycloneDDS RMW + UDP multicast izinleri
- Container ile aynı image hem geliştirme PC'lerinde hem Bee 1'de çalışır →
  reproducibility.

---

## 4.7 Açık Sorular / Eylem Maddeleri

1. ☐ **Bee 1 GPU VRAM'i 6 GB mı 12 GB mı?** (Beemobs/Advantech'e e-posta)
2. ☐ Bee 1 12 V hattının sürekli akım kapasitesi nedir? (Otonom paket
   yüküyle uyumlu mu?)
3. ☐ Pist günü ortam sıcaklığı tahmini? (Yaz şartlarında termal mitigasyon
   yeterli mi?)
4. ☐ CAN bus mesaj tanımları (DBC dosyası) Beemobs'tan resmi olarak
   alınacak.
5. ☐ Acil durdurma (Emergency Stop) devresi BT/SafeStop ile entegrasyonu
   nasıl olacak? (PDF sayfa 6 elektrik şeması üzerinden)
