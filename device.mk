# Device makefile for vivo X300 Pro (PD2502)

LOCAL_PATH := device/vivo/PD2502

# Inherit from common AOSP 64-bit-only product configuration
$(call inherit-product, $(SRC_TARGET_DIR)/product/base.mk)
$(call inherit-product, $(SRC_TARGET_DIR)/product/core_64_bit_only.mk)
$(call inherit-product, $(SRC_TARGET_DIR)/product/virtual_ab_ota.mk)

# Disable ELF and page-size checks on prebuilt binaries for faster build and 4KB kernel compatibility
PRODUCT_CHECK_ELF_FILES := false
PRODUCT_CHECK_PREBUILT_MAX_PAGE_SIZE := false

# Recovery init scripts
PRODUCT_COPY_FILES += \
    $(LOCAL_PATH)/recovery/root/init.recovery.mt6993.rc:$(TARGET_COPY_OUT_RECOVERY)/root/init.recovery.mt6993.rc \
    $(LOCAL_PATH)/recovery/root/init.recovery.platform.rc:$(TARGET_COPY_OUT_RECOVERY)/root/init.recovery.platform.rc \
    $(LOCAL_PATH)/recovery/root/init.recovery.touch.rc:$(TARGET_COPY_OUT_RECOVERY)/root/init.recovery.touch.rc \
    $(LOCAL_PATH)/recovery/root/init.recovery.svc.rc:$(TARGET_COPY_OUT_RECOVERY)/root/init.recovery.svc.rc \
    $(LOCAL_PATH)/recovery/root/init.recovery.wifi.rc:$(TARGET_COPY_OUT_RECOVERY)/root/init.recovery.wifi.rc

# Recovery fstab and flags
PRODUCT_COPY_FILES += \
    $(LOCAL_PATH)/recovery.fstab:$(TARGET_COPY_OUT_RECOVERY)/root/system/etc/recovery.fstab \
    $(LOCAL_PATH)/recovery/root/etc/twrp.flags:$(TARGET_COPY_OUT_RECOVERY)/root/system/etc/twrp.flags

# Helper prebuilts for Dual UFS and Touchpanel
PRODUCT_COPY_FILES += \
    $(LOCAL_PATH)/recovery/root/system/bin/mtk_plpath_utils:$(TARGET_COPY_OUT_RECOVERY)/root/system/bin/mtk_plpath_utils \
    $(LOCAL_PATH)/recovery/root/system/bin/userdata_setup:$(TARGET_COPY_OUT_RECOVERY)/root/system/bin/userdata_setup \
    $(LOCAL_PATH)/recovery/root/system/bin/vts_app_recovery:$(TARGET_COPY_OUT_RECOVERY)/root/system/bin/vts_app_recovery

# Touchscreen firmware binaries
PRODUCT_COPY_FILES += $(call find-copy-subdir-files,*,$(LOCAL_PATH)/recovery/root/vendor/firmware,$(TARGET_COPY_OUT_RECOVERY)/root/vendor/firmware)
