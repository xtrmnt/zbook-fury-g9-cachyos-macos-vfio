# Sequoia installation stages

This procedure records the stages that worked. It assumes the [host prerequisites](01-host.md), access to the referenced upstream EFI/recovery tools, and permission to use your software. No Proxmox host-install script should be run on CachyOS.

## 1. Prepare separate storage

Use a new VM name and directory. Preserve the Ventura VM and its disks. The build used:

```text
/var/lib/libvirt/images/macos-sequoia/
  OpenCore-Sequoia.img          # private copy of the upstream raw OpenCore disk
  macos-sequoia-vfio.qcow2      # new 256 GiB system disk
  OVMF_VARS.fd                 # independent writable firmware variables
  Sequoia-Recovery.img         # temporary recovery media
```

Only create a new disk when the path does not exist. `qemu-img create` must not be rerun on an installed system disk. Check the destination first, then for a genuinely new build:

```bash
sudo qemu-img create -f qcow2 /var/lib/libvirt/images/macos-sequoia/macos-sequoia-vfio.qcow2 256G
```

The directory must already exist with appropriate libvirt access. Obtain the OpenCore image from [OSX-PROXMOX](https://github.com/luchina-gabriel/OSX-PROXMOX). The downloaded `.iso` in this build was actually an approximately 96 MiB MBR/FAT raw disk, not an ISO9660 CD image. Verify its format with `qemu-img info`; attach it as `raw` only if that is what your copy contains. Use a separate copy for the VM rather than modifying the downloaded master.

## 2. Obtain recovery media from Apple

Use upstream [OpenCore macrecovery](https://github.com/acidanthera/OpenCorePkg/tree/master/Utilities/macrecovery) and the [Dortania Linux installation guide](https://dortania.github.io/OpenCore-Install-Guide/installer-guide/linux-install.html). The Sequoia query used was:

```bash
python3 macrecovery.py -b Mac-7BA5B2D9E42DDD94 -m 00000000000000000 download
```

Retain both the downloaded DMG and chunklist and require successful verification. Queries and Apple's available recovery products can change; confirm that the resulting installer actually offers Sequoia.

The build used a new FAT32 disk image containing:

```text
com.apple.recovery.boot/BaseSystem.dmg
com.apple.recovery.boot/BaseSystem.chunklist
```

It was attached as a third SATA disk. These are recovery downloads, not a full offline installer. The guest needs networking to finish installation. The recovery-copy disk was writable because this libvirt setup rejected a read-only SATA hard disk; the original verified download was preserved separately.

## 3. Generate the installation definition locally

The helper reads only the Apple SMC argument from an existing working macOS XML. Supply your own private source file; do not commit it. It does not copy the old UUID, MAC, disk paths, or host devices.

From this repository's root on CachyOS:

```bash
mkdir -p local
virsh -c qemu:///system dumpxml --inactive macos-ventura-vfio > local/ventura.xml
python3 tools/prepare_definition.py \
  --source-xml local/ventura.xml \
  --stage install \
  --output local/sequoia-install.xml
virt-xml-validate local/sequoia-install.xml domain
```

Review the output's paths, memory, CPU features, controllers, and networking before using it. It requests a fresh UUID and MAC and uses a separate NVRAM path. Libvirt initializes that variables file from the firmware template if it does not already exist. Do not substitute Ventura's writable NVRAM file.

The installation stage has **virtual VGA + SPICE**, USB emulated keyboard/tablet, no PCI/physical USB passthrough, OpenCore boot order 1, and three SATA disks. It keeps 32 GiB RAM, 8 vCPUs, Skylake-Client with `invtsc`, and VMXNET3 on `default` NAT.

Check that no existing domain already uses the new name before defining it. After review:

```bash
virsh -c qemu:///system define --validate local/sequoia-install.xml
virsh -c qemu:///system start macos-sequoia-vfio
```

Open the console in Virtual Machine Manager. Select recovery in OpenCore, erase **only the new 256 GiB system disk** as APFS with GUID partitioning, and install Sequoia. The guest may display the disk as approximately **274.9 GB decimal**. Choose the macOS installer entry during installation restarts until setup completes.

## 4. Install EFI on the system disk

The owner installed the upstream **AMD-5000-6000-series EFI** onto the system disk's EFI partition. This is separate from the temporary OpenCore disk. Obtain that package from its author and follow its own instructions; this repository does not bundle or silently modify it.

Use `diskutil list` to identify the system disk before mounting EFI. Disk numbers changed after auxiliary disks were removed. Verify these paths on the mounted EFI:

```text
EFI/BOOT/BOOTx64.efi
EFI/OC/OpenCore.efi
EFI/OC/config.plist
```

The selected configuration had `SecureBootModel=Disabled`, signed-DMG loading, and `agdpmod=pikera`. Machine identifiers remain private. Do not assume a successful reboot proves which EFI was used while the temporary OpenCore disk is still attached.

Shut down the guest, detach the temporary OpenCore and recovery devices **without deleting their files**, and boot from the system disk with virtual video still enabled. A desktop boot at this stage confirmed that the system EFI worked independently.

## 5. Add the W6600M only after independent boot works

Follow [the GPU transition](03-gpu.md). Do not carry virtual VGA into the working GPU configuration. Keep your installation-stage XML and storage backups available for rollback.
