# OrangeFox / TWRP Device Tree for vivo X300 Pro (PD2502 / V2514)

## Device Specifications
- **Brand:** vivo
- **Model:** vivo X300 Pro (PD2502F_EX / V2514)
- **SoC:** MediaTek Dimensity 9500 (MT6993)
- **Kernel:** Linux 6.12.x GKI (ARM64-v8a)
- **Display:** 1260 x 2800 AMOLED, ~520 DPI
- **Android Base:** OriginOS 6 (Android 16, API 36)
- **Recovery Architecture:** Virtual A/B (Boot Header v4). Recovery ramdisk is located in `vendor_boot`.

---

## Partition Architecture & Layout
Modern MediaTek flagships (Dimensity 9300/9400/9500) do NOT have a separate `/recovery` partition.
Instead:
- `boot.img`: Generic Kernel Image (`kernel`).
- `init_boot.img`: Generic first-stage ramdisk.
- `vendor_boot.img`: Device Tree Blob (`dtb`), `bootconfig`, platform vendor ramdisk, and the **recovery ramdisk** (`type=[recovery]`).
- `super.img`: Dynamic logical partitions (`system`, `system_ext`, `vendor`, `product`, `odm`, `vendor_dlkm`, `cust`, `vgc`).
- `userdata`: F2FS with Dual UFS RAID mapper (`userdata_setup` -> `/dev/block/mapper/mtk_userdata`) and FBEv2 inlinecrypt (`aes-256-xts:aes-256-cts:v2+inlinecrypt_optimized`).

---

## Building OrangeFox Recovery

### 1. Set Up the OrangeFox Build Environment
Sync an OrangeFox source manifest supporting Android 14+ or 15+ (e.g. `fox_14.1` or newer):
```bash
mkdir -p ~/OrangeFox && cd ~/OrangeFox
repo init --depth=1 -u https://gitlab.com/OrangeFox/manifest.git -b fox_14.1
repo sync -c -j$(nproc --all) --force-sync --no-clone-bundle --no-tags
```

### 2. Copy the Device Tree
Clone or copy this folder to `device/vivo/PD2502`:
```bash
cp -r /path/to/device_vivo_PD2502 ~/OrangeFox/device/vivo/PD2502
```

### 3. Build OrangeFox
```bash
cd ~/OrangeFox
source build/envsetup.sh
source device/vivo/PD2502/vendorsetup.sh
lunch fox_PD2502-eng
mka recoveryimage -j$(nproc --all)
```

The output will be generated in `out/target/product/PD2502/vendor_boot.img` and `OrangeFox-*.zip`.

---

## Flashing Instructions

Because recovery is integrated into `vendor_boot`:
```bash
adb reboot bootloader
fastboot flash vendor_boot vendor_boot.img
fastboot reboot recovery
```

> **Warning:** Always keep a backup of your stock `boot_a.bin`, `init_boot_a.bin`, and `vendor_boot_a.bin` before testing!
