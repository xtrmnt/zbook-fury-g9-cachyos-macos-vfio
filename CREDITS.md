# Credits, provenance, and third-party rights

This repository contributes the machine-specific build record, a sanitized libvirt template, a local preparation helper, and observations from testing. It does not claim authorship of the bootloader, drivers, virtualization stack, streaming software, or firmware.

| Project / authors | Contribution to this setup | Source / rights information |
|---|---|---|
| **Gabriel Luchina and OSX-PROXMOX contributors** | Initial OpenCore image, VM-oriented EFI, and the AMD 5000/6000-series EFI selected by the owner | [OSX-PROXMOX](https://github.com/luchina-gabriel/OSX-PROXMOX). Follow the project's own notices and each bundled component's license. No EFI binaries are copied here. |
| **Acidanthera and OpenCore contributors** | OpenCore bootloader, configuration tooling, and `macrecovery.py` | [OpenCorePkg](https://github.com/acidanthera/OpenCorePkg) and its license notices |
| **Acidanthera contributors** | Graphics and platform kexts used by the selected EFI | [Lilu](https://github.com/acidanthera/Lilu), [WhateverGreen](https://github.com/acidanthera/WhateverGreen), [VirtualSMC](https://github.com/acidanthera/VirtualSMC), [RestrictEvents](https://github.com/acidanthera/RestrictEvents); licenses remain upstream |
| **XLNC / AppleMCEReporterDisabler contributors** | Codeless AppleMCEReporterDisabler entry in the selected EFI; its bundled Info.plist identifies `org.xlnc.disabler.MCEReporter` | Obtained through [OSX-PROXMOX](https://github.com/luchina-gabriel/OSX-PROXMOX). An authoritative standalone source revision/license was not established, so this component is not redistributed. |
| **Carnations-Botanica / VMHide contributors** | VMHide kext in the selected EFI | [VMHide](https://github.com/Carnations-Botanica/VMHide) and its source notices |
| **Dortania contributors** | OpenCore installation, Linux recovery-media preparation, and troubleshooting references | [OpenCore Install Guide](https://dortania.github.io/OpenCore-Install-Guide/) and [guide source](https://github.com/dortania/OpenCore-Install-Guide) |
| **QEMU, Linux KVM/VFIO, and libvirt contributors** | Virtualization, PCI/USB assignment, VM definitions, and NAT networking | [QEMU](https://www.qemu.org/), [Linux VFIO documentation](https://docs.kernel.org/driver-api/vfio.html), [libvirt](https://libvirt.org/) |
| **TianoCore / EDK II contributors** | OVMF UEFI firmware | [EDK II](https://github.com/tianocore/edk2); firmware package and component licenses apply |
| **CachyOS and Arch Linux contributors** | Linux host distribution and package ecosystem | [CachyOS](https://cachyos.org/), [Arch Linux](https://archlinux.org/) |
| **virt-manager contributors** | Host-side VM management interface | [virt-manager](https://virt-manager.org/) |
| **LizardByte / Sunshine contributors** | macOS streaming host | [Sunshine](https://github.com/LizardByte/Sunshine), [documentation](https://docs.lizardbyte.dev/projects/sunshine/latest/) |
| **Moonlight contributors** | CachyOS streaming client | [Moonlight Qt](https://github.com/moonlight-stream/moonlight-qt), [setup guide](https://github.com/moonlight-stream/moonlight-docs/wiki/Setup-Guide) |
| **Existential Audio / BlackHole contributors** | Virtual audio device recommended during setup; playback is now owner-confirmed, but use of BlackHole in the final path has not been separately confirmed | [BlackHole](https://github.com/ExistentialAudio/BlackHole), [official download](https://existential.audio/blackhole/) |
| **Homebrew contributors** | Optional package installation method for BlackHole | [Homebrew](https://brew.sh/), [BlackHole cask](https://formulae.brew.sh/cask/blackhole-2ch) |

The earlier working Ventura VM supplied the machine's known-good Q35/OVMF/CPU and GPU-assignment layout. The Sequoia VM was created separately; the Ventura disks and definition were retained.

## Version provenance

The local OSX-PROXMOX checkout inspected during preparation was at commit [`252186c71723488559f535cc307e8b6daab93cc3`](https://github.com/luchina-gabriel/OSX-PROXMOX/tree/252186c71723488559f535cc307e8b6daab93cc3). This identifies that checkout only. The AMD EFI was subsequently installed by the owner inside macOS, and its exact downloaded artifact checksum was not recorded. Do not treat that checkout commit as proof of every installed binary's origin.

The initial upstream image was described by its source as OpenCore 1.0.7. Loaded kext versions were observed through `kmutil showloaded`: Lilu 1.7.2, WhateverGreen 1.7.0, VirtualSMC 1.3.7, RestrictEvents 1.1.6, and VMHide 2.0.0. AppleMCEReporterDisabler 1.2 was an EFI configuration comment, not independently verified as a loaded executable. Sunshine and Moonlight application versions were not recorded.

## Redistribution policy

Only original prose, helper code, and a sanitized configuration template are included. No upstream source implementation, complete upstream `config.plist`, binary, logo, screenshot, ROM, macOS recovery download, firmware variables, or Apple SMC key is bundled.

The repository's MIT license applies only to its original material. Each linked project retains its own copyright and license. Check the license attached to the exact revision you obtain; attribution alone does not authorize copying or relicensing. Preserve upstream notices if you redistribute permitted components in your own project. No license grant is asserted for the vendor GPU ROM or Apple software.
