# Observations and troubleshooting record

These are observations from this machine, not universal fixes. See [the no-support policy](../SUPPORT.md).

## GPU plus virtual VGA failed

Symptoms included reported panic text in the virt-manager console, a white/blank screen, SSH timeouts, and a return to TianoCore after macOS startup services. The physical monitor initially showed only TianoCore. A panic-related NVRAM entry existed, but its date and content were not established. No useful panic report or readable backtrace was recovered.

Lilu, WhateverGreen, VirtualSMC, RestrictEvents, and VMHide were confirmed loaded. The intended `agdpmod=pikera` argument was active. Disabling virtual VGA while retaining W6600M GPU/audio passthrough allowed desktop boot and Metal 3 reporting. This is the configuration change associated with success; the underlying crash cause remains unproven.

## Boot arguments and verbose mode

Sending the Command+V hotkey through libvirt did not visibly enable verbose mode. Adding `-v` to the system EFI worked after reboot. A direct `sudo nvram boot-args=...` write was denied by macOS; there was no need to weaken security settings to address it.

In the selected EFI, `boot-args` was already listed under `NVRAM → Delete`, and the desired string under `NVRAM → Add`. OpenCore deletes/re-adds that variable during boot. Preserve the other boot arguments and back up the plist before editing. Verify the effective value with `sysctl kern.bootargs` after a virtual-only reboot. See [OpenCore's configuration reference](https://dortania.github.io/docs/latest/Configuration.html).

## EFI mount failed through diskutil

`diskutil mount readOnly` failed, but direct FAT mounting succeeded. Identify the correct EFI partition with `diskutil list` first. On this machine it changed from `disk2s1` to `disk0s1` after auxiliary disks were removed. For inspection only, using **your confirmed partition identifier**:

```bash
sudo mkdir -p /Volumes/EFI-check
sudo /sbin/mount_msdos -o rdonly /dev/disk0s1 /Volumes/EFI-check
```

Do not infer corruption from a single failed mount or format/repair a working EFI without evidence. A read-only mount must be unmounted before remounting writable for a deliberate backed-up edit.

## No panic file

DiagnosticReports contained unrelated user-fault, shutdown-stall, and Jetsam files. An NVRAM panic variable is not a readable backtrace and does not alone date the current failure. Preserve evidence before resets. A blank SPICE console alone is not proof of a panic when a physical GPU is passed through.

## Blurry Moonlight desktop

The overlay showed a 720p HEVC stream with low decoding latency and no network drops. Increasing Moonlight's requested resolution improved clarity. Check actual stream resolution, macOS capture size, and host scaling before increasing bitrate or modifying GPU settings.

## Missing audio devices

Headless macOS reported an empty audio device list. The DisplayPort audio function being assigned does not prove a usable audio output exists with no display connected. BlackHole was proposed; end-to-end sound remained unverified. Follow the [audio notes](04-streaming.md#audio-pending-verification) before treating this as complete.

## Missing USB devices at boot

Explicit physical keyboard/mouse assignments can make the VM depend on those devices being present. The final setup removes those assignments and uses Moonlight input. Preserve the emulated USB controller and inputs unless you have a specific reason to change them.
