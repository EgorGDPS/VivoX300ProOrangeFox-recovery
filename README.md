# OrangeFox / TWRP Device Tree for vivo X300 Pro (PD2502 / V2514)

# WARNING MOST THINGS ARE UNTESTED AND CAN BREAK

## Device Specifications
- **Brand:** vivo
- **Model:** vivo X300 Pro (PD2502F_EX / V2514)
- **SoC:** MediaTek Dimensity 9500 (MT6993)
- **Kernel:** Linux 6.12.x GKI (ARM64-v8a)
- **Display:** 1260 x 2800 AMOLED, ~520 DPI
- **Android Base:** OriginOS 6 (Android 16, API 36)
- **Recovery Architecture:** Virtual A/B (Boot Header v4). Recovery ramdisk is located in `vendor_boot`.

---

## Current Status & Working Features
- [x] **Native OLED Display:** 1260 x 2800 resolution with functional brightness control.
- [x] **Touchscreen (Out-of-the-box):** Goodix GT9916 (`/dev/vts_thp0`, `/dev/input/event4`) managed by supervisor service and userland `vtsthp`.
- [x] **Haptics:** Linear Resonant Actuator (LRA) feedback enabled.
- [x] **Dynamic Partitions:** All 8 logical partitions (`system_root`, `system_ext`, `vendor`, `product`, `odm`, `vendor_dlkm`, `odm_dlkm`, `system_dlkm`) mapped and mountable via GUI and CLI.
- [x] **ADB Sideload:** Full ConfigFS USB gadget state machine for `sideload` and `adb`.
- [x] **ZIP Flashing:** Supported with `/cache -> /tmp` RAM staging and `$PATH` integration for encrypted userdata.
- [x] **ADB & MTP:** Functional USB modes in recovery.

---

## Partition Architecture & Layout
- `boot.img`: Generic Kernel Image (`kernel`).
- `init_boot.img`: Generic first-stage ramdisk (root target for Magisk).
- `vendor_boot.img`: Device Tree Blob (`dtb`), `bootconfig`, platform vendor ramdisk, and the **recovery ramdisk** (`type=[recovery]`).
- `super.img`: Dynamic logical partitions (`system`, `system_ext`, `vendor`, `product`, `odm`, `vendor_dlkm`, `cust`, `vgc`).
- `userdata`: F2FS with Dual UFS RAID mapper (`userdata_setup` -> `/dev/block/mapper/mtk_userdata`) and FBEv2 inlinecrypt (`aes-256-xts:aes-256-cts:v2+inlinecrypt_optimized`).

---

## Building Recovery Image

### Method 1: Standalone Perfect Assembly (Recommended)
You can directly assemble the tested, verified vendor_boot recovery image using the included script:
```bash
python3 assemble_perfect_recovery.py
```
This unpacks the base recovery ramdisk, injects the Goodix touch daemon and libraries, sets non-blocking `/vendor` symlinks, patches `init.rc` for `/cache -> /tmp`, configures ConfigFS USB triggers, and packs the final `vendor_boot` header v4 image.

### Method 2: OrangeFox Build Environment
Sync an OrangeFox source manifest supporting Android 14+ or 15+ (e.g. `fox_14.1` or newer):
```bash
mkdir -p ~/OrangeFox && cd ~/OrangeFox
repo init --depth=1 -u https://gitlab.com/OrangeFox/manifest.git -b fox_14.1
repo sync -c -j$(nproc --all) --force-sync --no-clone-bundle --no-tags
```

Copy this repository to `device/vivo/PD2502` and build:
```bash
cd ~/OrangeFox
source build/envsetup.sh
source device/vivo/PD2502/vendorsetup.sh
lunch fox_PD2502-eng
mka recoveryimage -j$(nproc --all)
```

---

## Flashing Instructions

Because recovery is integrated into `vendor_boot`:
```bash
adb reboot bootloader
fastboot flash vendor_boot OrangeFox-vendor_boot-PD2502.img
fastboot reboot recovery
```

> **Warning:** Always keep a backup of your stock `boot_a.bin`, `init_boot_a.bin`, and `vendor_boot_a.bin` before testing!
