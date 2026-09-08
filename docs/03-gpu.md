# W6600M passthrough

The working Ventura definition provided two physical PCI assignments and an OpenCore-compatible guest device-ID override. The final Sequoia configuration retained those settings and now runs successfully on the Omarchy host.

| Item | Observed value |
|---|---|
| Physical GPU | `0000:03:00.0`, `1002:73e1` |
| Physical audio | `0000:03:00.1`, `1002:ab28` |
| Guest GPU slot | `0000:00:05.0`, multifunction enabled |
| Guest audio slot | `0000:00:05.1` |
| Host binding | Both functions use `vfio-pci` before guest startup |
| Assignment mode | `managed='no'`, inherited from the working setup |
| Guest device-ID override | `29667` decimal = `0x73e3` |
| ROM | Private, existing `w6600m-73e3.rom` |
| Virtual video | `none` |
| BAR0 ReBAR | **256 MiB** before VFIO binding |
| BAR2 ReBAR | **256 MiB** observed |

The override applies to `hostdev0`, the GPU in the template. Reordering or inserting host devices can change auto-generated aliases; inspect the effective QEMU configuration and confirm that the override still targets the GPU if you change device order. Never publish native QEMU output without removing private values.

## ReBAR and VFIO binding on Omarchy

The current host runs a systemd oneshot service before libvirt. Its job is to configure the W6600M's BAR sizing and then bind both GPU and HDMI/DP audio functions to VFIO.

The working result is:

```text
03:00.0 ... Kernel driver in use: vfio-pci
03:00.1 ... Kernel driver in use: vfio-pci
```

and:

```text
Physical Resizable BAR
    BAR 0: current size: 256MB
    BAR 2: current size: 256MB
```

Verify after boot with:

```bash
lspci -nnk -s 03:00.0
lspci -nnk -s 03:00.1
sudo lspci -vvv -s 03:00.0 | grep -A4 -E 'Region|Resizable BAR'
```

The current service is named:

```text
w6600m-vfio.service
```

and runs before `libvirtd.service` / `virtqemud.service`. The underlying script is machine-specific and should not be copied blindly to another GPU without understanding PCI resource resizing and driver rebinding.

The important design rule is **ordering**: configure BAR sizing first, then bind to VFIO, then allow libvirt to start the guest.

## Why 256 MiB matters here

On this machine the W6600M advertises multiple supported BAR0 sizes, including 256 MiB through 8 GiB. The known-good macOS VFIO baseline uses a **256 MiB BAR0**. Larger is not automatically better for this guest. Preserve the working value unless you are deliberately testing another layout and have a rollback path.

## Final guest topology

The working libvirt XML uses:

```xml
<video>
  <model type="none"/>
</video>
```

QEMU `info pci` confirmed that the only VGA controller presented to the guest is the passed-through AMD device:

```text
VGA controller: PCI device 1002:73e3
id "hostdev0"
```

There is no VMware/QXL/virtio virtual VGA device in the current guest. This is important because the earlier dual-video configuration was associated with failed macOS boots.

The W6600M audio function is presented adjacent to the GPU as function 1.

## Prepare or review a definition

Stop the guest before replacing its persistent definition. Export the inactive XML to a private path first and validate any generated replacement.

If using this repository's helper, review the result rather than treating it as authoritative for a different host. Preserve custom settings you added yourself.

The current Omarchy VM also references storage on the ZFS pool, so confirm all paths exist before attempting to start the domain.

Useful checks:

```bash
virsh -c qemu:///system domblklist macos-sequoia-zfs-test --details
virsh -c qemu:///system dumpxml macos-sequoia-zfs-test | \
  grep -nE 'loader|nvram|source file=|hostdev|rom file=|x-pci-device-id|<video>'
```

## Verify in macOS

```bash
system_profiler SPDisplaysDataType
sysctl kern.bootargs
sudo kmutil showloaded | grep -Ei 'Lilu|WhateverGreen|VirtualSMC|VMHide|RestrictEvents'
```

Observed graphics fields:

```text
AMD Radeon Navi23
VRAM (Total): 8 GB
Device ID: 0x73e3
Metal Support: Metal 3
```

These establish guest recognition and Metal support, not a full GPU stress test.

Observed loaded kexts in the original validation included Lilu, WhateverGreen, VirtualSMC, RestrictEvents, and VMHide. They came from the selected upstream EFI; this repository neither supplies nor independently audits them.

The last verified boot arguments were:

```text
-v keepsyms=1 debug=0x100 agdpmod=pikera
```

The debug flags were retained during troubleshooting. Removing `-v` later is optional; preserve the working argument set in a backup before changing it.

## Headless operation

Do not add virtual VGA just to obtain a remote desktop. The current guest uses the passed-through W6600M as its only graphics adapter and BetterDisplay supplies the software virtual screen captured by Sunshine.

See [04-streaming.md](04-streaming.md) for the BetterDisplay/Sunshine/Moonlight path.

## Optional physical USB

Individual keyboard/mouse passthrough worked during early testing and was later removed after Moonlight input was working. The USB controller itself was not passed through.

Explicit physical USB assignments can make VM startup depend on those devices being present. The final template deliberately avoids that dependency.
