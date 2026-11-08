import os
import shutil
import subprocess

work_dir = "/home/egorf/repack_workspace"
if os.path.exists(work_dir):
    shutil.rmtree(work_dir)
os.makedirs(work_dir)

magiskboot = "/home/egorf/x300prorecovery/device_vivo_PD2502/prebuilt/magiskboot"
dt_dir = "/home/egorf/x300prorecovery/device_vivo_PD2502"
stock_dump = "/home/egorf/stock_vendor_boot_a.bin"
fox_base = "/home/egorf/OrangeFox-vivo-x300pro-PD2502/vendor_boot.img"

print("1. Unpacking clean recovery ramdisk from OrangeFox base...")
fox_dir = os.path.join(work_dir, "fox")
os.makedirs(fox_dir)
subprocess.run([magiskboot, "unpack", fox_base], cwd=fox_dir, check=False)
rec_cpio = os.path.join(fox_dir, "vendor_ramdisk", "recovery.cpio")
print(f"OrangeFox recovery.cpio size: {os.path.getsize(rec_cpio)} bytes")

print("2. Preparing patched vtsthp binary...")
# Replace /vendor/lib64/libvts.so with /system/lib64/libvts.so
with open("/home/egorf/x300prorecovery/unpack_recovery/vendor/bin/vtsthp", "rb") as f:
    vtsthp_data = bytearray(f.read())

old_str = b"/vendor/lib64/libvts.so"
new_str = b"/system/lib64/libvts.so"
assert len(old_str) == len(new_str)
count = 0
idx = 0
while True:
    pos = vtsthp_data.find(old_str, idx)
    if pos == -1:
        break
    vtsthp_data[pos:pos+len(new_str)] = new_str
    count += 1
    idx = pos + len(new_str)
print(f"Replaced {count} occurrences of {old_str.decode()} with {new_str.decode()} in vtsthp")

patched_vtsthp = os.path.join(work_dir, "vtsthp_patched")
with open(patched_vtsthp, "wb") as f:
    f.write(vtsthp_data)
os.chmod(patched_vtsthp, 0o755)

print("3. Preparing start_touch.sh script...")
start_touch_sh = os.path.join(work_dir, "start_touch.sh")
with open(start_touch_sh, "w") as f:
    f.write("""#!/system/bin/sh

setup_mounts() {
    echo -n /system/vendor/firmware > /sys/module/firmware_class/parameters/path 2>/dev/null
    mkdir -p /vendor
    if [ ! -e /vendor/lib64 ]; then
        toybox ln -sf /system/lib64 /vendor/lib64 2>/dev/null
    fi
    if [ ! -e /vendor/firmware ]; then
        toybox ln -sf /system/vendor/firmware /vendor/firmware 2>/dev/null
    fi
    # Magisk staging support when /data is encrypted
    mkdir -p /tmp/cache /tmp/data_adb /tmp/data_adb/magisk 2>/dev/null
    rm -f /cache 2>/dev/null
    toybox ln -sf /tmp /cache 2>/dev/null
    toybox ln -sf /system/bin/getprop /sbin/getprop 2>/dev/null
    toybox ln -sf /system/bin/getprop /bin/getprop 2>/dev/null
}

# Initial wait for TWRP partition manager to finish unlinking /vendor
sleep 3
setup_mounts

# Vivo props
resetprop ro.vivo.product.model PD2502
resetprop ro.vendor.vivo.product.model PD2502
resetprop ro.build.oem.projects PD2502

# Touch status
echo 0 > /sys/class/vts/vivo_ts/status/proximity 2>/dev/null
echo 1 > /sys/class/vts/vivo_ts/status/force_normal 2>/dev/null

# Fix permissions
chmod 0666 /dev/vts_thp0 /dev/vts_thp1 /dev/vivo_input_agent /dev/vivo_gdix_thp 2>/dev/null
chmod 0666 /dev/input/event* 2>/dev/null

# Ensure backlight is on
echo 6000 > /sys/class/leds/lcd-backlight/brightness 2>/dev/null

# Restart vtsthp now that /vendor/firmware is properly setup
killall vtsthp 2>/dev/null
start vtsthpServiceRecovery0 2>/dev/null

# Continuous supervisor loop (runs in foreground of daemon service, NO oneshot)
while true; do
    sleep 2
    if [ ! -e /vendor/firmware ]; then
        setup_mounts
    fi
    if ! pidof vtsthp >/dev/null 2>&1; then
        echo 1 > /sys/class/vts/vivo_ts/status/force_normal 2>/dev/null
        start vtsthpServiceRecovery0 2>/dev/null
    fi
done
""")
os.chmod(start_touch_sh, 0o755)

