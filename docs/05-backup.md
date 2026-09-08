# Backups, migration archive, and rollback

Keep private backups outside the repository. A libvirt XML backup alone does not protect the macOS installation or user data.

The CachyOS-to-Omarchy migration was deliberately performed with the VM data on a separate ZFS pool so the Linux host OS could be replaced without rebuilding the known-good macOS guest.

## Current ZFS layout

The `fury` pool contains dedicated datasets for VM data and migration material. Relevant current paths include:

```text
/fury/migration/cachyos
/fury/vm/macos
/fury/vm/macos/sequoia
/fury/vm/macos/ventura
```

The exact directory/dataset distinction matters: `sequoia` is currently a directory under the `fury/vm/macos` dataset rather than a separate ZFS dataset.

Two useful recovery snapshots were created during the migration:

```text
fury/migration/cachyos@pre-omarchy
fury/vm/macos@pre-omarchy-working
```

These are rollback points on the same storage pool. They are **not substitutes for an independent backup on another physical device**.

Inspect before changing anything:

```bash
sudo zpool status fury
sudo zfs list -r fury
sudo zfs list -t snapshot -r fury
```

Do not run `zpool upgrade fury` or `zfs upgrade` merely because a newly installed host offers newer feature flags. Pool upgrades can reduce rollback compatibility with the previous host environment.

## Migration archive

A private migration archive was retained under:

```text
/fury/migration/cachyos/
```

It includes categories such as:

```text
host-config/
libvirt/
original-macos-sequoia/
MASTER-FILE-LIST.txt
MASTER-SHA256SUMS.txt
RESTORE-RUNBOOK.txt
```

The archive was checksum-verified after the Omarchy installation. Keep this material private; host configuration, XML, firmware variables and recovery notes may expose machine-specific identities, paths or credentials.

A useful integrity pattern is to maintain a file manifest and SHA-256 manifest, then verify them from a known root. Do not publish the private manifest if its filenames reveal sensitive material.

## Working VM components to preserve together

With the guest fully shut off, preserve at least:

- current inactive libvirt XML;
- system QCOW2 and any backing chain;
- VM-specific writable OVMF variables;
- matching OVMF firmware family/version information;
- OpenCore disk/image and EFI configuration;
- exact GPU ROM referenced by the domain;
- network reservation details;
- checksums;
- ownership/permission information;
- host package/kernel/ZFS versions;
- a short restoration runbook.

The current Sequoia VM has private copies of its working XML, writable OVMF variables and W6600M ROM in the migration/storage layout. Those files are intentionally not included in Git.

## ZFS snapshot strategy

Before a risky host-side change, a recursive or targeted ZFS snapshot is a fast local rollback mechanism. Choose snapshot scope deliberately; do not snapshot unrelated large datasets merely out of habit.

Example pattern:

```bash
sudo zfs snapshot fury/vm/macos@before-change
```

Before rolling back, stop every VM using the affected files. A ZFS rollback can destroy newer filesystem state. Inspect snapshots and make an independent copy of anything created after the snapshot that you may need.

## Full VM backup

A separate backup of the system QCOW2 is required to protect APFS volumes, macOS applications and user data from failure of the `fury` pool itself.

Stop the VM for a simple consistent offline copy. Inspect the backing chain first:

```bash
qemu-img info --backing-chain /path/to/macos.qcow2
```

If backing files exist, preserve the complete chain or create a standalone QCOW2-aware copy. Do not use destructive image commands against a live VM disk.

Store at least one verified copy on different physical storage. ZFS mirrors protect against some device failures; they do not protect against accidental deletion, pool-wide corruption, theft, controller failure, or a bad administrative command.

## Rollback rules

1. Shut down the guest before replacing disks, firmware variables, ROMs or persistent PCI layout.
2. Back up the current state before restoring an older state.
3. Restore only the required component and verify VM name, UUID, MAC, paths, permissions and shared GPU ownership.
4. Validate XML before defining it.
5. Persistent PCI topology changes require a full VM stop/start; rebooting macOS does not recreate QEMU devices.
6. If using a virtual-video recovery definition, remove both W6600M functions and their QEMU device-ID override before enabling virtual VGA. Do not recreate the failed dual-video topology.
7. Never start Ventura and Sequoia simultaneously if both definitions assign the same W6600M.
8. Confirm ZFS is imported and mounted before diagnosing a missing VM disk as a libvirt problem.

## Before reinstalling the Linux host

The CachyOS-to-Omarchy migration provides a useful general checklist:

```text
[ ] VM is shut down cleanly
[ ] known-good XML exported
[ ] writable OVMF variables copied
[ ] OpenCore/EFI copied
[ ] system disk(s) accounted for
[ ] GPU ROM copied and checksummed
[ ] network definition/reservation recorded
[ ] host VFIO/ReBAR scripts and systemd units archived
[ ] firewall/libvirt configuration archived
[ ] ZFS pool status healthy
[ ] migration snapshot created
[ ] checksum manifest verified
[ ] restore notes readable without relying on shell history
```

Only then replace the host OS.

## Before publishing changes

Never add generated private XML, firmware variables, complete EFI, Apple SMC values, ROMs, disk images, Sunshine configuration/credentials, BetterDisplay private configuration, keys, pairing state, diagnostic reports containing serials, or private backups to Git.

The `.gitignore` is a convenience, not a security boundary. Inspect every staged file and the complete commit diff before publishing.
