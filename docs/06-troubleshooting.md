# Observations and troubleshooting record

These are observations from this machine, not universal fixes. Preserve evidence before changing multiple variables at once. See [the no-support policy](../SUPPORT.md).

## GPU plus virtual VGA failed

Symptoms included reported panic text in the virt-manager console, a white/blank screen, SSH timeouts, and a return to TianoCore after macOS startup services. No useful panic report or readable backtrace was recovered.

Lilu, WhateverGreen, VirtualSMC, RestrictEvents, and VMHide were confirmed loaded. The intended `agdpmod=pikera` argument was active.

Disabling virtual VGA while retaining W6600M GPU/audio passthrough allowed desktop boot and Metal 3 reporting. Later QEMU PCI inspection confirmed the W6600M as the guest's only VGA controller.

Working XML:

```xml
<video>
  <model type="none"/>
</video>
```

This is the configuration change associated with success; the exact underlying crash mechanism remains unproven.

## VM disks disappear after host migration or reboot

If libvirt reports missing VM disks, NVRAM or ROM paths under `/fury`, check ZFS before editing the VM definition:

```bash
sudo zpool status fury
sudo zfs list -r fury
mount | grep '/fury'
```

The current Omarchy host explicitly requires ZFS import/mount services before libvirt. A service-ordering failure can look like a libvirt storage problem even when the VM definition is correct.

Check:

```bash
systemctl status zfs-import-cache.service zfs-mount.service
systemctl status libvirtd.service
```

Do not recreate disks or redefine paths until you know the pool is imported.

## W6600M is not owned by VFIO

Before starting macOS:

```bash
lspci -nnk -s 03:00.0
lspci -nnk -s 03:00.1
```

Both functions should report `Kernel driver in use: vfio-pci` in the current setup.

Also verify the ReBAR state:

```bash
sudo lspci -vvv -s 03:00.0 | grep -A4 -E 'Region|Resizable BAR'
```

The known-good BAR0 size is 256 MiB. The current host configures ReBAR and VFIO through `w6600m-vfio.service` before libvirt starts.

If the service fails, diagnose that first rather than repeatedly starting the VM.

## Guest gets an IP but Internet/DHCP behavior is inconsistent

The macOS guest uses libvirt's `virbr0` NAT network. UFW can interfere with DHCP/DNS/forwarding even when host-to-guest communication partly works.

Useful checks:

```bash
virsh -c qemu:///system net-list --all
virsh -c qemu:///system net-dhcp-leases default
ip addr show virbr0
sudo ufw status numbered
```

The current portable forwarding rule is based on the libvirt bridge/subnet rather than a specific Wi-Fi device:

```bash
sudo ufw route allow in on virbr0 from 192.168.122.0/24
```

DHCP also requires client UDP 68 to server UDP 67 on `virbr0`:

```bash
sudo ufw allow in on virbr0 proto udp from any port 68 to any port 67
```

Adjust to your actual subnet and firewall policy.

## Sunshine captures the wrong display

With BetterDisplay running, the current expected log is similar to:

```text
Detected display: Moonlight (id: 4128837) connected: true
Configuring selected display (4128837) to stream
```

If BetterDisplay is quit, the software virtual display disappears and Sunshine can fall back to another target such as `Built-in Display`.

Recovery sequence:

1. Start BetterDisplay.
2. Confirm the `Moonlight` virtual display exists.
3. Restart Sunshine.
4. Inspect the Sunshine log for the selected display.

Do not add a virtual VGA adapter to the VM to solve this problem.

## Moonlight requests 120 FPS but receives about 90 FPS

At 1920x1200 the current setup settles around 89.5-89.6 FPS when Moonlight requests 120 FPS. Despite that ceiling, the observed stream had zero network/jitter drops, approximately 1 ms network latency, ~0.4 ms decode time and ~0.4 ms frame queue time.

This is not evidence of a network bottleneck. The remaining perceived pointer/typing latency is larger than those client-side numbers imply and is still under investigation.

