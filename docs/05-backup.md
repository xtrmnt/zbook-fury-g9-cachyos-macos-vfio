# Backups and rollback

Keep private backups outside the repository. A definition backup alone does not protect the macOS installation or user data.

## Configuration recovery bundle

With the guest fully shut off, preserve:

- Current inactive libvirt XML.
- VM-specific writable OVMF variables and matching OVMF code/template family.
- Complete system-disk EFI partition and its files, including OpenCore configuration and kexts.
- The exact GPU ROM the definition references.
- Network reservation details.
- Checksums, host versions, file paths, permissions, and a short restoration note.

An actual private bundle was created during this build and checked for archive integrity; the XML passed `virt-xml-validate`. That bundle is not included here. A full recovery rehearsal was not performed.

The copied EFI was a **partition image**, not a complete disk. Never overwrite a QCOW2 file with a raw EFI partition image. Do not reuse an old sector offset without confirming the current partition table. Firmware variables and EFI can contain identifiers and should remain private.

## Full VM backup

A separate backup of the system QCOW2 is required to retain APFS volumes, macOS applications, user data, and installed Sunshine settings. Stop the VM for a simple consistent offline copy. Inspect `qemu-img info --backing-chain` first: if backing files exist, preserve the complete chain or create a standalone backup using a QCOW2-aware conversion process. Do not run destructive image commands against a live VM disk.

Store a verified copy on a different physical device. A reflink or snapshot on the same disk is useful for rollback but does not protect against that disk failing. Do not claim a full backup is complete until it has been made and checked.

## Rollback rules

1. Shut down the guest before replacing disks, firmware variables, or applying a different device layout.
2. Back up the current state before restoring an older one.
3. Restore only the required component; review VM name, UUID, MAC, file paths, permissions, and shared GPU ownership.
4. Use `virt-xml-validate` and `virsh define --validate` on a reviewed private XML.
5. A persistent XML change normally needs a full VM stop/start. A reboot inside the guest does not recreate its QEMU devices.
6. For a virtual-only recovery definition, remove both physical GPU functions and their QEMU override together, then enable virtual VGA. Do not accidentally keep the failing dual-video layout.
7. Keep Ventura shut down with autostart disabled. Sequoia still depends on its referenced GPU ROM even if old Ventura disks are later deleted.

## Before publishing changes

Never add generated XML, firmware variables, complete EFI, SMC values, ROMs, disk images, Sunshine configuration/credentials, keys, pairing state, diagnostic reports with serials, or private backups to Git. The `.gitignore` is a convenience, not a security boundary. Inspect every staged file and the complete commit history before publishing.
