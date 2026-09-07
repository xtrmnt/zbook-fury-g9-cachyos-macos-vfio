#!/usr/bin/env python3
"""Write a private, reviewable VM definition. Never alter a host or start a VM."""

import argparse
import os
from pathlib import Path
import re
import secrets
import uuid
import xml.etree.ElementTree as ET

QEMU = "http://libvirt.org/schemas/domain/qemu/1.0"
ET.register_namespace("qemu", QEMU)


def pci(value):
    match = re.fullmatch(r"([0-9a-fA-F]{4}):([0-9a-fA-F]{2}):([0-9a-fA-F]{2})\.([0-7])", value)
    if not match:
        raise argparse.ArgumentTypeError("Use a full PCI address such as 0000:03:00.0")
    return dict(zip(("domain", "bus", "slot", "function"), ("0x" + s for s in match.groups())))


def build(args):
    template = Path(__file__).resolve().parents[1] / "configs/sequoia-gpu-only.xml.in"
    root = ET.parse(template).getroot()
    source = ET.parse(args.source_xml).getroot()
    smc = [a.get("value") for a in source.findall(f"{{{QEMU}}}commandline/{{{QEMU}}}arg")
           if a.get("value", "").startswith("isa-applesmc,osk=")]
    if len(smc) != 1 or not smc[0].split("osk=", 1)[1] or "__LOCAL_OSK_REQUIRED__" in smc[0]:
        raise ValueError("Source must contain exactly one non-placeholder Apple SMC argument")
    for arg in root.findall(f"{{{QEMU}}}commandline/{{{QEMU}}}arg"):
        if arg.get("value", "").startswith("isa-applesmc,osk="):
            arg.set("value", smc[0])
    root.find("name").text = args.name
    root.find("os/nvram").text = args.nvram
    devices = root.find("devices")
    devices.find("disk/source").set("file", args.disk)
    interface = devices.find("interface")
    interface.find("source").set("network", args.network)
    if args.identity_xml:
        identity = ET.parse(args.identity_xml).getroot()
        if identity.findtext("name") != args.name:
            raise ValueError("Identity XML name must match --name")
        identity_uuid = str(uuid.UUID(identity.findtext("uuid")))
        mac = identity.find("devices/interface/mac")
        if mac is None:
            raise ValueError("Identity XML must contain a network MAC")
        mac_value = mac.get("address", "")
        if not re.fullmatch(r"(?:[0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}", mac_value):
            raise ValueError("Invalid identity MAC")
    else:
        identity_uuid = str(uuid.uuid4())
        mac_value = "52:54:00:" + ":".join(f"{b:02x}" for b in secrets.token_bytes(3))
    root.insert(1, ET.Element("uuid"))
    root.find("uuid").text = identity_uuid
    interface.insert(0, ET.Element("mac", {"address": mac_value}))
    gpu, audio = devices.findall("hostdev[@type='pci']")
    gpu.find("source/address").attrib.update(args.gpu)
    audio.find("source/address").attrib.update(args.audio)
    gpu.find("rom").set("file", args.rom)
    if args.stage == "install":
        devices.remove(gpu)
        devices.remove(audio)
        root.remove(root.find(f"{{{QEMU}}}override"))
        video = devices.find("video")
        video.clear()
        ET.SubElement(video, "model", {"type": "vga", "vram": "16384", "heads": "1", "primary": "yes"})
        ET.SubElement(video, "address", {"type": "pci", "domain": "0x0000", "bus": "0x00", "slot": "0x01", "function": "0x0"})
        for boot in list(root.findall("os/boot")):
            root.find("os").remove(boot)
        for path, target, unit in [(args.opencore, "sda", "0"), (args.recovery, "sdc", "2")]:
            disk = ET.SubElement(devices, "disk", {"type": "file", "device": "disk"})
            ET.SubElement(disk, "driver", {"name": "qemu", "type": "raw"})
            ET.SubElement(disk, "source", {"file": path})
            ET.SubElement(disk, "target", {"dev": target, "bus": "sata"})
            if target == "sda":
                ET.SubElement(disk, "boot", {"order": "1"})
            ET.SubElement(disk, "address", {"type": "drive", "controller": "0", "bus": "0", "target": "0", "unit": unit})
    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ")
    return tree


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source-xml", required=True, type=Path, help="Private working macOS XML supplying the SMC argument only")
    p.add_argument("--identity-xml", type=Path, help="Preserve an existing Sequoia UUID/MAC during a stage transition")
    p.add_argument("--stage", choices=["install", "gpu"], required=True)
    p.add_argument("--output", required=True, type=Path, help="New private output file; existing files are never overwritten")
    p.add_argument("--name", default="macos-sequoia-vfio")
    base = "/var/lib/libvirt/images/macos-sequoia/"
    p.add_argument("--disk", default=base + "macos-sequoia-vfio.qcow2")
    p.add_argument("--nvram", default=base + "OVMF_VARS.fd")
    p.add_argument("--opencore", default=base + "OpenCore-Sequoia.img")
    p.add_argument("--recovery", default=base + "Sequoia-Recovery.img")
    p.add_argument("--rom", default="/var/lib/libvirt/vbios/w6600m-73e3.rom")
    p.add_argument("--gpu", type=pci, default=pci("0000:03:00.0"))
    p.add_argument("--audio", type=pci, default=pci("0000:03:00.1"))
    p.add_argument("--network", default="default")
    args = p.parse_args()
    try:
        for name in ("disk", "nvram", "opencore", "recovery", "rom"):
            if not Path(getattr(args, name)).is_absolute():
                raise ValueError(f"--{name} must be an absolute path")
        tree = build(args)
        fd = os.open(args.output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "wb") as stream:
            tree.write(stream, encoding="utf-8", xml_declaration=True)
    except (OSError, ValueError, ET.ParseError, AttributeError, TypeError) as exc:
        p.exit(1, f"Cannot prepare definition: {exc}\n")
    print(f"Wrote private definition: {args.output}")
    print("Review paths, identities, PCI assignments, firmware and machine type; validate before defining.")
    print("No VM or host state was changed. Keep this generated file out of Git.")


if __name__ == "__main__":
    main()