Before changing VFIO, ZFS or firewall settings, compare codecs and frame-rate requests while watching Moonlight's statistics overlay with **Ctrl+Alt+Shift+S**.

## VideoToolbox H.264 probe warning

Sunshine's H.264 availability test can initially emit a VideoToolbox compression-session error suggesting `-allow_sw 1`, while the subsequent availability test still reports H.264.

The current explicit settings are:

```text
encoder = videotoolbox
vt_software = disabled
vt_realtime = enabled
```

HEVC currently works cleanly. Do not enable software encoding merely to suppress the H.264 probe warning unless you are deliberately testing software encoding and understand the performance cost.

## macOS unexpectedly shuts down

One event was initially mistaken for sleep. `pmset` showed sleep already disabled, and the macOS power log contained no corresponding Sleep/Wake cycle.

Host QEMU/libvirt logs showed a guest-originated orderly shutdown rather than libvirt sending QEMU SIGTERM.

A narrow macOS Unified Log window identified BetterDisplay sending the Apple Event for the shutdown dialog:

```text
BetterDisplay ... AESendMessage(aevt,rsdn ... target='psn '[loginwindow])
loginwindow ... Received a kAEShowShutdownDialog
loginwindow ... logoutType:3 - Shutdown
```

BetterDisplay had no custom shortcuts recorded. Sunshine/Moonlight was active, but the cause of BetterDisplay sending the event has **not** been established.

If this recurs and the shutdown dialog is visible, preserve the system state and capture a narrow Unified Log window immediately around the event instead of allowing repeated shutdowns and collecting hours of logs.

The current always-on power settings are:

```bash
sudo pmset -a sleep 0 disksleep 0 powernap 0
```

`powerbutton` is not a valid `pmset` setting in this environment; do not retry old examples that use `sudo pmset -a powerbutton 0`.

## Boot arguments and verbose mode

Sending Command+V through libvirt did not visibly enable verbose mode. Adding `-v` to the OpenCore EFI worked after reboot. A direct `sudo nvram boot-args=...` write was denied by macOS; there was no need to weaken security settings.

In the selected EFI, `boot-args` was already listed under `NVRAM -> Delete`, and the desired string under `NVRAM -> Add`. OpenCore deletes/re-adds that variable during boot. Preserve the other arguments and back up the plist before editing.

Verify with:

```bash
sysctl kern.bootargs
```

## EFI mount failed through diskutil

`diskutil mount readOnly` failed during earlier testing, while direct FAT mounting succeeded. Identify the correct EFI partition with `diskutil list` first; disk identifiers can change when auxiliary disks are removed.

For inspection only, using **your confirmed partition identifier**:

```bash
sudo mkdir -p /Volumes/EFI-check
sudo /sbin/mount_msdos -o rdonly /dev/disk0s1 /Volumes/EFI-check
```

Do not infer corruption from one failed mount or format/repair a working EFI without evidence.

## No panic file

DiagnosticReports contained unrelated user-fault, shutdown-stall, and Jetsam files. An NVRAM panic variable is not a readable backtrace and does not alone date a current failure.

A blank SPICE console is also not proof of a panic when a physical GPU is passed through and virtual video is disabled.

## Blurry Moonlight desktop

An early overlay showed a 720p HEVC stream with low decoding latency and no network drops. Increasing Moonlight's requested resolution improved clarity.

Check actual stream resolution, BetterDisplay virtual-display size, macOS scaling and host scaling before simply increasing bitrate.

The current working virtual display is 1920x1200.

## Missing audio devices

Early headless macOS testing reported an empty audio-device list. The DisplayPort audio PCI function being assigned does not guarantee a usable output with no physical display.

End-to-end playback through Sunshine/Moonlight was subsequently confirmed. The current repository intentionally avoids claiming a specific virtual-audio recipe unless it has been independently recorded and verified.

## Missing USB devices at boot

Explicit physical keyboard/mouse assignments can make VM startup depend on those devices being present. The current setup removes those assignments and uses Moonlight input.

Preserve the emulated USB controller and inputs unless you have a specific reason to change them.
