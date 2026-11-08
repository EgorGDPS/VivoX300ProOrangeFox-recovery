#!/system/bin/sh
# Force Vivo model properties
resetprop ro.vivo.product.model PD2502
resetprop ro.vendor.vivo.product.model PD2502
resetprop ro.build.oem.projects PD2502
# Force normal touch proximity
echo 0 > /sys/class/vts/vivo_ts/status/proximity
echo 1 > /sys/class/vts/vivo_ts/status/force_normal
# Keep Goodix THP daemon alive
while true; do
    /system/bin/vtsthp --thp 0
    sleep 2
done
