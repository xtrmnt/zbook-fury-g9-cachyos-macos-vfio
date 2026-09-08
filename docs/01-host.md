# Host prerequisites and current scope

This build began with a working CachyOS VFIO host and an existing Ventura VM. It has since been migrated to **Omarchy** without rebuilding the macOS Sequoia guest. The repository therefore documents two host states:

- **CachyOS**: original validated baseline.
- **Omarchy**: current host implementation.

Exact BIOS revision history, every early VFIO change, and the original GPU-ROM acquisition process were not fully recorded. Treat this as a machine-specific adaptation record, not a complete bare-metal installer.

## Observed hardware

- HP ZBook Fury G9 with Intel Core i7-12850HX.
- AMD Radeon PRO W6600M, physical GPU ID `1002:73e1`, at `0000:03:00.0`.
- GPU audio function `1002:ab28`, at `0000:03:00.1`.
- The Intel integrated GPU remains available to the Linux host.
- Both W6600M functions are bound to `vfio-pci` before guest startup.

Inspect your own machine rather than assuming these addresses:

```bash
lspci -nnk -s 03:00.0
lspci -nnk -s 03:00.1
virsh -c qemu:///system list --all
qemu-system-x86_64 --version
virsh --version
```

Use the [Linux VFIO documentation](https://docs.kernel.org/driver-api/vfio.html) and your distribution documentation to verify IOMMU groups, device isolation, ownership, and binding. Do not copy PCI addresses or ACS/kernel overrides from another machine without understanding the consequences.

## Current Omarchy kernel and ZFS baseline

The current known-good host is booted on the Arch LTS kernel:

```text
linux-lts 6.18.46-1-lts
```

with OpenZFS:

```text
zfs-2.4.4-1
zfs-kmod-2.4.4-1
```

The normal Arch kernel is also installed as a fallback, but the current ZFS/VFIO validation is on the LTS kernel.

Useful checks:

```bash
uname -r
dkms status
modinfo zfs | grep -E '^(filename|version|vermagic):'
zfs version
```

The Omarchy bootloader is Limine using UKIs. The current installation has both normal and LTS UKIs present. Do not assume systemd-boot commands or paths just because the host is Arch-based.

## ZFS storage

The current Omarchy host stores VM and migration data on the `fury` pool, built from two NVMe mirrors. Relevant datasets include:

```text
fury/migration/cachyos
fury/vm/macos
fury/vm/windows
```

The macOS VM currently lives under:

```text
/fury/vm/macos/sequoia/
```

Before libvirt can start the guest, the pool must be imported and its datasets mounted.

The following services are enabled so ZFS imports and mounts during boot:

```text
zfs-import-cache.service
zfs-mount.service
zfs.target
```

Verify with:

```bash
systemctl is-enabled zfs-import-cache.service zfs-mount.service zfs.target
sudo zpool status fury
sudo zfs get -r mounted fury
```

A valid `/etc/zfs/zpool.cache` exists and contains the `fury` pool. If `zpool status fury` reports that the pool does not exist after boot, investigate service ordering rather than redefining the VM or recreating storage.

## Service ordering

The current host explicitly orders libvirt after three prerequisites:

- ZFS pool import;
- ZFS filesystem mount;
- W6600M ReBAR configuration and VFIO binding.

The libvirt override is conceptually:

```ini
[Unit]
Requires=zfs-import-cache.service
Requires=zfs-mount.service
Requires=w6600m-vfio.service

After=zfs-import-cache.service
After=zfs-mount.service
After=w6600m-vfio.service
```

This prevents libvirt from attempting to start a guest whose disk/NVRAM paths are absent or whose GPU is still owned by the host driver.

The W6600M service is a oneshot unit that runs before libvirt and leaves the GPU/audio functions bound to `vfio-pci`.

Verify effective ordering with:

```bash
SYSTEMD_PAGER=cat systemctl show libvirtd.service -p Requires --value | tr ' ' '\n'
SYSTEMD_PAGER=cat systemctl show libvirtd.service -p After --value | tr ' ' '\n'
```

## Firmware

The current tested firmware paths on Omarchy are:

```text
/usr/share/edk2/x64/OVMF_CODE.4m.fd
/usr/share/edk2/x64/OVMF_VARS.4m.fd
```

Each VM requires a separate writable variables file. Keep the code/template sizes and firmware family matched. The current working definition uses `pc-q35-11.1`; verify that your installed QEMU supports that machine type before defining the VM.

The private GPU ROM currently lives with the VM data under the ZFS dataset. It is **not distributed** here, and its exact extraction/modification procedure was not recorded. Preserve your known-working ROM privately and keep a checksum.

## Existing VMs and migration state

The original Ventura VM was retained as a rollback source with autostart disabled. Never start two VMs that assign the same physical GPU.

The Sequoia guest was migrated by preserving the known-good disk, writable OVMF variables, ROM, and libvirt definition, then recreating the host-side virtualization stack on Omarchy.

The migration archive also contains private host configuration and a restore runbook. Those private files are not suitable for publication because they can include machine-specific paths, identities, and recovery material.

## Current validation boundary

The following currently work on Omarchy:

- ZFS import and manual VM storage access;
- W6600M 256 MiB ReBAR setup;
- VFIO binding of GPU and audio functions;
- libvirt networking;
- macOS Sequoia boot from the migrated disk;
- W6600M Metal 3;
- BetterDisplay virtual monitor;
- Sunshine/Moonlight streaming and audio.

A full powered-off host boot followed by unattended ZFS import, VFIO/ReBAR setup, VM start, BetterDisplay startup, Sunshine startup, and Moonlight reconnection is still a validation item rather than a documented guarantee.
