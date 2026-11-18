# Xiaomi 14 Ultra (aurora) — OS3.0.305.0.WNAMIXM GKI build

**Status: PRE-FLIGHT; not compiled and not validated for flashing.**

This branch is isolated from the previously tested `Aurora - Manager 33294` build on `main`. The earlier workflow pins Linux `6.1.138-android14-2025-06`, KernelSU Next v3.4.0, SUSFS and NoMount. Those pins MUST NOT be assumed compatible with the freshly installed HyperOS `OS3.0.305.0.WNAMIXM`.

## Target

- Device: Xiaomi 14 Ultra (`aurora`), Global firmware `OS3.0.305.0.WNAMIXM`.
- Output: GKI ARM64 `Image` plus AnyKernel3 artifact; KernelSU Next **built-in (GKI mode)**, SUSFS if a tested source integration matches, optional NoMount after compatibility verification.
- Preserve stock `boot.img` from the **same** firmware, current known-working boot/init_boot copies, unlocked bootloader, and recovery path.
- Do not build an `android16-6.12` image solely because Android userspace is 16. Determine the GKI/KMI generation from the phone's current stock kernel.
- Do not run `aurora-33294.yml` as an OS3.0.305.0 build. It is hard-coded for the previous target.

## Phone pre-flight (run in PowerShell with USB debugging)

```powershell
adb devices -l
adb shell getprop ro.product.device
adb shell getprop ro.build.version.incremental
adb shell uname -r
adb shell uname -a
adb shell getconf PAGE_SIZE
adb shell getprop ro.boot.slot_suffix
adb shell getprop ro.build.version.security_patch
adb shell getprop ro.vendor.build.security_patch
adb shell su -c id
```

Save the output. Compare the full `uname -r` (KMI family AND Linux sublevel), page size and stock boot image with the available GKI source branch/patch level. Android OS security patch is **not** an interchangeable substitute for the GKI branch patch level.

## Work after pre-flight

1. Select the matching GKI source revision (matching KMI and kernel sublevel/security requirements).
2. Pin and verify the KernelSU Next integration commit (target manager v3.4.2), separately verify SUSFS patch integration and NoMount against that revision.
3. Create a separate purpose-built workflow with fail-closed guards; **do not** silently modify the older tested workflow.
4. Compile once, examine full CI logs, resulting `Image` metadata and patch rejects; record SHA-256 and source revisions.
5. Test reversible boot from the device's currently active slot only where the bootloader supports `fastboot boot`. Do not flash both slots or relock the bootloader.
6. Only after a successful boot and functionality test, consider persistent flashing and verify root mode.

## References

- KernelSU Next v3.4.2: https://github.com/KernelSU-Next/KernelSU-Next/releases/tag/v3.4.2
- WildKernels build guide: https://github.com/WildKernels/GKI_KernelSU_SUSFS/blob/main/docs/build-from-fork.md
- WildKernels installation and KMI matching: https://github.com/WildKernels/GKI_KernelSU_SUSFS/blob/main/docs/installation.md

## LKM to built-in GKI transition

The phone is currently rooted with KernelSU Next. Before a built-in GKI boot test, establish whether its current installation is LKM in a patched `init_boot` (or other ramdisk), and plan to restore the matching **stock** image for that partition. Do not leave an LKM boot hook in place alongside the built-in KernelSU Next driver; back up the known-good patched image first and keep a reversible recovery path. The built-in GKI kernel is installed in `boot`, whereas LKM generally patches the ramdisk (`init_boot` on devices using that partition). Consult https://github.com/KernelSU-Next/KernelSU-Next/issues/1227 before migration.
