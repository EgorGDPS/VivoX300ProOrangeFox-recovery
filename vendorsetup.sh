#!/usr/bin/env bash
#
# OrangeFox Recovery environment setup for vivo X300 Pro (PD2502)
#

export FOX_BUILD_DEVICE="PD2502"
export FOX_TARGET_DEVICES="PD2502,PD2502F,V2514,x300pro"

# Partition layout & Recovery type
export FOX_AB_DEVICE=1
export FOX_VIRTUAL_AB_DEVICE=1
export FOX_VENDOR_BOOT_RECOVERY=1

# Build engine flags
export FOX_USE_TWRP_RECOVERY_IMAGE_BUILDER=1
export OF_USE_MAGISKBOOT=1
export OF_USE_MAGISKBOOT_FOR_ALL_PATCHES=1

# Storage and Encryption handling
export OF_DONT_PATCH_ENCRYPTED_DEVICE=1
export OF_NO_TREBLE_COMPATIBILITY_CHECK=1
export OF_NO_RELOAD_AFTER_DEC=1

# Features & Display geometry
export OF_FLASHLIGHT_ENABLE=0
export OF_ADVANCED_SECURITY=1
export OF_SCREEN_H=2800
export OF_STATUS_H=120
export OF_STATUS_INDENT_LEFT=48
export OF_STATUS_INDENT_RIGHT=48
export OF_ALLOW_DISABLE_NAVBAR=0

# Shell & utilities
export FOX_USE_BASH_SHELL=1
export FOX_USE_NANO_EDITOR=1
export FOX_USE_TAR_BINARY=1
export FOX_USE_SED_BINARY=1

# Maintainer and Variant
export OF_MAINTAINER="Egor"
export FOX_VARIANT="Unofficial"

echo ">> Configured OrangeFox build environment for vivo X300 Pro ($FOX_BUILD_DEVICE)"
