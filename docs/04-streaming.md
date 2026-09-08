# Sunshine, Moonlight, and BetterDisplay on the same laptop

Sunshine runs inside the logged-in macOS desktop. Moonlight runs on the Linux host and reaches the guest through libvirt's private NAT network. The host's external Wi-Fi/Ethernet address is not the address used for this local stream.

The project began with CachyOS as the host and currently runs on Omarchy. The host distribution is not fundamental to the streaming topology.

## Install and pair

Use the official Sunshine macOS instructions. This Intel VM uses the **x86_64** package. Grant the required screen/system-audio capture and Accessibility permissions in macOS and verify the requirements for the installed Sunshine release.

Check the server from macOS Terminal or SSH:

```bash
pgrep -if sunshine
sudo lsof -nP -iTCP:47990 -sTCP:LISTEN
curl -k -s -o /dev/null -w 'HTTP status: %{http_code}\n' https://localhost:47990/
```

A `401` response confirms that the local Sunshine web interface answered and required authentication; it does not test capture or encoding.

Find the VM address on the Linux host:

```bash
virsh -c qemu:///system domifaddr macos-sequoia-zfs-test --source lease
```

Use your actual domain name if different. Open `https://GUEST_IP:47990`, configure Sunshine, add the guest IP in Moonlight, and complete pairing. Keep pairing databases and certificates private. No router port forwarding is required for this host-to-guest connection.

## Stable DHCP address and libvirt networking

The current guest uses VMXNET3 and a stable reservation on libvirt's default NAT network. Keep DHCP enabled in macOS.

The Omarchy migration also exposed an important firewall detail: local host-to-guest streaming may work while guest DHCP/DNS/Internet access is broken if UFW does not explicitly allow the libvirt bridge.

The working approach includes allowances for DNS, DHCP and forwarding on `virbr0`. One particularly useful portable forwarding rule is:

```bash
sudo ufw route allow in on virbr0 from 192.168.122.0/24
```

Do not unnecessarily tie the forwarding rule to Wi-Fi or Ethernet; the guest should continue working when the laptop changes physical uplink.

For DHCP, the working configuration also permits UDP traffic from client port 68 to server port 67 on `virbr0`:

```bash
sudo ufw allow in on virbr0 proto udp from any port 68 to any port 67
```

Adjust the subnet and firewall policy to your environment rather than copying rules blindly.

## BetterDisplay virtual display

The original CachyOS baseline was first validated with a physical Mini DisplayPort monitor and later shown to reconnect headlessly after the cable was removed.

The current Omarchy configuration is cleaner: **BetterDisplay 4.3.6 build 50119** creates a software virtual display named `Moonlight`. Sunshine sees it as a connected capture target:

```text
Detected display: Moonlight (id: 4128837) connected: true
Configuring selected display (4128837) to stream
```

The numeric display ID is an observation from this machine and should not be assumed portable.

A **1920x1200** virtual display is currently being used. This arrangement avoids relying on a physical monitor or HDMI/DP dummy plug for normal remote operation.

BetterDisplay must remain running. During testing, quitting BetterDisplay removed the virtual `Moonlight` display; Sunshine then detected another display target instead. Restart BetterDisplay and ensure the virtual display is active before restarting Sunshine if this happens.

Do not solve headless display problems by adding a libvirt virtual VGA device. The working VFIO guest uses:

```xml
<video>
  <model type="none"/>
</video>
```

QEMU PCI inspection confirmed that the passed-through W6600M is the guest's only VGA controller.

## Sunshine VideoToolbox configuration

The current explicit Sunshine settings are:

```text
encoder = videotoolbox
vt_software = disabled
vt_realtime = enabled
```

The log confirms that Sunshine is reading those settings.

**HEVC** is the cleanest tested codec on the W6600M. AV1 is unavailable. H.264 is detected, but the VideoToolbox probe has emitted an initial compression-session error suggesting software fallback; the availability test can still subsequently report H.264. Do not enable software encoding merely to silence that probe warning without measuring the effect.

