# Sunshine and Moonlight on the same laptop

Sunshine runs inside the logged-in macOS desktop. Moonlight runs on CachyOS and reaches the guest through libvirt's private NAT network. The host's external Wi-Fi/Ethernet address is not the address used for this local stream.

## Install and pair

Use the official [Sunshine macOS instructions](https://docs.lizardbyte.dev/projects/sunshine/latest/md_docs_2getting__started.html). This Intel VM uses the **x86_64** package. Grant the required screen/system-audio capture and Accessibility permissions in macOS; verify the requirements for your installed release.

Check the server from macOS Terminal or SSH:

```bash
pgrep -if sunshine
sudo lsof -nP -iTCP:47990 -sTCP:LISTEN
curl -k -s -o /dev/null -w 'HTTP status: %{http_code}\n' https://localhost:47990/
```

The observed server returned HTTP `401`, meaning its web interface responded and required authentication. This is not a test of capture or encoding. `-k` is used here only for the local self-signed web interface.

Find the VM address on CachyOS:

```bash
virsh -c qemu:///system domifaddr macos-sequoia-vfio --source lease
```

Open `https://GUEST_IP:47990` in a browser, create/sign in to the Sunshine account, add `GUEST_IP` in Moonlight, and enter Moonlight's pairing PIN in Sunshine. Keep pairing databases and certificates private. No router port forwarding is required for this host-to-guest connection.

## Stable DHCP address

Reserve the guest address using its actual MAC from `virsh domiflist`. The following is an **example**, not this machine's identity. Choose an unused address on your libvirt subnet and replace the example MAC. Inspect the network XML and leases first; do not duplicate an existing reservation.

```xml
<host mac='52:54:00:12:34:56' name='macos-sequoia' ip='192.168.122.233'/>
```

Save your edited entry privately as `local/reservation.xml`, then:

```bash
virsh -c qemu:///system net-update default add-last ip-dhcp-host local/reservation.xml --live --config
```

Keep DHCP enabled in the guest. Verify both live and inactive network XML. The owner reserved the guest's already-leased address, so the active session did not need interruption. This survives network restarts but does not make streams survive guest shutdown or host sleep.

## Startup and headless observations

Add Sunshine to macOS **General → Login Items & Extensions → Open at Login** if using the app package. It launches after user login, not as a promise of pre-login access. Avoid starting a duplicate service instance. See [Apple's login-item guide](https://support.apple.com/guide/mac-help/open-items-automatically-when-you-log-in-mh15189/mac).

With the mini DisplayPort monitor initially connected, the owner verified:

1. A working stream continued after physically unplugging the DisplayPort cable.
2. A new Moonlight desktop stream could be started with the cable still disconnected.
3. The owner rebooted macOS, then reconnected successfully with the cable disconnected.
4. Physical USB keyboard and mouse assignments were removed; Moonlight provided input.

After unplugging, `system_profiler SPDisplaysDataType` still listed the GPU and Metal 3, but no display. **Do not generalize this into a guarantee of all headless/cold-boot/login scenarios.** The exact effective display/capture arrangement and login mechanism were not recorded. A completely powered-off host boot, sleep/wake, and FileVault pre-login access were not tested. Keep a physical monitor and SSH as recovery options. Do not reintroduce virtual VGA to create a display.

## Stream quality

The first statistics overlay showed **1280×720**, HEVC, about 60 FPS, no network-dropped frames, approximately 1 ms network latency, and 0.27 ms decoding time. These are one observation, not benchmarks. The owner reported better clarity after changing the requested stream to 1080p. The laptop panel's native resolution and final stream parameters were not independently recorded.

A useful starting profile is 1920×1080, 60 FPS, 30 Mbps, HDR off, hardware decoding, with H.264 initially or HEVC if it works well. Treat these as tuning suggestions, not a measured optimum. Match the actual capture and client resolution where possible. Use **Ctrl+Alt+Shift+S** for Moonlight statistics. See the [Moonlight guide](https://github.com/moonlight-stream/moonlight-docs/wiki/Setup-Guide).

Sunshine's macOS encoder is VideoToolbox. Check its logs for actual hardware-encoder selection; Metal support alone does not prove hardware video encoding. Leave advanced encoder options at defaults until measuring a problem. See [Sunshine configuration](https://docs.lizardbyte.dev/projects/sunshine/latest/md_docs_2configuration.html).

## Audio: pending verification

With the monitor unplugged, `system_profiler SPAudioDataType` returned no devices. Audio playback through Moonlight had **not been confirmed** when this repository was prepared.

Current upstream Sunshine documentation describes native system-audio capture on macOS 14+ with **Audio Sink left blank**. Installed-release behavior can differ. The proposed next step was a virtual output using [BlackHole 2ch](https://existential.audio/blackhole/). If using Homebrew in the macOS guest:

```bash
brew install --cask blackhole-2ch
```

After installation and restart, select BlackHole 2ch as the macOS output and test Sunshine's native capture first. If necessary, use `BlackHole 2ch` explicitly as Sunshine's audio sink according to the installed release's instructions. Set Moonlight to stereo and verify CachyOS's volume mixer. Installation, permissions, device selection, and successful playback must all be checked before marking audio complete.
