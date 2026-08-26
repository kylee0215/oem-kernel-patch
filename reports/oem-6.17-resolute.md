# Kernel-Team Email Check — oem-6.17-resolute

_Generated: 2026-08-26 19:04:51 UTC_

**Source:** https://kernel.ubuntu.com/oem-delta/dev/oem-6.17-resolute.html

**Checked against:** last 3 month(s) of kernel-team archives

**Summary:** 21 found, 5 not found · 2 ready to apply (ACK'd with ≥2 ACKs)

## Ready to apply (≥2 ACKs)

- `e9c4c6c91471` ACK*2 — ASoC: sdw_utils: Add missed component_name strings for TI amps
- `88c7115617e3` ACK*2 — UBUNTU: SAUCE: drm/i915/tc: Revert forced DP-alt connected workaround

## All checked commits

| Hash | Subject | Public bug | Private bug | Emailed? | Version | Match | Link | Found In | Signed-off-by |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `e9c4c6c91471` | ASoC: sdw_utils: Add missed component_name strings for TI amps | [2164504](https://bugs.launchpad.net/bugs/2164504) | [stella-3568](https://warthogs.atlassian.net/browse/stella-3568) | ACK*2 | v1 | 100% | [email](https://lists.ubuntu.com/archives/kernel-team/2026-August/171150.html) | August 2026 | Chia-Lin |
| `38573fd563ab` | ASoC: SDCA: Move kcontrol search out of IRQ | [2163215](https://bugs.launchpad.net/bugs/2163215) | [cpl-325](https://warthogs.atlassian.net/browse/cpl-325) | ACK/CMNT | v2 | 100% | [email](https://lists.ubuntu.com/archives/kernel-team/2026-August/171241.html) | August 2026 | Chris |
| `d9db0ad11c05` | ASoC: SDCA: Switch to fixup_controls callback for IRQ registration | [2163215](https://bugs.launchpad.net/bugs/2163215) | [cpl-325](https://warthogs.atlassian.net/browse/cpl-325) | ACK/CMNT | v2 | 100% | [email](https://lists.ubuntu.com/archives/kernel-team/2026-August/171240.html) | August 2026 | Chris |
| `0f380e30f69f` | ASoC: Add a component fixup_controls callback | [2163215](https://bugs.launchpad.net/bugs/2163215) | [cpl-325](https://warthogs.atlassian.net/browse/cpl-325) | ACK/CMNT | v2 | 100% | [email](https://lists.ubuntu.com/archives/kernel-team/2026-August/171239.html) | August 2026 | Chris |
| `38cf850fdb21` | ASoC: SDCA: Populate IRQ data earlier | [2163215](https://bugs.launchpad.net/bugs/2163215) | [cpl-325](https://warthogs.atlassian.net/browse/cpl-325) | ACK/CMNT | v2 | 100% | [email](https://lists.ubuntu.com/archives/kernel-team/2026-August/171238.html) | August 2026 | Chris |
| `ef19b0a3e699` | ASoC: SDCA: Remove devm from primary IRQ cleanup | [2163215](https://bugs.launchpad.net/bugs/2163215) | [cpl-325](https://warthogs.atlassian.net/browse/cpl-325) | ACK/CMNT | v2 | 100% | [email](https://lists.ubuntu.com/archives/kernel-team/2026-August/171236.html) | August 2026 | Chris |
| `71959b21f984` | ASoC: SDCA: Add sdca_irq_cleanup_late() | [2163215](https://bugs.launchpad.net/bugs/2163215) | [cpl-325](https://warthogs.atlassian.net/browse/cpl-325) | ACK/CMNT | v2 | 100% | [email](https://lists.ubuntu.com/archives/kernel-team/2026-August/171235.html) | August 2026 | Chris |
| `b2e62a968554` | ASoC: SDCA: Rename sdca_irq_allocate() to include devm | [2163215](https://bugs.launchpad.net/bugs/2163215) | [cpl-325](https://warthogs.atlassian.net/browse/cpl-325) | ACK/CMNT | v2 | 100% | [email](https://lists.ubuntu.com/archives/kernel-team/2026-August/171233.html) | August 2026 | Chris |
| `a5979f4d88c1` | ASoC: SDCA: Correct kernel doc for sdca_irq_cleanup() | [2163215](https://bugs.launchpad.net/bugs/2163215) | [cpl-325](https://warthogs.atlassian.net/browse/cpl-325) | ACK/CMNT | v2 | 100% | [email](https://lists.ubuntu.com/archives/kernel-team/2026-August/171234.html) | August 2026 | Chris |
| `96be68a19737` | ice: wait for reset completion in ice_resume() | [2162803](https://bugs.launchpad.net/bugs/2162803) | [sutton-4006](https://warthogs.atlassian.net/browse/sutton-4006), [sutton-4745](https://warthogs.atlassian.net/browse/sutton-4745) | APPLIED[R] | v1 | 100% | [email](https://lists.ubuntu.com/archives/kernel-team/2026-August/170645.html) | August 2026 | Aaron |
| `a9bd124e81ed` | Revert "UBUNTU: SAUCE: usb: typec: ucsi: Detect and skip duplicate altmodes from buggy firmware" | [2162695](https://bugs.launchpad.net/bugs/2162695) | [somerville-4776](https://warthogs.atlassian.net/browse/somerville-4776), [somerville-4933](https://warthogs.atlassian.net/browse/somerville-4933), [somerville-4948](https://warthogs.atlassian.net/browse/somerville-4948) | APPLIED | v1 | 100% | [email](https://lists.ubuntu.com/archives/kernel-team/2026-August/170629.html) | August 2026 | Chia-Lin |
| `88c7115617e3` | UBUNTU: SAUCE: drm/i915/tc: Revert forced DP-alt connected workaround | [2160082](https://bugs.launchpad.net/bugs/2160082) | [cpl-327](https://warthogs.atlassian.net/browse/cpl-327) | ACK*2 | v2 | 100% | [email](https://lists.ubuntu.com/archives/kernel-team/2026-August/171203.html) | August 2026 | ChunAn |
| `c70f2fcf9520` | UBUNTU: SAUCE: r8169: gate RTL8116AF fixes behind Dell P5M1260 quirk | [2160475](https://bugs.launchpad.net/bugs/2160475) | [wtn-372](https://warthogs.atlassian.net/browse/wtn-372) | NACK/CMNT | v1 | 100% | [email](https://lists.ubuntu.com/archives/kernel-team/2026-July/170135.html) | July 2026 | Chia-Lin |
| `97c1a2096415` | UBUNTU: SAUCE: r8169: fix RTL8116af can not enter s0idle and c10 | [2160475](https://bugs.launchpad.net/bugs/2160475) | [wtn-372](https://warthogs.atlassian.net/browse/wtn-372) | NACK/CMNT | v1 | 100% | [email](https://lists.ubuntu.com/archives/kernel-team/2026-July/170134.html) | July 2026 | Chia-Lin |
| `a172ada0e76c` | UBUNTU: SAUCE: r8169: add ltr support for RTL8116af | [2160475](https://bugs.launchpad.net/bugs/2160475) | [wtn-372](https://warthogs.atlassian.net/browse/wtn-372) | NACK/CMNT | v1 | 100% | [email](https://lists.ubuntu.com/archives/kernel-team/2026-July/170133.html) | July 2026 | Chia-Lin |
| `f74aa363f83e` | UBUNTU: SAUCE: r8169: fix RTL8116af link readiness bug | [2160475](https://bugs.launchpad.net/bugs/2160475) | [wtn-372](https://warthogs.atlassian.net/browse/wtn-372) | NACK/CMNT | v1 | 100% | [email](https://lists.ubuntu.com/archives/kernel-team/2026-July/170132.html) | July 2026 | Chia-Lin |
| `498f79395de9` | UBUNTU: SAUCE: r8169: move funcitons forward | [2160475](https://bugs.launchpad.net/bugs/2160475) | [wtn-372](https://warthogs.atlassian.net/browse/wtn-372) | NACK/CMNT | v1 | 100% | [email](https://lists.ubuntu.com/archives/kernel-team/2026-July/170131.html) | July 2026 | Chia-Lin |
| `fabbe56533a3` | UBUNTU: SAUCE: net: phy: realtek: add support for dummy phy | [2160475](https://bugs.launchpad.net/bugs/2160475) | [wtn-372](https://warthogs.atlassian.net/browse/wtn-372) | NACK/CMNT | v1 | 100% | [email](https://lists.ubuntu.com/archives/kernel-team/2026-July/170130.html) | July 2026 | Chia-Lin |
| `d020bdac04a9` | Revert "UBUNTU: SAUCE: r8169: add quirk for RTL8116af SerDes" | [2160475](https://bugs.launchpad.net/bugs/2160475) | [wtn-372](https://warthogs.atlassian.net/browse/wtn-372) | NACK/CMNT | v1 | 100% | [email](https://lists.ubuntu.com/archives/kernel-team/2026-July/170129.html) | July 2026 | Chia-Lin |
| `1d74a8bd19e3` | Revert "UBUNTU: SAUCE: r8169: enable RTL8168H/RTL8168EP/RTL8168FP/RTL8125/RTL8126 LTR support" | [2160475](https://bugs.launchpad.net/bugs/2160475) | [wtn-372](https://warthogs.atlassian.net/browse/wtn-372) | No | - | - | - | - | Chia-Lin |
| `faad731a9dd9` | UBUNTU: SAUCE: wifi: ath12k: avoid MHI deinit during suspend | [2160183](https://bugs.launchpad.net/bugs/2160183) | - | NACK/CMNT | v1 | 100% | [email](https://lists.ubuntu.com/archives/kernel-team/2026-July/169962.html) | July 2026 | ChunAn,Kuan-Ying |
| `4950595e49fa` | Revert "UBUNTU: SAUCE: wifi: mt76: mt7925: add DMI quirk for HP Z2 Mini G1a Workstation" | [2158229](https://bugs.launchpad.net/bugs/2158229) | - | ACK | v1 | 100% | [email](https://lists.ubuntu.com/archives/kernel-team/2026-June/169577.html) | June 2026 | Chia-Lin,Kuan-Ying |
| `3c358c780acc` | UBUNTU: SAUCE: HID: intel-ish-hid: Reset enum_devices_done before enumeration | [2135086](https://bugs.launchpad.net/bugs/2135086) | [wtn-328](https://warthogs.atlassian.net/browse/wtn-328) | No | - | - | - | - | Chris,Kuan-Ying |
| `8acc4006b129` | UBUNTU: SAUCE: tools: clamp sizeof in perf_cpu_map__merge | [2132312](https://bugs.launchpad.net/bugs/2132312) | - | No | - | - | - | - | Stefan |
| `4c41280bee2b` | UBUNTU: [Config] Set TOUCHSCREEN_APPLE_Z2=m (arm64) | [2115758](https://bugs.launchpad.net/bugs/2115758) | - | No | - | - | - | - | Juerg,Timo |
| `0cb67e7682f7` | UBUNTU: [Config] Enable SYM53C8XX_2 on arm64 | [2118499](https://bugs.launchpad.net/bugs/2118499) | - | No | - | - | - | - | Benjamin,Mehmet,Timo |
