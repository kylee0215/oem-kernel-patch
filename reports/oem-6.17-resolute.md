# Kernel-Team Email Check — oem-6.17-resolute

_Generated: 2026-09-26 12:46:17 UTC_

**Source:** https://kernel.ubuntu.com/oem-delta/dev/oem-6.17-resolute.html

**Checked against:** last 3 month(s) of kernel-team archives

**Summary:** 10 found, 3 not found · 1 ready to apply (ACK'd with ≥2 ACKs)

## Ready to apply (≥2 ACKs)

- `0f380e30f69f` ACK/CMNT*2 — ASoC: Add a component fixup_controls callback

## All checked commits

| Hash | Subject | Public bug | Private bug | Emailed? | Version | Match | Link | Found In | Signed-off-by |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `38573fd563ab` | ASoC: SDCA: Move kcontrol search out of IRQ | [2163215](https://bugs.launchpad.net/bugs/2163215) | [cpl-325](https://warthogs.atlassian.net/browse/cpl-325) | sent | v6 | 100% | [email](https://lists.ubuntu.com/archives/kernel-team/2026-September/172066.html) | September 2026, August 2026 | Chris |
| `d9db0ad11c05` | ASoC: SDCA: Switch to fixup_controls callback for IRQ registration | [2163215](https://bugs.launchpad.net/bugs/2163215) | [cpl-325](https://warthogs.atlassian.net/browse/cpl-325) | sent | v6 | 100% | [email](https://lists.ubuntu.com/archives/kernel-team/2026-September/172065.html) | September 2026, August 2026 | Chris |
| `0f380e30f69f` | ASoC: Add a component fixup_controls callback | [2163215](https://bugs.launchpad.net/bugs/2163215) | [cpl-325](https://warthogs.atlassian.net/browse/cpl-325) | ACK/CMNT*2 | v8 | 100% | [email](https://lists.ubuntu.com/archives/kernel-team/2026-September/172446.html) | September 2026, August 2026 | Chris |
| `38cf850fdb21` | ASoC: SDCA: Populate IRQ data earlier | [2163215](https://bugs.launchpad.net/bugs/2163215) | [cpl-325](https://warthogs.atlassian.net/browse/cpl-325) | sent | v6 | 100% | [email](https://lists.ubuntu.com/archives/kernel-team/2026-September/172063.html) | September 2026, August 2026 | Chris |
| `ef19b0a3e699` | ASoC: SDCA: Remove devm from primary IRQ cleanup | [2163215](https://bugs.launchpad.net/bugs/2163215) | [cpl-325](https://warthogs.atlassian.net/browse/cpl-325) | NACK | v6 | 100% | [email](https://lists.ubuntu.com/archives/kernel-team/2026-September/172156.html) | September 2026, August 2026 | Chris |
| `71959b21f984` | ASoC: SDCA: Add sdca_irq_cleanup_late() | [2163215](https://bugs.launchpad.net/bugs/2163215) | [cpl-325](https://warthogs.atlassian.net/browse/cpl-325) | sent | v6 | 100% | [email](https://lists.ubuntu.com/archives/kernel-team/2026-September/172060.html) | September 2026, August 2026 | Chris |
| `b2e62a968554` | ASoC: SDCA: Rename sdca_irq_allocate() to include devm | [2163215](https://bugs.launchpad.net/bugs/2163215) | [cpl-325](https://warthogs.atlassian.net/browse/cpl-325) | sent | v6 | 100% | [email](https://lists.ubuntu.com/archives/kernel-team/2026-September/172059.html) | September 2026, August 2026 | Chris |
| `a5979f4d88c1` | ASoC: SDCA: Correct kernel doc for sdca_irq_cleanup() | [2163215](https://bugs.launchpad.net/bugs/2163215) | [cpl-325](https://warthogs.atlassian.net/browse/cpl-325) | NACK/CMNT | v2 | 100% | [email](https://lists.ubuntu.com/archives/kernel-team/2026-August/171234.html) | August 2026 | Chris |
| `a9bd124e81ed` | Revert "UBUNTU: SAUCE: usb: typec: ucsi: Detect and skip duplicate altmodes from buggy firmware" | [2162695](https://bugs.launchpad.net/bugs/2162695) | [somerville-4776](https://warthogs.atlassian.net/browse/somerville-4776), [somerville-4933](https://warthogs.atlassian.net/browse/somerville-4933), [somerville-4948](https://warthogs.atlassian.net/browse/somerville-4948) | APPLIED | v1 | 100% | [email](https://lists.ubuntu.com/archives/kernel-team/2026-August/170629.html) | August 2026 | Chia-Lin |
| `faad731a9dd9` | UBUNTU: SAUCE: wifi: ath12k: avoid MHI deinit during suspend | [2160183](https://bugs.launchpad.net/bugs/2160183) | - | NACK/CMNT | v1 | 100% | [email](https://lists.ubuntu.com/archives/kernel-team/2026-July/169962.html) | July 2026 | ChunAn,Kuan-Ying |
| `8acc4006b129` | UBUNTU: SAUCE: tools: clamp sizeof in perf_cpu_map__merge | [2132312](https://bugs.launchpad.net/bugs/2132312) | - | No | - | - | - | - | Stefan |
| `4c41280bee2b` | UBUNTU: [Config] Set TOUCHSCREEN_APPLE_Z2=m (arm64) | [2115758](https://bugs.launchpad.net/bugs/2115758) | - | No | - | - | - | - | Juerg,Timo |
| `0cb67e7682f7` | UBUNTU: [Config] Enable SYM53C8XX_2 on arm64 | [2118499](https://bugs.launchpad.net/bugs/2118499) | - | No | - | - | - | - | Benjamin,Mehmet,Timo |
