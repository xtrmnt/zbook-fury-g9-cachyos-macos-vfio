# Credits, provenance, and third-party rights

This repository contributes the machine-specific build record, a sanitized libvirt template, a local preparation helper, and observations from testing. It does not claim authorship of the bootloader, drivers, virtualization stack, streaming software, display software, firmware, Linux distributions, or ZFS.

| Project / authors | Contribution to this setup | Source / rights information |
|---|---|---|
| **Gabriel Luchina and OSX-PROXMOX contributors** | Initial OpenCore image, VM-oriented EFI, and the AMD 5000/6000-series EFI selected by the owner | [OSX-PROXMOX](https://github.com/luchina-gabriel/OSX-PROXMOX). Follow the project's notices and each bundled component's license. No EFI binaries are copied here. |
| **Acidanthera and OpenCore contributors** | OpenCore bootloader, configuration tooling, and `macrecovery.py` | [OpenCorePkg](https://github.com/acidanthera/OpenCorePkg) and its license notices |
| **Acidanthera contributors** | Graphics and platform kexts used by the selected EFI | [Lilu](https://github.com/acidanthera/Lilu), [WhateverGreen](https://github.com/acidanthera/WhateverGreen), [VirtualSMC](https://github.com/acidanthera/VirtualSMC), [RestrictEvents](https://github.com/acidanthera/RestrictEvents); licenses remain upstream |
| **XLNC / AppleMCEReporterDisabler contributors** | Codeless AppleMCEReporterDisabler entry in the selected EFI | Obtained through [OSX-PROXMOX](https://github.com/luchina-gabriel/OSX-PROXMOX). An authoritative standalone source revision/license was not established, so this component is not redistributed. |
| **Carnations-Botanica / VMHide contributors** | VMHide kext in the selected EFI | [VMHide](https://github.com/Carnations-Botanica/VMHide) and its source notices |
| **Dortania contributors** | OpenCore installation, Linux recovery-media preparation, and troubleshooting references | [OpenCore Install Guide](https://dortania.github.io/OpenCore-Install-Guide/) and [guide source](https://github.com/dortania/OpenCore-Install-Guide) |
| **QEMU, Linux KVM/VFIO, and libvirt contributors** | Virtualization, PCI/USB assignment, VM definitions, and NAT networking | [QEMU](https://www.qemu.org/), [Linux VFIO documentation](https://docs.kernel.org/driver-api/vfio.html), [libvirt](https://libvirt.org/) |
| **TianoCore / EDK II contributors** | OVMF UEFI firmware | [EDK II](https://github.com/tianocore/edk2); firmware package and component licenses apply |
| **CachyOS contributors** | Original validated Linux host distribution | [CachyOS](https://cachyos.org/) and its project/package notices |
| **Omarchy contributors** | Current Linux host environment | [Omarchy](https://omarchy.org/) and its project/package notices |
| **Arch Linux contributors** | Package ecosystem underlying the current host | [Arch Linux](https://archlinux.org/) and package-specific licenses |
| **OpenZFS contributors** | `fury` storage pool, VM/migration datasets, snapshots, and host-migration persistence | [OpenZFS](https://openzfs.org/) and [OpenZFS on GitHub](https://github.com/openzfs/zfs) |
| **virt-manager contributors** | Host-side VM management interface | [virt-manager](https://virt-manager.org/) |
| **LizardByte / Sunshine contributors** | macOS streaming host and VideoToolbox capture/encoding path | [Sunshine](https://github.com/LizardByte/Sunshine) and its documentation |
| **Moonlight contributors** | Linux streaming client | [Moonlight Qt](https://github.com/moonlight-stream/moonlight-qt) and [Moonlight documentation](https://github.com/moonlight-stream/moonlight-docs) |
| **BetterDisplay / waydabber** | macOS virtual `Moonlight` display used as the current headless Sunshine capture target | [BetterDisplay](https://github.com/waydabber/BetterDisplay); software and license remain upstream |
| **Existential Audio / BlackHole contributors** | Virtual audio device considered during troubleshooting; final use is not asserted | [BlackHole](https://github.com/ExistentialAudio/BlackHole) and [official site](https://existential.audio/blackhole/) |
| **Homebrew contributors** | Optional macOS package installation mechanism used during experimentation | [Homebrew](https://brew.sh/) |

The earlier working Ventura VM supplied the machine's known-good Q35/OVMF/CPU and GPU-assignment layout. The Sequoia VM was created separately and later migrated intact from CachyOS to Omarchy.

## Version provenance

The local OSX-PROXMOX checkout inspected during preparation was at commit [`252186c71723488559f535cc307e8b6daab93cc3`](https://github.com/luchina-gabriel/OSX-PROXMOX/tree/252186c71723488559f535cc307e8b6daab93cc3). This identifies that checkout only. The AMD EFI was subsequently installed by the owner inside macOS, and its exact downloaded artifact checksum was not recorded. Do not treat that checkout commit as proof of every installed binary's origin.

The initial upstream image was described by its source as OpenCore 1.0.7. Loaded kext versions were observed through `kmutil showloaded`: Lilu 1.7.2, WhateverGreen 1.7.0, VirtualSMC 1.3.7, RestrictEvents 1.1.6, and VMHide 2.0.0. AppleMCEReporterDisabler 1.2 was an EFI configuration comment, not independently verified as a loaded executable.

Current streaming/display versions recorded during the Omarchy phase include:

```text
BetterDisplay 4.3.6 (build 50119)
Sunshine 2026.516.143833
Moonlight Qt 6.1.0
```

These are observations from the tested machine, not minimum or recommended versions. In particular, software should be reviewed for newer security/stability releases before reproducing an old snapshot exactly.

The current Omarchy host validation was performed on Linux LTS 6.18.46-1-lts with OpenZFS 2.4.4. Package versions will naturally move over time.

## Redistribution policy

Only original prose, helper code, and sanitized configuration templates are included. No upstream source implementation, complete upstream `config.plist`, binary, logo, screenshot, ROM, macOS recovery download, firmware variables, Apple SMC key, Sunshine pairing database, BetterDisplay private configuration, or credentials are bundled.

The repository's MIT license applies only to its original material. Each linked project retains its own copyright and license. Check the license attached to the exact revision you obtain; attribution alone does not authorize copying or relicensing. Preserve upstream notices if you redistribute permitted components in your own project. No license grant is asserted for the vendor GPU ROM or Apple software.
