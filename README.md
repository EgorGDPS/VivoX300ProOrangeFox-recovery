# OrangeFox / TWRP Device Tree for vivo X300 Pro (PD2502 / V2514)

> [!CAUTION]
> ### DISCLAIMER & NO RESPONSIBILITY
> **USE AT YOUR OWN RISK.**
> * Flashing custom recovery images can potentially brick your device, cause bootloops, corrupt partitions, or cause permanent data loss.
> * The author(s) and maintainer(s) assume **ABSOLUTELY NO RESPONSIBILITY** for any damage, bricked devices, data loss, dead motherboards, hardware failure, thermonuclear war, or you getting fired because your alarm clock failed.
> * You alone choose to make these modifications to your device. If you point the finger at anyone else for messing up your device, you will be laughed at.
> * **A LOT OF FEATURES ARE CURRENTLY UNTESTED.** Only basic, core recovery functions (native OLED display, touchscreen input, ADB sideload, ZIP flashing with cache redirection, partition mounting) have been verified. Advanced functions such as decryption of stock encrypted userdata, full partition backup/restore, OTG storage, and advanced OrangeFox addons are experimental or untested.

---

## Known Bugs & Quirks
1. **Screen Turn-On Delay:** When turning on the display or waking from sleep, there is a noticeable delay before the panel lights up.
2. **Display Wake Glitch:** For approximately one second after the screen turns on, half of the display may render black while the other half renders normally, after which it instantly normalizes.
3. **Occasional Recovery UI Restart:** The recovery UI process may occasionally soft-restart with the OrangeFox splash screen (e.g. during specific partition manager transitions), but this does not affect general usage or brick the device.

---

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

### Method 1: Standalone Perfect Assembly (Fastest & Verified)
You can directly assemble the tested, verified vendor_boot recovery image using the included self-contained script:
```bash
python3 assemble_perfect_recovery.py
```
This unpacks the base recovery ramdisk, injects the Goodix touch daemon and libraries, sets non-blocking `/vendor` symlinks, patches `init.rc` for `/cache -> /tmp`, configures ConfigFS USB triggers, extracts the stock platform ramdisk, and packs the final header v4 `OrangeFox-vendor_boot-PD2502.img`.

### Method 2: OrangeFox 16.0 Build from Source
Sync the OrangeFox Android 16 (`fox_16.0`) source tree:
```bash
mkdir -p ~/OrangeFox && cd ~/OrangeFox
repo init --depth=1 -u https://gitlab.com/OrangeFox/Manifest.git -b fox_16.0
repo sync -c -j$(nproc --all) --force-sync --no-clone-bundle --no-tags
```

Copy this repository to `device/vivo/PD2502`:
```bash
cp -r /path/to/device_vivo_PD2502 ~/OrangeFox/device/vivo/PD2502
```

Build OrangeFox recovery:
```bash
cd ~/OrangeFox
source build/envsetup.sh
source device/vivo/PD2502/vendorsetup.sh
lunch twrp_PD2502-bp2a-eng
mka vendorbootimage recoveryimage -j$(nproc --all)
```

Post-build assembly with all hardware drivers and mods:
```bash
python3 device/vivo/PD2502/assemble_perfect_recovery.py \
  --fox-base out/target/product/PD2502/vendor_boot.img \
  --device-tree device/vivo/PD2502 \
  --output out/target/product/PD2502/OrangeFox-vendor_boot-PD2502.img
```

---

## GitHub Actions Automated CI/CD Workflow

The repository includes a production-ready automated build workflow located at [`.github/workflows/build_fox.yml`](.github/workflows/build_fox.yml).

### Workflow Features
1. **Automated Pipeline on Push & Manual Dispatch:** Runs automatically on push to `main` or on demand via `workflow_dispatch`.
2. **Resource Optimization:** Configures 16GB swap on Ubuntu runner and tunes Go Soong compiler memory limits (`GOMEMLIMIT=12GiB`) to prevent out-of-memory errors during AOSP Android 16 compilation.
3. **Android 16 Compatibility Patches:**
   - Automatically handles 16KB vs 4KB page size enforcement for prebuilt binaries.
   - Applies `host_init_verifier` patches to accommodate vendor init syntax.
   - Enforces Header Version 4 in `mkbootimg`.
4. **Automated Perfect Assembly:** Runs `assemble_perfect_recovery.py` on the compiled `vendor_boot.img` output to inject all verified mods (Goodix touchscreen drivers, haptics, sideload triggers, `/cache -> /tmp` staging).
5. **Artifacts & Checksums:** Automatically computes SHA256 checksums and uploads `OrangeFox-vendor_boot-PD2502.img` and `SHA256SUMS.txt` as downloadable GitHub Actions release artifacts.

---

## Flashing Instructions

Because recovery is integrated into `vendor_boot`:
```bash
adb reboot bootloader
fastboot flash vendor_boot OrangeFox-vendor_boot-PD2502.img
fastboot reboot recovery
```

> **Warning:** Always keep a backup of your stock `boot_a.bin`, `init_boot_a.bin`, and `vendor_boot_a.bin` before testing!
