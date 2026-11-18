#!/usr/bin/env python3
"""Rebase only the SUSFS fs/namespace.c header-addition hunk onto aurora ACK.

The pinned android14-6.1 SUSFS patch has a header include block that differs
from ACK 0c3d559bcd85 (Xiaomi HyperOS 3.0.305.0). Instead of suppressing
patch rejects, transplant its exact added lines to the nearest unambiguous
include anchors and remove that now-redundant first hunk. Everything else is
applied normally by patch(1), which must pass without rejects.

Stop if the upstream patch's first hunk changes meaning or expectations.
"""
from pathlib import Path
import re
import sys


def fail(reason):
    raise SystemExit("Cannot safely rebase SUSFS namespace header: " + reason)


def main():
    if len(sys.argv) != 3:
        fail("usage: rebase_susfs_namespace_header.py PATCH fs/namespace.c")
    patch_path = Path(sys.argv[1])
    source_path = Path(sys.argv[2])
    patch = patch_path.read_text()
    source = source_path.read_text()
    diff_header = "diff --git a/fs/namespace.c b/fs/namespace.c\n"
    if patch.count(diff_header) != 1:
        fail("namespace.c diff missing or duplicated")

    start = patch.index(diff_header)
    next_diff = patch.find("\ndiff --git ", start + len(diff_header))
    end = len(patch) if next_diff == -1 else next_diff + 1
    section = patch[start:end]
    first_hunk_start = section.find("\n@@ ")
    if first_hunk_start < 0:
        fail("first namespace.c hunk not found")
    first_hunk_start += 1
    next_hunk = section.find("\n@@ ", first_hunk_start + 1)
    if next_hunk < 0:
        fail("next namespace.c hunk not found (unexpected patch)")
    next_hunk += 1
    first_hunk = section[first_hunk_start:next_hunk]
    header = first_hunk.splitlines()[0]
    if not re.match(r"^@@ -\d+,\d+ \+\d+,\d+ @@", header):
        fail("unexpected unified diff header")

    changes = first_hunk.splitlines(keepends=True)[1:]
    if any(line.startswith("-") for line in changes):
        fail("the first hunk removes source lines; manual review required")
    added_groups = []
    current = []
    for line in changes:
        if line.startswith("+"):
            current.append(line[1:])
        else:
            if current:
                added_groups.append("".join(current))
                current = []
            if not line.startswith((" ", "\\")):
                fail("unexpected diff marker")
    if current:
        added_groups.append("".join(current))
    if len(added_groups) != 2:
        fail("expected exactly two independent addition groups, got " + str(len(added_groups)))

    include_block, declarations_block = added_groups
    if (
        "#include <linux/susfs_def.h>" not in include_block
        or not include_block.startswith("#ifdef CONFIG_KSU_SUSFS\n")
        or not include_block.rstrip().endswith("#endif // #ifdef CONFIG_KSU_SUSFS")
    ):
        fail("unexpected SUSFS include addition")
    if (
        "susfs_is_current_ksu_domain" not in declarations_block
        or "CL_COPY_MNT_NS" not in declarations_block
        or not declarations_block.startswith("#ifdef CONFIG_KSU_SUSFS_SUS_MOUNT\n")
        or "#endif" not in declarations_block
    ):
        fail("unexpected SUSFS declaration addition")
    if '#include "internal.h"\n' not in source:
        fail("internal.h include missing")
    if "#include <linux/mnt_idmapping.h>\n" in source:
        include_anchor = "#include <linux/mnt_idmapping.h>\n"
    elif "#include <linux/shmem_fs.h>\n" in source:
        include_anchor = "#include <linux/shmem_fs.h>\n"
    else:
        fail("no trusted include anchor")
    declarations_anchor = '#include "internal.h"\n'
    if source.count(include_anchor) != 1 or source.count(declarations_anchor) != 1:
        fail("include anchors not unique")
    if "susfs_is_current_ksu_domain" in source or "#include <linux/susfs_def.h>" in source:
        fail("SUSFS header content already exists")
    if source.index(include_anchor) >= source.index(declarations_anchor):
        fail("include order is unexpected")
    source = source.replace(include_anchor, include_anchor + include_block, 1)
    source = source.replace(declarations_anchor, declarations_anchor + "\n" + declarations_block, 1)

    # Retain the diff file header, the remaining nine hunks and every other
    # file's diff unchanged. The transplanted additions preserve line offsets
    # expected by subsequent hunks, but patch(1) must still verify context.
    revised_section = section[:first_hunk_start] + section[next_hunk:]
    revised = patch[:start] + revised_section + patch[end:]
    source_path.write_text(source)
    patch_path.write_text(revised)
    print("SUSFS namespace.c first header hunk rebased (2 additions, no deletions).")
    print("Original first hunk:", header)
    print("Remaining namespace.c hunks will be applied by patch(1) without error suppression.")


if __name__ == "__main__":
    main()