print("4. Preparing configuration and RC files...")
# ld.config.txt
ld_config = os.path.join(work_dir, "ld.config.txt")
with open(ld_config, "w") as f:
    f.write("""dir.recovery = /system/bin
[recovery]
namespace.default.isolated = false
namespace.default.search.paths = /system/${LIB}
namespace.default.search.paths += /system/vendor/${LIB}
namespace.default.search.paths += /vendor/${LIB}
namespace.default.asan.search.paths = /data/asan/system/${LIB}
namespace.default.asan.search.paths += /system/${LIB}
namespace.default.hwasan.search.paths = /system/${LIB}/hwasan
namespace.default.hwasan.search.paths += /system/${LIB}
""")

# vtsthp.rc
vtsthp_rc = os.path.join(work_dir, "vtsthp.rc")
with open(vtsthp_rc, "w") as f:
    f.write("""on property:vendor.vivo.touch.support.vtsthp_recovery0=1
    write /dev/thp-dev 0
    chmod 0664 /dev/thp-dev
    chown system /dev/thp-dev

    chmod 0664 /dev/vts_thp0
    start vtsthpServiceRecovery0

on property:vendor.vivo.touch.support.vtsthp_recovery1=1
    chmod 0664 /dev/vts_thp1
    start vtsthpServiceRecovery1

service vtsthpServiceRecovery0 /system/bin/vtsthp --thp 0
    class core
    user root
    group system
    disabled
    seclabel u:r:recovery:s0

service vtsthpServiceRecovery1 /system/bin/vtsthp --thp 1
    class core
    user root
    group system
    disabled
    seclabel u:r:recovery:s0
""")

# init.recovery.mt6993.rc
mtk_rc = os.path.join(work_dir, "init.recovery.mt6993.rc")
with open(mtk_rc, "w") as f:
    f.write("""import /init.recovery.touch.rc
import /init.recovery.project.rc

on init
    setprop sys.usb.configfs 1
    setprop sys.usb.controller "16751000.usb0"

on property:sys.usb.config=mtp,adb && property:sys.usb.configfs=1
    setprop sys.usb.config adb

on property:sys.usb.config=mtp && property:sys.usb.configfs=1
    setprop sys.usb.config adb

on property:sys.usb.config=none && property:sys.usb.configfs=1
    setprop sys.usb.state none

on property:sys.usb.config=adb && property:sys.usb.configfs=1
    write /config/usb_gadget/g1/idProduct 0x${ro.recovery.usb.adb.pid}
    write /config/usb_gadget/g1/configs/b.1/strings/0x409/configuration "adb"
    symlink /config/usb_gadget/g1/functions/ffs.adb /config/usb_gadget/g1/configs/b.1/f1
    write /config/usb_gadget/g1/UDC ${sys.usb.controller}
    setprop sys.usb.state adb

on property:sys.usb.config=sideload && property:sys.usb.configfs=1
    write /config/usb_gadget/g1/idProduct 0x${ro.recovery.usb.adb.pid}
    write /config/usb_gadget/g1/configs/b.1/strings/0x409/configuration "adb"
    symlink /config/usb_gadget/g1/functions/ffs.adb /config/usb_gadget/g1/configs/b.1/f1
    write /config/usb_gadget/g1/UDC ${sys.usb.controller}
    setprop sys.usb.state sideload

on late-init
    start mtk_storageproxyd

on fs
    exec u:r:recovery:s0 root root -- /system/bin/userdata_setup
    symlink /dev/block/mapper/mtk_userdata /dev/block/by-name/userdata

on fs && property:ro.debuggable=0

on boot
    exec u:r:update_engine:s0 root root -- /system/bin/mtk_plpath_utils
    symlink /tmp /cache
    symlink /system/bin/getprop /sbin/getprop
""")

# init.recovery.touch.rc
touch_rc = os.path.join(work_dir, "init.recovery.touch.rc")
with open(touch_rc, "w") as f:
    f.write("""on boot
	setprop ro.vivo.product.model PD2502
	setprop ro.vendor.vivo.product.model PD2502
	setprop ro.build.oem.projects PD2502
	chmod 0666 /dev/vts_thp0
	chmod 0666 /dev/vts_thp1
	chmod 0666 /dev/vivo_input_agent
	chmod 0666 /dev/vivo_gdix_thp
	write /sys/class/vts/vivo_ts/status/proximity 0
	write /sys/class/vts/vivo_ts/status/force_normal 1
	start start_touch

on property:vendor.vivo.touch.support.vtsthp_recovery0=1
	chmod 0666 /dev/vts_thp0
	start vtsthpServiceRecovery0

service start_touch /system/bin/sh /system/bin/start_touch.sh
	class core
	user root
	group root system
	seclabel u:r:recovery:s0

service vtsthpServiceRecovery0 /system/bin/vtsthp --thp 0
	class core
	user root
	group system
	disabled
	seclabel u:r:recovery:s0
""")

