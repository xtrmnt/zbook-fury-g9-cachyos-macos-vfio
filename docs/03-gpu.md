# W6600M passthrough

The working Ventura definition provided two physical PCI assignments and an OpenCore-compatible guest device-ID override. The final Sequoia configuration retained those settings.

| Item | Observed value |
|---|---|
| Physical GPU | `0000:03:00.0`, `1002:73e1` |
| Physical audio | `0000:03:00.1`, `1002:ab28` |
| Guest GPU slot | `0000:00:05.0`, multifunction enabled |
| Guest audio slot | `0000:00:05.1` |
| Host binding | Both functions already using `vfio-pci` |
| Assignment mode | `managed='no'`, inherited from working host setup |
| Guest device-ID override | `29667` decimal = `0x73e3` |
| ROM | Private, existing `w6600m-73e3.rom` |
| Virtual video | `none` |

The override applies to `hostdev0`, the GPU in this template. Reordering or inserting host devices can change auto-generated aliases; inspect `virsh domxml-to-native qemu-argv` and confirm that the override still targets the GPU if you change device order. Never publish that command output without removing private values.

## Prepare the final definition

Stop the guest first. Export its current inactive definition to a private path. Use the helper with `--identity-xml` to preserve the Sequoia UUID and MAC when transitioning the same VM:

```bash
virsh -c qemu:///system dumpxml --inactive macos-sequoia-vfio > local/sequoia-before-gpu.xml
python3 tools/prepare_definition.py \
  --source-xml local/sequoia-before-gpu.xml \
  --identity-xml local/sequoia-before-gpu.xml \
  --stage gpu \
  --output local/sequoia-gpu.xml
virt-xml-validate local/sequoia-gpu.xml domain
```

Review the generated definition and supply different path/BDF arguments if needed. The helper uses this repository's controller layout, not arbitrary changes in the source VM: compare the definitions before replacing one. In particular, preserve any custom configuration you added yourself. With the guest shut off, apply the reviewed XML using `virsh define --validate`, then start it.

For the first successful test, a monitor was connected to mini DisplayPort. Keep SSH available for diagnostics. The final setup retains SPICE and emulated inputs, but **has no virtual display** and no physical USB assignments.

## Verify in macOS

```bash
system_profiler SPDisplaysDataType
sysctl kern.bootargs
sudo kmutil showloaded | grep -Ei 'Lilu|WhateverGreen|VirtualSMC|VMHide|RestrictEvents'
```

Observed graphics fields: `AMD Radeon Navi23`, **8 GB**, device ID `0x73e3`, **Metal 3**, online physical display at 1080p/60 Hz. These establish recognition and reported acceleration support, not a complete GPU stress test or proof of Sunshine hardware encoding.

Observed loaded kexts: Lilu 1.7.2, WhateverGreen 1.7.0, VirtualSMC 1.3.7, RestrictEvents 1.1.6, VMHide 2.0.0. They came from the selected upstream EFI; this repository neither supplies nor independently audits them.

The last verified boot arguments were:

```text
-v keepsyms=1 debug=0x100 agdpmod=pikera
```

The debug flags were retained during troubleshooting. Removing `-v` later is optional; preserve the working argument set in a backup first. Avoid unrelated boot-argument changes while diagnosing a failure.

## Optional physical USB

Individual USB passthrough worked with a SiGma keyboard `1c4f:0002` and Pixart mouse `093a:2510`. They were later removed from live and saved definitions after Moonlight input worked. The USB controller itself was not passed through.

If adding your own devices, identify them using `lsusb`, distinguish identical vendor/product pairs, and keep a host-side input method. Missing explicitly assigned USB devices can prevent a later VM start. Do not use the IDs above unless they match your actual devices. The final template deliberately has no physical USB entries.
