# MiKernel: Xiaomi 14 Ultra (aurora), HyperOS OS3.0.305.0.WNAMIXM

## Status
**Full-feature GKI build candidate (not yet boot-validated).** The first minimal GKI temporarily bootlooped, but the handset was recovered by restoring its known-good `init_boot_a` image. It is now functioning on the original kernel and KernelSU Next LKM. Do **not** flash the first GKI image permanently.

## Device and build target
- Device: Xiaomi 14 Ultra Global, codename `aurora`, firmware `OS3.0.305.0.WNAMIXM`.
- Stock kernel: `6.1.138-android14-11-g0c3d559bcd85-ab14529422` (ACK `0c3d559bcd85c64dae9c9c9687abbe5347fff3ad`).
- ARM64, 4K pages, active slot `_a` at time of recovery.
- GKI: Android 14 / Linux 6.1.138 / KMI generation 11; Kleaf `--config=release --lto=none`.
- KernelSU Next built-in from `pershoot/KernelSU-Next` pinned `39b15dead6fa806cb3582f866b081fa1d9e1c9e4`, with `CONFIG_KSU_SUSFS=y`.
- SUSFS kernel patches from `pershoot/susfs4ksu` pinned `6d4f9a92ac7946d9d2d1904149d764506c9ae7b9`, variant `android14-6.1`.
- NoMount VFS from `maxsteeel/nomount` pinned `48e4b79a357d77f787b0db8167dbb1f5570ded17`, `CONFIG_NOMOUNT=y`.
- Keep `CONFIG_MODVERSIONS=y`, other stock module ABI/config options; upload `Module.symvers` for local vendor CRC comparison.

## KernelSU Next Manager compatibility
- Official KernelSU Next v3.4.2 has kernel UAPI **5**.
- This pinned SUSFS fork has kernel UAPI **6**.
- **Do not deploy the UAPI 6 build without a matching UAPI 6 Manager and userspace.** A successful kernel build does not solve this requirement.

## Build
- PR: https://github.com/magicisa/MiKernel/pull/2
- Workflow: `.github/workflows/aurora-305-gki.yml` on `aurora-305-release-abi-rc`.
- Manual workflow on `main` is not the correct trigger before merge; use PR/push checks.
- An artifact can include kernel `Image`, `IMAGE-SHA256.txt`, `GKI-CONFIG.txt`, `BUILD-INFO.txt`, and optional `Module.symvers`. The GitHub Actions ZIP is **not** a flashable `boot.img`.

## ABI evidence (previous no-SUSFS candidate only)
The previous release-profile baseline succeeded with matching CRCs for 417/417 symbols shared between `vmlinux` and Xiaomi's `qca_cld3_kiwi_v2.ko` Wi-Fi module. 139 module CRC entries were not matched to `vmlinux` and may be provided by other vendor modules. This was **not** a successful boot test. The full SUSFS/NoMount image must be compared separately using `tools/check_vendor_module_crc.py`; the earlier result cannot be inherited.

## Recovery (keep local only, no proprietary binaries in GitHub)
- Verified current/working boot: `C:\ROM\aurora305-backup\boot_a_current.img`.
- Verified working KernelSU LKM init_boot: `C:\ROM\aurora305-backup\init_boot_a_current.img`.
- Stock init_boot from same official firmware: `C:\ROM\aurora_global_images_OS3.0.305.0.WNAMIXM_16.0\images\init_boot.img`.
- Active slot must be checked immediately before any flash: `fastboot getvar current-slot`.
- Previously `fastboot boot` worked and did not overwrite `boot_a`; this is **not** a guarantee the custom kernel will boot.
- A rollback after the failed temporary boot succeeded using `fastboot flash init_boot_a <working-patched-init_boot.img>`.
- Never relock the bootloader or wipe data for a kernel experiment. Do not flash `Image` as `boot.img`.
- To migrate LKM -> built-in GKI, `init_boot_a` must be restored to the matching original stock image after confirming the current slot; restore the backed-up patched `init_boot_a` if reverting to stock kernel + LKM.

## Readiness criteria
- GitHub build successful with no patch rejects, all three features built in.
- Compare `Module.symvers` CRCs to Xiaomi vendor modules.
- Kernel and Manager UAPI/userspace matched.
- Kernel packaged into proper Android v4 boot image with AVB reviewed.
- Decide controlled installation and rollback. **Compilation success alone never proves device boot compatibility.**