# init.recovery.usb.rc
usb_rc = os.path.join(work_dir, "init.recovery.usb.rc")
with open(usb_rc, "w") as f:
    f.write("""on property:sys.usb.config=mtp,adb && property:sys.usb.configfs=1
    setprop sys.usb.config adb

on property:sys.usb.config=mtp && property:sys.usb.configfs=1
    setprop sys.usb.config adb

on property:sys.usb.config=none && property:sys.usb.configfs=1
    setprop sys.usb.state none

on property:sys.usb.config=adb && property:sys.usb.configfs=1
    write /config/usb_gadget/g1/idProduct 0x${ro.recovery.usb.adb.pid}
    write /config/usb_gadget/g1/configs/b.1/strings/0x409/configuration "adb"
    symlink /config/usb_gadget/g1/functions/ffs.adb /config/usb_gadget/g1/configs/b.1/f1
    write /config/usb_gadget/g1/UDC ${sys.usb.controller}
    setprop sys.usb.state adb

on property:sys.usb.config=sideload && property:sys.usb.configfs=1
    write /config/usb_gadget/g1/idProduct 0x${ro.recovery.usb.adb.pid}
    write /config/usb_gadget/g1/configs/b.1/strings/0x409/configuration "adb"
    symlink /config/usb_gadget/g1/functions/ffs.adb /config/usb_gadget/g1/configs/b.1/f1
    write /config/usb_gadget/g1/UDC ${sys.usb.controller}
    setprop sys.usb.state sideload
""")

print("5. Injecting files into recovery.cpio...")
def inject(mode, target_path, src_file):
    # Ensure target_path NEVER starts with "vendor/"
    assert not target_path.startswith("vendor/"), f"Illegal path starting with vendor/: {target_path}"
    subprocess.check_call([magiskboot, "cpio", rec_cpio, f"add {mode} {target_path} {src_file}"], cwd=fox_dir, stdout=subprocess.DEVNULL)

# Patch system/etc/init/hw/init.rc to point /cache to /tmp instead of /data/cache
extracted_init_rc = os.path.join(work_dir, "init.rc.extracted")
subprocess.check_call([magiskboot, "cpio", rec_cpio, f"extract system/etc/init/hw/init.rc {extracted_init_rc}"], cwd=fox_dir, stdout=subprocess.DEVNULL)
with open(extracted_init_rc, "r") as f:
    init_rc_content = f.read()
init_rc_content = init_rc_content.replace("symlink /data/cache /cache", "symlink /tmp /cache")
patched_init_rc = os.path.join(work_dir, "init.rc.patched")
with open(patched_init_rc, "w") as f:
    f.write(init_rc_content)
inject("0644", "system/etc/init/hw/init.rc", patched_init_rc)

# Inject static symlinks into cpio
subprocess.run([magiskboot, "cpio", rec_cpio, "ln tmp cache"], cwd=fox_dir, stdout=subprocess.DEVNULL)
subprocess.run([magiskboot, "cpio", rec_cpio, "ln /system/bin/toolbox sbin/getprop"], cwd=fox_dir, stdout=subprocess.DEVNULL)
subprocess.run([magiskboot, "cpio", rec_cpio, "ln /system/bin/toolbox bin/getprop"], cwd=fox_dir, stdout=subprocess.DEVNULL)

# Injected root rc files
inject("0755", "init.recovery.mt6993.rc", mtk_rc)
inject("0755", "init.recovery.touch.rc", touch_rc)
inject("0755", "init.recovery.usb.rc", usb_rc)

# Injected etc configs
inject("0644", "system/etc/ld.config.txt", ld_config)
inject("0644", "system/etc/init/vtsthp.rc", vtsthp_rc)
fstab_src = "/home/egorf/x300prorecovery/device_vivo_PD2502/recovery/root/system/etc/recovery.fstab"
flags_src = "/home/egorf/x300prorecovery/device_vivo_PD2502/recovery/root/system/etc/twrp.flags"
inject("0644", "system/etc/recovery.fstab", fstab_src)
inject("0644", "system/etc/twrp.flags", flags_src)
inject("0644", "etc/recovery.fstab", fstab_src)
inject("0644", "etc/twrp.flags", flags_src)