The goal is to keep encoding on VideoToolbox hardware and keep real-time mode enabled for low latency.

## Measured stream observations

These are point-in-time observations, not formal benchmarks.

At **1920x1080 ~60 FPS** Moonlight reported:

- zero network-dropped frames;
- about 1 ms network latency;
- about 0.60 ms decode time;
- about 0.69 ms frame queue time;
- about 1.83 ms render time including VSync.

At **1920x1200 60 FPS**:

- zero network-dropped frames;
- about 1 ms network latency;
- about 0.55 ms decode time;
- about 0.53 ms frame queue time;
- about 3.06 ms render time including VSync.

With Moonlight requesting **120 FPS**, the stream settled at approximately **89.5-89.6 FPS** rather than 120. At that rate the observed values were approximately:

- zero network/jitter drops;
- 1 ms network latency;
- 0.41 ms decode time;
- 0.43 ms frame queue time;
- 2.31 ms render time including VSync.

The host laptop panel itself is 3840x2400 at 60 Hz. Despite the 60 Hz panel, requesting a higher stream frame rate improved perceived pointer responsiveness somewhat.

The remaining pointer and typing delay is larger than the Moonlight network/decode numbers would predict. That suggests the remaining latency is upstream of the client network/decode pipeline—potentially macOS capture/input timing—but the cause is not yet established.

Use **Ctrl+Alt+Shift+S** in Moonlight to display statistics while testing.

A sensible current starting point for this machine is **1920x1200**, HEVC, hardware decoding and roughly **30 Mbps**, then tune frame rate while watching the statistics overlay.

## Audio

Audio playback from the macOS VM through Sunshine/Moonlight to the Linux host is owner-confirmed.

Sunshine's macOS audio capture behavior can change between releases, so verify the installed version's permissions and device selection rather than assuming an old recipe is required. Keep any virtual audio device configuration specific to the machine out of the public repository unless it has been independently verified.

## macOS power management

For an always-on remote VM, normal idle sleep is undesirable. The current guest uses:

```bash
sudo pmset -a sleep 0 disksleep 0 powernap 0
```

Verify with:

```bash
pmset -g custom
```

Do not use a nonexistent `pmset powerbutton` setting; current macOS `pmset` does not expose that key in the way older troubleshooting suggestions sometimes imply.

## Observed BetterDisplay shutdown event

One testing session ended in an orderly guest-initiated macOS shutdown. This was initially mistaken for sleep, but the evidence did not show a sleep/wake cycle.

The host's QEMU/libvirt logs showed the VM exiting with a guest-originated shutdown rather than libvirt sending QEMU SIGTERM. macOS Unified Logging then identified the immediate trigger:

```text
BetterDisplay ... AESendMessage(aevt,rsdn ... target='psn '[loginwindow])
loginwindow ... Received a kAEShowShutdownDialog
loginwindow ... logoutType:3 - Shutdown
```

BetterDisplay had no custom keyboard shortcuts recorded. Its native brightness/audio keyboard handling was present during the session, and Sunshine/Moonlight was active, but **none of that establishes why BetterDisplay sent the event**.

This is documented because the provenance is unusually clear and may help another user recognize the same symptom. It should not be cited as proof of a BetterDisplay defect or a Moonlight input bug without reproduction.

## Recovery checklist

If Moonlight cannot see the intended macOS desktop:

1. Confirm the VM is running.
2. Confirm macOS has an IP address on the libvirt network.
3. Confirm BetterDisplay is running and the `Moonlight` virtual display is enabled.
4. Restart Sunshine after the virtual display exists.
5. Check Sunshine's log for `Detected display` and `Configuring selected display`.
6. Verify the encoder log shows VideoToolbox and the intended settings.
7. Check UFW/libvirt bridge rules if pairing works but guest networking is incomplete.
8. Use SSH as the recovery path rather than adding virtual VGA to the VFIO guest.
