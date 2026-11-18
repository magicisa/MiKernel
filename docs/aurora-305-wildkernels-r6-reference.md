# Aurora 305 boot regression: known-good WildKernels r6 as an A/B reference

Date: 2026-11-18. **Analysis only, not a flash instruction.**

## Evidence that a WildKernels GKI really worked on this phone

User's historical Kernel Flasher log from 2026-07-28: installed
`6.1.138-android14-2025-06-AnyKernel3.zip` (Normal, `do.flash_bypass=0`)
into active `boot_a` and finished `Done!`. A subsequent user verification
confirmed a rooted, working KernelSU/SUSFS GKI `6.1.138-android14-9-...`
on an earlier HyperOS 3 build. This **must not** be interpreted as a tested
WildKernels boot on OS3.0.305.0.WNAMIXM.

Historical public reference:
- [WildKernels r6 release](https://github.com/WildKernels/GKI_KernelSU_SUSFS/releases/tag/r6)
- [r6 build recipe](https://github.com/WildKernels/GKI_KernelSU_SUSFS/blob/r6/.github/workflows/build.yml)
- [r6 download-kernel action](https://github.com/WildKernels/GKI_KernelSU_SUSFS/blob/r6/.github/actions/download-kernel/action.yml)
- [r6 build-kernel action](https://github.com/WildKernels/GKI_KernelSU_SUSFS/blob/r6/.github/actions/build-kernel/action.yml)
- [MiKernel test workflow](../.github/workflows/aurora-305-gki.yml)

## Controlled differences

| Axis | Historically working WildKernels r6 Normal | Failing MiKernel aurora 305 |
|---|---|---|
| Intended GKI | 6.1.138 android14 2025-06, 4K | 6.1.138 android14-11, 4K |
| Linux release observed | `6.1.138-android14-9-...` | `6.1.138-android14-11-g0c3d559bcd85-dirty` |
| Source checkout | `repo init` for `common-android14-6.1-2025-06`, unpinned branch head | Explicitly pinned `0c3d559bcd85c64dae9c9c9687abbe5347fff3ad` |
| Kleaf invocation | `--config=fast --config=stamp` | `--config=release --lto=none` |
| KernelSU Next | pershoot dev-susfs r6 33225 (historical build) | pershoot SUSFS fork 33568 / UAPI6 |
| SUSFS | 2.2.0 per r6 release | 2.4.0 |
| NoMount kernel VFS | **Not listed in r6 release feature set** | **Built into kernel** via `CONFIG_NOMOUNT=y` |
| Module bypass | Normal `do.flash_bypass=0`; bypass variant existed but was not used | No force-loader bypass |
| User firmware | Earlier HyperOS 3 build | OS3.0.305.0.WNAMIXM |

**Do not equate matching 6.1.138 sublevel with identical ABI or same kernel code.**
The older working `android14-9` and current Xiaomi stock `android14-11`
suffixes are a meaningful confounder. Compare actual `Image`, exported
symbols, .config, dynamic vendor modules and modules.load for each precise build.
NoMount remains a requirement for final release, but not necessarily for the
first regression-isolation build.

## What the failed MiKernel proved

Both `fastboot boot` and permanent `boot_a` flashing on OS3.0.305.0
did not complete boot. Kernel/ADB/zygote/system_server reached userspace,
but ALSA `pineapple-mtp-snd-card` was absent, `AGM` failed, no ready
`media.audio_policy` service, and the Android watchdog terminated
`system_server` repeatedly. User confirmed successful rollback afterward.

Twelve actual audio module `.ko` passed 604 module-versus-kernel CRC
comparisons plus 48 intermodule matches, 0 mismatches; no conclusions about
load/probe behavior or other 144 external references.

## Recommended engineering next steps

1. **Acquire the exact formerly working WildKernels AnyKernel3 ZIP** for
   offline comparison; preserve its provenance and SHA-256. Do not substitute a
   present-day nightly or another release merely because its filename matches.
2. Extract `Image`, banner, optional `/proc/config.gz` / module signatures
   and inspect `anykernel.sh` to confirm Normal rather than Bypass.
3. Compare Wild `Image` against *both* Xiaomi 305 stock `Image` and failed
   MiKernel `Image`. Confirm source/GKI revision and KMI changes before
   taking the Wild recipe as compatible with current 305 firmware.
4. Build controlled A/B diagnostics: (a) r6-like base/flags and KernelSU Next
   and SUSFS only (no NoMount), (b) same base with current KSU/SUSFS,
   (c) then add NoMount. Change **one axis at a time**; keep final functionality
   target KSU Next + SUSFS + NoMount.
5. Add CI proof of `Module.symvers` and relevant Xiaomi audio modules.
   On a later *specifically approved* temporary test, collect `dmesg`,
   `/proc/modules`, and `/sys/class/sound` before watchdog resets. Filter
   `Unknown symbol`, `invalid module format`, `module verification failed`,
   `machine_dlkm`, `snd`, `audio`, `probe`, `regulator`, `q6`,
   `adsp`, and `errno` without relying on filtered logcat alone.
6. Never fix by falsifying `vermagic`, force-loading modules, changing
   `vbmeta`, disabling SELinux, or suppressing watchdog. No additional flash
   of the unchanged failing candidate.

**Decision:** WildKernels is now the highest-priority working reference; the
root cause remains unknown until a like-for-like control is compared.