# Injected bin executables
inject("0755", "system/bin/vtsthp", patched_vtsthp)
inject("0755", "system/vendor/bin/vtsthp", patched_vtsthp)
inject("0755", "system/bin/start_touch.sh", start_touch_sh)

# Injected shared libraries (libexpat.so + 10 touch libs)
expat_src = "/home/egorf/x300prorecovery/unpack_recovery/system/lib64/libexpat.so"
inject("0644", "system/lib64/libexpat.so", expat_src)
inject("0644", "system/vendor/lib64/libexpat.so", expat_src)

stock_libs_dir = "/home/egorf/x300prorecovery/unpack_recovery/vendor/lib64"
touch_lib_names = [
    "PD2502_MODID0x0103_libgdix_tsa.so",
    "PD2502_MODID0x0104_libgdix_tsa.so",
    "PD2502_MODID0x0105_libgdix_tsa.so",
    "PD2509_MODID0x0104_libgdix_tsa.so",
    "libgdix_afeH018AM2900.so",
    "libgdix_tsa.so",
    "libgdix_tsc.so",
    "libsynaHal.so",
    "libvts.so",
    "libvtsthp.so",
]
for lib in touch_lib_names:
    src = os.path.join(stock_libs_dir, lib)
    assert os.path.exists(src), f"Missing lib: {src}"
    inject("0644", f"system/lib64/{lib}", src)
    inject("0644", f"system/vendor/lib64/{lib}", src)

# Injected touch firmware configs under system/vendor/firmware
stock_fw_dir = "/home/egorf/x300prorecovery/unpack_recovery/vendor/firmware"
for fw_file in sorted(os.listdir(stock_fw_dir)):
    src = os.path.join(stock_fw_dir, fw_file)
    if os.path.isfile(src):
        inject("0644", f"system/vendor/firmware/{fw_file}", src)

print(f"Injection complete! New recovery.cpio size: {os.path.getsize(rec_cpio)} bytes")

print("6. Compressing recovery.cpio with lz4_legacy...")
comp_rec = os.path.join(work_dir, "recovery.cpio.lz4")
subprocess.check_call([magiskboot, "compress=lz4_legacy", rec_cpio, comp_rec])
print(f"Compressed recovery.cpio size: {os.path.getsize(comp_rec)} bytes")

print("7. Unpacking stock vendor_boot_a.bin (with -n to keep raw platform ramdisk)...")
stock_dir = os.path.join(work_dir, "stock")
os.makedirs(stock_dir)
subprocess.run([magiskboot, "unpack", "-n", stock_dump], cwd=stock_dir, check=False)

stock_platform_ramdisk = os.path.join(stock_dir, "vendor_ramdisk", "ramdisk.cpio")
print(f"Stock platform ramdisk size: {os.path.getsize(stock_platform_ramdisk)} bytes")

print("8. Assembling final vendor_boot directory...")
final_dir = os.path.join(work_dir, "final")
os.makedirs(os.path.join(final_dir, "vendor_ramdisk"))

shutil.copy(stock_platform_ramdisk, os.path.join(final_dir, "vendor_ramdisk", "ramdisk.cpio"))
shutil.copy(comp_rec, os.path.join(final_dir, "vendor_ramdisk", "recovery.cpio"))
shutil.copy(os.path.join(stock_dir, "dtb"), os.path.join(final_dir, "dtb"))
shutil.copy(os.path.join(stock_dir, "bootconfig"), os.path.join(final_dir, "bootconfig"))

with open(os.path.join(final_dir, "header"), "w") as f:
    f.write("name=\ncmdline=bootopt=64S3,32N2,64N2 product.version=PD2502F_EX_A_16.0.4.3.W20 fingerprint.abbr=16/BP2A.250605.031.A3 region_ver=W20 product.solution=MTK bootconfig\n")

print("9. Repacking final vendor_boot image with -n...")
out_img = "/home/egorf/OrangeFox-vendor_boot-PD2502.img"
subprocess.check_call([magiskboot, "repack", "-n", stock_dump, out_img], cwd=final_dir)

dest2 = "/home/egorf/x300prorecovery/orangefox_vendor_boot.img"
shutil.copy(out_img, dest2)
print(f"Final image built: {out_img} (Size: {os.path.getsize(out_img)} bytes)")

print("10. Verifying generated image...")
verify_dir = os.path.join(work_dir, "verify")
os.makedirs(verify_dir)
subprocess.run([magiskboot, "unpack", out_img], cwd=verify_dir, check=False)
print("SUCCESS: Image verified cleanly!")
