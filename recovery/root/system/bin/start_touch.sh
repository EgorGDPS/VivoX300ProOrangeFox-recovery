#!/system/bin/sh

setup_mounts() {
    mkdir -p /vendor/bin /vendor/lib64 /vendor/firmware
    mount -o bind /system/bin /vendor/bin 2>/dev/null
    mount -o bind /system/lib64 /vendor/lib64 2>/dev/null
    mount -o bind /system/vendor/firmware /vendor/firmware 2>/dev/null
}

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

# Start recovery service
setprop vendor.vivo.touch.support.vtsthp_recovery0 1
start vtsthpServiceRecovery0 2>/dev/null

# Persistent supervisor: If TWRP unlinks /vendor or if vtsthp dies, restore and restart!
(
    while true; do
        sleep 2
        if [ ! -f /vendor/firmware/touch_firmwares_recovery.bin ]; then
            setup_mounts
            setprop vendor.vivo.touch.support.vtsthp_recovery0 1
            start vtsthpServiceRecovery0 2>/dev/null
        fi
        if ! pidof vtsthp >/dev/null 2>&1; then
            echo 1 > /sys/class/vts/vivo_ts/status/force_normal 2>/dev/null
            start vtsthpServiceRecovery0 2>/dev/null
        fi
    done
) &
