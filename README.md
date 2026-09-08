# HP ZBook Fury G9: macOS Sequoia VFIO with W6600M passthrough

A personal build record for running macOS Sequoia in QEMU/KVM on an HP ZBook Fury G9, with an AMD Radeon PRO W6600M passed through to the guest and Sunshine/Moonlight providing low-latency access from the same laptop's Linux desktop.

The project began on **CachyOS** and has since migrated successfully to **Omarchy**. The repository is intentionally distro-neutral: CachyOS is retained as the original validated baseline, while Omarchy is the current host implementation.

**Status: working on one machine; cold-boot/persistence and long-duration stability are still being validated.** This is a configuration reference, not a universal installer or a supported product.

> **No support. Use at your own risk.** I do not provide installation help, troubleshooting, remote assistance, maintenance commitments, or compatibility guarantees. This material is provided **AS IS, WITHOUT WARRANTY**. To the maximum extent permitted by applicable law, I and the contributors are not liable for damages or losses resulting from its use, including data loss, hardware damage, downtime, or lost income. See [DISCLAIMER.md](DISCLAIMER.md), [SUPPORT.md](SUPPORT.md), and [LICENSE](LICENSE).

This project documents configuration and testing. The software that makes it possible belongs to its upstream authors—especially **Gabriel Luchina and the OSX-PROXMOX contributors**, **Acidanthera**, **Dortania**, **QEMU/libvirt**, **LizardByte/Moonlight**, and **BetterDisplay**. See [CREDITS.md](CREDITS.md) for attribution and source links. No upstream EFI package, kext, GPU ROM, firmware binary, macOS image, Apple SMC key, Sunshine pairing database, or private credential is redistributed here.

## Current architecture

```text
HP ZBook Fury G9
|
+- Linux host (originally CachyOS, currently Omarchy)
|  +- Intel integrated graphics -> Linux desktop
|  +- ZFS pool `fury`
|  +- libvirt / QEMU / KVM
|  +- Moonlight client
|
+- macOS Sequoia VM
   +- Radeon PRO W6600M VFIO passthrough
   |  +- 256 MiB BAR0 ReBAR configuration before VFIO bind
   |  +- Metal 3
   |
   +- BetterDisplay
   |  +- virtual display `Moonlight`
   |     +- 1920x1200 tested
   |
   +- Sunshine
      +- VideoToolbox
      +- HEVC
      +- vt_software = disabled
      +- vt_realtime = enabled
```

## What is currently verified

| Component | Observed result |
|---|---|
| Guest | macOS Sequoia **15.7.9**, build **24G830** |
| CPU / memory | **8 vCPUs**, `Skylake-Client`, `invtsc`, **32 GiB RAM** |
| Firmware / machine | OVMF 4 MiB family, **Q35 `pc-q35-11.1`** |
| GPU | Radeon PRO **W6600M**, 8 GB; guest device ID **`0x73e3`** |
| Acceleration | `system_profiler` reports **Metal 3** |
| Guest video topology | W6600M is the only VGA device; libvirt virtual video model is `none` |
| ReBAR | BAR0 successfully configured to **256 MiB** before VFIO binding |
| Networking | **VMXNET3** on libvirt NAT with a stable DHCP reservation |
| Guest storage | VM stored on ZFS pool `fury` under the Omarchy host |
| Virtual display | BetterDisplay virtual display named **`Moonlight`** works as Sunshine capture target |
| Sunshine encoder | **VideoToolbox**, HEVC tested, `vt_software = disabled`, `vt_realtime = enabled` |
| Remote desktop | Sunshine in macOS; Moonlight on the **same Linux laptop** |
| Stream performance | ~90 FPS sustained in a 1920x1200 test with zero network/jitter drops |
| Client-side latency observations | ~1 ms network, ~0.4 ms decode, ~0.4 ms frame queue in the best observed runs |
| Audio | Owner-confirmed playback through Sunshine/Moonlight |

These are observations from one system, not minimum requirements or benchmark guarantees.

## Critical finding: disable virtual VGA

The installation stage used virtual VGA/SPICE with no PCI passthrough. After adding the W6600M while retaining virtual VGA, the guest failed to boot reliably. Changing **only the video model to `none`** allowed the guest to reach the desktop with Metal 3 and physical GPU output.

Keep this in the working GPU definition:

```xml
<video>
  <model type="none"/>
</video>
```

Later QEMU PCI inspection confirmed that the passed-through W6600M is the guest's only VGA controller. Do not re-enable a virtual VGA device as a headless-display substitute. SPICE input/audio plumbing may remain configured, but its console does not provide the passed-through GPU's framebuffer.

## Headless display evolution

The original CachyOS baseline was validated using a physical Mini DisplayPort display before testing headless Sunshine/Moonlight operation.

The current Omarchy configuration uses **BetterDisplay 4.3.6 build 50119** to create a software virtual display named `Moonlight`. Sunshine detects that display directly:

```text
Detected display: Moonlight (id: 4128837) connected: true
Configuring selected display (4128837) to stream
```

This removes the normal requirement to keep a physical display attached for day-to-day streaming. BetterDisplay must remain running: when it is quit, the virtual display disappears and Sunshine falls back to another detected display target.

