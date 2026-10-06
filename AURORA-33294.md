# Xiaomi 14 Ultra (aurora): Manager 33294 build

Run **Actions → Aurora - Manager 33294 → Run workflow → main**.
This workflow has no configuration fields and no scheduled trigger.
It builds one Android 14 / Linux 6.1.138 kernel, 4 KB pages, with
KernelSU-Next, SUSFS 2.3.0 and NoMount. Optional upstream feature packs
are not selected. Kernel branding is empty and symbol-version mismatch
forcing is disabled. The generic upstream workflows remain unchanged. Three shared composite actions
have invalid input `type` declarations removed (metadata only).

## Why these sources

The official Manager is v3.4.0 spoofed, build 33294, release commit
`1a879d6a866f80b1fa1c1009a2ffa747873cbb5e` (UAPI 4).
The kernel integration is the pershoot revision used by WildKernels r21:
`4c5853188012f63a1a1fedd4a57fda6375fecb38` (also UAPI 4).
All files under `uapi/` match the Manager release; the build checks this.
The kernel's own build number is allowed to differ. It is not overridden.
Current dev-susfs has moved to UAPI 5 and is deliberately not used here.

SUSFS is pinned to `6d4f9a92ac7946d9d2d1904149d764506c9ae7b9`:
the r21 base `24743360ea08d98f6ad72b856851abed8de5854f` plus pershoot's
two integration commits. No floating SUSFS cherry-picks are performed.
NoMount, kernel_patches and AnyKernel3 are also pinned in the workflow.
The upstream Android manifest, toolchains and third-party Actions retain
their upstream reference behavior; this is not a fully hermetic build.

## Artifacts and validation

- `Manager-33294-spoofed`: official APK and verified SHA256SUMS.
- `NoMount-Metamodule`: module built from the same NoMount source as the kernel.
- `6.1.138-android14-2025-06-KernelSU-Next-AnyKernel3`: kernel package.
- Build summary and provenance metadata from the upstream build process.

Preparation and compilation do not install anything on the phone.
A passing build and matching UAPI do not establish device boot compatibility.
Before flashing, preserve the working boot partition and the stock boot image
for OS3.0.304.0.WNAMIXM, and review the completed logs and package.
The observed working phone uses slot B and kernel 6.1.138-android14-9.
Do not change slots or flash both slots merely to test this build.
Retain the installed working Manager until the kernel update path is reviewed.

## Maintenance

`aurora-build.yml` is a dedicated copy of the upstream reusable build workflow,
with target guards, a UAPI check, fixed SUSFS checkout, and missing-kernel
artifacts treated as errors. Unused feature and cache steps are omitted.
The basic filesystem configuration is applied directly to avoid malformed
upstream misc-action metadata. Keep it separate from generic workflow updates.
There is no automatic publish or release step.
