# HP ZBook Fury G9: macOS Sequoia on CachyOS with W6600M passthrough

A personal build record for running macOS Sequoia in QEMU/KVM on an HP ZBook Fury G9, with an AMD Radeon PRO W6600M passed through to the guest and Sunshine/Moonlight providing access from the same laptop's CachyOS desktop.

**Status: working baseline on one machine; still being tested.** This is a configuration reference, not a universal installer or a supported product. Audio playback from macOS through Sunshine/Moonlight to CachyOS is confirmed by the owner.

> **No support. Use at your own risk.** I do not provide installation help, troubleshooting, remote assistance, maintenance commitments, or compatibility guarantees. This material is provided **AS IS, WITHOUT WARRANTY**. To the maximum extent permitted by applicable law, I and the contributors are not liable for damages or losses resulting from its use, including data loss, hardware damage, downtime, or lost income. See [DISCLAIMER.md](DISCLAIMER.md), [SUPPORT.md](SUPPORT.md), and [LICENSE](LICENSE).

This project documents configuration and testing. The software that makes it possible belongs to its upstream authors—especially **Gabriel Luchina and the OSX-PROXMOX contributors**, **Acidanthera**, **Dortania**, **QEMU/libvirt**, and **LizardByte/Moonlight**. See [CREDITS.md](CREDITS.md) for the full attribution and source links. No upstream EFI package, kext, GPU ROM, firmware binary, macOS image, or Apple SMC key is redistributed here.

## What was verified

| Component | Observed result |
|---|---|
| Guest | macOS Sequoia **15.7.9**, build **24G830** |
| CPU / memory | **8 vCPUs**, `Skylake-Client`, `invtsc`, **32 GiB RAM** |
| System disk | **256 GiB QCOW2**, independent of the old Ventura disks |
| Firmware / machine | OVMF 4 MiB family, **Q35 `pc-q35-11.1`** |
| GPU | Radeon PRO **W6600M**, 8 GB, guest device ID **`0x73e3`** |
| Acceleration | `system_profiler` reports **Metal 3** |
| Physical output | Mini DisplayPort monitor at **1920×1080, 60 Hz** |
| Input | Individual USB keyboard/mouse passthrough tested, then removed for Moonlight use |
| Networking | **VMXNET3** on libvirt NAT; DHCP reservation for a stable guest address |
| Remote desktop | Sunshine in macOS; Moonlight on the **same CachyOS laptop** |
| Headless use | Existing stream, fresh stream, and a guest reboot worked after removing the DisplayPort cable |
| Audio | **Owner-confirmed playback** from macOS through Sunshine/Moonlight to CachyOS; final capture settings not recorded |

Host observations: Intel Core **i7-12850HX**, approximately **125 GiB RAM visible to Linux**, QEMU **11.1.1**, libvirt **12.7.0**. These are recorded versions, not minimum requirements or promises about other releases. No exhaustive benchmark, suspend/resume, cold-host-boot, or long-term reliability test was completed.

## Critical finding: disable virtual VGA for the GPU configuration

The installation used virtual VGA/SPICE with no PCI passthrough. After adding the W6600M while retaining virtual VGA, the guest failed to boot reliably; panic text was reported, and console capture showed startup followed by a return to firmware. No readable panic backtrace was preserved.

Changing **only the video model to `none`** allowed the guest to reach the desktop with Metal 3 and the physical display. Keep this setting in the working GPU definition:

```xml
<video>
  <model type="none"/>
</video>
```

This is an observed workaround on this setup, **not proof of the underlying panic mechanism**. Do not re-enable virtual VGA as a headless-display substitute. SPICE input can remain configured, but its console does not show the passed-through GPU output.

## Start here

1. Read [host prerequisites](docs/01-host.md). This record starts from an existing, working VFIO host; it does not pretend the original host provisioning was fully captured.
2. Follow the [Sequoia installation stages](docs/02-install.md), first using virtual video.
3. Review the [W6600M configuration and transition](docs/03-gpu.md).
4. Configure [Sunshine, Moonlight, networking, and optional audio](docs/04-streaming.md).
5. Keep [backups and rollback](docs/05-backup.md), and consult the [observations and troubleshooting notes](docs/06-troubleshooting.md).

The [XML template](configs/sequoia-gpu-only.xml.in) reflects the final GPU-only, no-physical-USB baseline. It deliberately omits the original VM UUID and MAC address and replaces the Apple SMC value with a placeholder. **Do not define it directly.** The [local preparation tool](tools/prepare_definition.py) supplies fresh identity values and reads the SMC argument from your own working XML without printing it. It writes a file only; it never starts, stops, or changes a VM.

```bash
python3 tools/prepare_definition.py --help
```

See the installation guide for the separate installation-stage output. The GPU ROM path, host PCI addresses, QEMU machine version, firmware paths, and system disk path must be checked against your host before any definition is applied.

## Project boundaries

- The old Ventura VM was retained, shut down, with autostart disabled. Never run both while they assign the same physical GPU.
- No installer image, recovery archive, NVRAM dump, serial number, SMBIOS identity, Sunshine pairing database, certificate, private key, or credential belongs in this repository.
- This repository does not grant rights to Apple software or third-party binaries. Obtain and use them under their applicable terms.
- Original documentation and helper code use the [MIT License](LICENSE). Referenced upstream projects retain their own licenses; credit is not permission to redistribute them.
- Issues and Discussions are intended to be disabled. Publishing this record does not establish a support channel.
