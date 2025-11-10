# Embedded Nano Compute Board Reference Guide

This cheat sheet summarizes three compact single-board computers (SBCs) that work well for kiosk, edge analytics, and automation workloads that demand tiny footprints and low power draws.

## Quick Board Comparison

| Board | CPU | RAM Options | Wireless | I/O Highlights | Power Envelope |
| --- | --- | --- | --- | --- | --- |
| Waveshare CM4-NANO (CM4 carrier) | Raspberry Pi Compute Module 4 (quad-core Cortex-A72) | 1–8 GB LPDDR4 depending on CM4 module | 802.11ac + BT 5.0 on Wi-Fi CM4 SKUs | 2× HDMI, 2× USB 2.0, PCIe x1 slot, M.2 E-key, Gigabit Ethernet | 5 V @ 3 A (15 W max) |
| Orange Pi Zero 2W | Allwinner H618 (quad-core Cortex-A53) | 1 GB LPDDR4 | 802.11ac + BT 5.0 | 1× USB 2.0 OTG, 26-pin GPIO, mini HDMI, 100 Mbps Ethernet via USB adapter | 5 V @ 2 A (10 W max) |
| Raspberry Pi Zero 2 W | Broadcom BCM2710A1 (quad-core Cortex-A53) | 512 MB LPDDR2 | 802.11n + BT 4.2 | mini HDMI, USB 2.0 OTG, CSI camera | 5 V @ 1.5 A (7.5 W max) |

## Accessory Recommendations

### Waveshare CM4-NANO
- **Compute Module 4 SKU:** Select the eMMC + Wi-Fi version to simplify boot media and provide wireless connectivity.
- **Storage:** Utilize the onboard eMMC. For additional storage, use the PCIe x1 slot with an NVMe SSD via M.2 adapter.
- **Cooling:** Pair with a low-profile aluminum heat spreader or active cooler when using higher-TDP CM4 variants.
- **Power:** Provide a regulated 5 V, 3 A supply through the USB-C power input.
- **Expansion:** The carrier exposes a standard M.2 E-key slot suitable for Coral TPU or Wi-Fi upgrades.

### Orange Pi Zero 2W
- **Storage:** Use a high-endurance microSD card (U3 / A2 class) for rootfs reliability.
- **Enclosure:** Printed cases sized for the Zero 2W maintain access to the GPIO header; include vents for passive cooling.
- **Power:** Stable 5 V, 2 A USB-C power adapter with inline switch improves deployment convenience.
- **Networking:** USB-C OTG Ethernet adapters or USB 2.0 hubs expand peripheral connectivity.

### Raspberry Pi Zero 2 W
- **Storage:** High-endurance microSD card (A2) improves longevity in write-heavy scenarios.
- **USB Expansion:** Use a USB OTG shim or Zero 2 W hub to attach keyboards, cameras, or sensors.
- **Camera:** Compatible with the Raspberry Pi Camera Module 2/3 using the mini CSI ribbon adapter.
- **Power:** 5 V, 2.5 A supply is sufficient even when peripherals draw moderate current.
- **Thermals:** Passive copper shim with adhesive thermal tape keeps the BCM2710A1 within spec under sustained load.

## Ready-to-Flash OS Images

| Board | Recommended Image | Notes |
| --- | --- | --- |
| Waveshare CM4-NANO | Raspberry Pi OS Lite (64-bit) CM4 image | Use `rpiboot` for eMMC flashing; enable PCIe in `config.txt` when attaching NVMe devices. |
| Orange Pi Zero 2W | Orange Pi OS (Debian XFCE) or Armbian (CLI) | Flash with `orangepi-config` or `armbian-config`; install `opi-gpio` overlays for H618 peripherals. |
| Raspberry Pi Zero 2 W | Raspberry Pi OS Lite (32-bit) | Pre-enable SSH via `ssh` flag on boot partition; configure Wi-Fi using `wpa_supplicant.conf` before first boot. |

## Deployment Tips

- Validate power stability under peak load with an inline USB power meter before field deployment.
- Harden images by disabling unused services, locking down SSH, and setting up automatic security updates.
- Capture golden images after initial configuration so that future units can be reprovisioned quickly.
- Maintain spare microSD cards or eMMC modules pre-flashed with the latest configuration for hot swaps.

