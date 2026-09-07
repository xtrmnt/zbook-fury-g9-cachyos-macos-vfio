# Host prerequisites and scope

This build began with a working CachyOS VFIO host and an existing Ventura VM. Exact BIOS revision, bootloader configuration, kernel build, original ROM acquisition process, and every earlier VFIO change were not recorded. This is therefore a staged adaptation guide, not a complete bare-metal provisioning recipe.

## Observed hardware and bindings

- HP ZBook Fury G9 with Intel Core i7-12850HX.
- AMD Radeon PRO W6600M, physical GPU ID `1002:73e1`, at `0000:03:00.0`.
- GPU audio function `1002:ab28`, at `0000:03:00.1`.
- Both functions were already bound to `vfio-pci` before guest startup.
- The host remained usable while the W6600M was assigned to the guest.

Inspect your host rather than assuming these addresses:

```bash
lspci -nnk -s 03:00
virsh -c qemu:///system list --all
qemu-system-x86_64 --version
virsh --version
cat /sys/devices/system/clocksource/clocksource0/current_clocksource
```

The observed clocksource was `tsc`. `invtsc` was retained from the working Ventura definition; it is not a cure for an unstable host clock.

Use the [Linux VFIO documentation](https://docs.kernel.org/driver-api/vfio.html) and your distribution documentation to verify IOMMU groups, group ownership, device isolation, and binding. Do not copy PCI addresses or ACS/kernel overrides from another machine without understanding their consequences. This repository does not change host bindings or apply kernel overrides automatically.

## Firmware and files

The tested firmware paths were:

```text
/usr/share/edk2/x64/OVMF_CODE.4m.fd
/usr/share/edk2/x64/OVMF_VARS.4m.fd
```

Each VM requires a separate writable variables file. Keep the code/template sizes and firmware family matched. The template uses `pc-q35-11.1`; check that your installed QEMU supports it before defining a VM.

The template references `/var/lib/libvirt/vbios/w6600m-73e3.rom`. This was an existing working ROM from the Ventura setup. It is **not distributed** here, and its exact extraction/modification procedure was not recorded. A filename ending in `73e3` does not establish its contents or compatibility. Preserve your own known-working ROM, verify its provenance, and keep a private checksum.

## Existing VMs

Before changes, save the existing inactive XML and firmware variables with the VM stopped. Keep a disk backup separately. The owner retained Ventura with autostart disabled:

```bash
virsh -c qemu:///system dominfo macos-ventura-vfio
virsh -c qemu:///system autostart macos-ventura-vfio --disable
```

Only use that command if it is the correct domain name on your host. Never start two VMs that assign the same physical GPU.
