#
# OrangeFox / TWRP Makefile for vivo X300 Pro (PD2502)
#

# Inherit from our custom product configuration
$(call inherit-product, vendor/twrp/config/common.mk)

PRODUCT_DEVICE := PD2502
PRODUCT_NAME := twrp_PD2502
PRODUCT_BRAND := vivo
PRODUCT_MODEL := vivo X300 Pro
PRODUCT_MANUFACTURER := vivo
PRODUCT_RELEASE_NAME := vivo X300 Pro

PRODUCT_CHECK_PREBUILT_MAX_PAGE_SIZE := false

DEVICE_PATH := device/vivo/PD2502

# Inherit from device makefile
$(call inherit-product, $(DEVICE_PATH)/device.mk)