See [docs/04-streaming.md](docs/04-streaming.md) for the current remote-display and encoder notes.

## Omarchy migration

The known-good Sequoia VM was migrated from CachyOS to a fresh Omarchy installation without rebuilding macOS. The VM now resides on the existing ZFS pool `fury`.

Important host-side lessons from the migration:

- keep the original known-good VM disks, NVRAM, GPU ROM and XML backed up before changing the host OS;
- import and mount ZFS before libvirt starts the VM;
- configure the W6600M BAR and bind the GPU/audio functions to `vfio-pci` before libvirt can start the guest;
- use explicit libvirt/UFW rules for `virbr0` DHCP, DNS and forwarding rather than tying guest connectivity to a particular physical host interface;
- retain the LTS kernel as the current known-good ZFS/VFIO kernel while keeping the normal kernel as fallback.

A full powered-off host boot through ZFS import, VFIO/ReBAR setup, VM start, BetterDisplay startup and Sunshine/Moonlight reconnection is still being treated as a validation item rather than a completed guarantee.

## Sunshine / Moonlight notes

The current explicit Sunshine encoder settings are:

```text
encoder = videotoolbox
vt_software = disabled
vt_realtime = enabled
```

HEVC is currently the cleanest tested path. AV1 is unavailable on this macOS/W6600M combination. H.264 is detected but has shown an initial VideoToolbox compression-session warning during probing, so software encoding should not be enabled casually merely to suppress that warning.

At 1920x1200 with a requested 120 FPS stream, the observed rate settles around **89.5-89.6 FPS**. In that state, Moonlight reported approximately 1 ms network latency, ~0.4 ms hardware decode time, ~0.4 ms frame queue time, and no network/jitter frame loss. Perceived pointer/typing latency remains slightly higher than these client-side numbers suggest, so the remaining latency is believed to be upstream of Moonlight's network/decode path and is still under investigation.

## BetterDisplay shutdown event: observed, cause not yet established

During one test session the macOS guest performed an orderly shutdown. Host-side libvirt/QEMU logs showed a guest-originated shutdown rather than libvirt terminating QEMU.

macOS Unified Logging then showed BetterDisplay sending the Apple Event that requests the shutdown dialog:

```text
BetterDisplay ... AESendMessage(aevt,rsdn ... target='psn '[loginwindow])
loginwindow ... Received a kAEShowShutdownDialog
loginwindow ... logoutType:3 - Shutdown
```

BetterDisplay had **no custom keyboard shortcuts configured**. Sunshine/Moonlight was active at the time, but the evidence does **not** establish why BetterDisplay sent the event or that Moonlight caused it. Treat this as an observed troubleshooting datapoint, not a confirmed BetterDisplay defect.

For an always-on remote VM, macOS power settings were also adjusted so normal idle power management does not intentionally suspend the guest:

```bash
sudo pmset -a sleep 0 disksleep 0 powernap 0
```

## Start here

1. Read [host prerequisites](docs/01-host.md). The record began from an existing VFIO-capable host and does not pretend every original provisioning step was captured.
2. Follow the [Sequoia installation stages](docs/02-install.md), initially using virtual video.
3. Review the [W6600M configuration and transition](docs/03-gpu.md).
4. Configure [Sunshine, Moonlight, BetterDisplay, networking, and audio](docs/04-streaming.md).
5. Keep [backups and rollback](docs/05-backup.md), and consult [observations and troubleshooting](docs/06-troubleshooting.md).

The [XML template](configs/sequoia-gpu-only.xml.in) reflects the GPU-only, no-physical-USB baseline. It deliberately omits the original VM UUID and MAC address and replaces the Apple SMC value with a placeholder. **Do not define it directly.** The [local preparation tool](tools/prepare_definition.py) supplies fresh identity values and reads the SMC argument from your own working XML without printing it.

```bash
python3 tools/prepare_definition.py --help
```

The GPU ROM path, host PCI addresses, QEMU machine version, firmware paths, disk path, ZFS dataset paths and service ordering must be checked against your own host before applying any definition.

## Project history

### CachyOS baseline

The original successful implementation used CachyOS as the host. It established the core VFIO behavior: W6600M passthrough, Metal 3, `video model='none'`, VMXNET3 networking, Sunshine/Moonlight access and successful headless reconnects after the physical display was removed.

### Omarchy migration

The current host is Omarchy. The same macOS installation and VFIO architecture continue to work, now with VM storage on ZFS, explicit VFIO/ReBAR service ordering, and a BetterDisplay virtual monitor for fully software-defined headless streaming.

## Project boundaries

- Never run two VMs that assign the same physical GPU at the same time.
- No installer image, recovery archive, NVRAM dump, serial number, SMBIOS identity, Sunshine pairing database, certificate, private key, credential, GPU ROM, firmware binary, macOS image, or Apple SMC key belongs in this repository.
- This repository does not grant rights to Apple software or third-party binaries. Obtain and use them under their applicable terms.
- Original documentation and helper code use the [MIT License](LICENSE). Referenced upstream projects retain their own licenses; credit is not permission to redistribute them.
- Issues and Discussions are intended to be disabled. Publishing this record does not establish a support channel.
