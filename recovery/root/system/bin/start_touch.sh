#!/system/bin/sh

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
