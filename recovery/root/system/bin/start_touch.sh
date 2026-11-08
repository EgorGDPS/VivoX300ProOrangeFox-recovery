#!/system/bin/sh
# Setup vendor bindings in case TWRP unlinked /vendor
mkdir -p /vendor/bin /vendor/lib64 /vendor/firmware
mount -o bind /system/bin /vendor/bin 2>/dev/null
mount -o bind /system/lib64 /vendor/lib64 2>/dev/null
mount -o bind /system/vendor/firmware /vendor/firmware 2>/dev/null

# Vivo props
resetprop ro.vivo.product.model PD2502
resetprop ro.vendor.vivo.product.model PD2502
resetprop ro.build.oem.projects PD2502
setprop vendor.vivo.touch.support.vtsthp0 1
setprop vendor.vivo.touch.support.vtsthp_recovery0 1

# Touch status
echo 0 > /sys/class/vts/vivo_ts/status/proximity 2>/dev/null
echo 1 > /sys/class/vts/vivo_ts/status/force_normal 2>/dev/null

# Fix permissions
chmod 0666 /dev/vts_thp0 /dev/vts_thp1 /dev/vivo_input_agent /dev/vivo_gdix_thp 2>/dev/null
chmod 0666 /dev/input/event* 2>/dev/null

# Ensure backlight is on
echo 6000 > /sys/class/leds/lcd-backlight/brightness 2>/dev/null

# Launch daemon loop
while true; do
    /system/bin/vtsthp --thp 0
    sleep 1
done &
