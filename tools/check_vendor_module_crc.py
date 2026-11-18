#!/usr/bin/env python3
"""Audit a 64-bit little-endian ARM64 vendor .ko against GKI Module.symvers.

Reads only: does not load, change, or upload proprietary modules.
Exit: 0 = no mismatches among checked vmlinux symbols (NOT boot proof);
      1 = CRC mismatch; 2 = incompatible input or no shared vmlinux symbols.
"""
import argparse
from pathlib import Path
import struct
import sys


def load_versions(module: Path):
    blob = module.read_bytes()
    if blob[:4] != b"\x7fELF" or blob[4] != 2 or blob[5] != 1:
        raise ValueError("Expected ELF64 little-endian module")
    if struct.unpack_from("<H", blob, 18)[0] != 183:
        raise ValueError("Expected AArch64 ELF module")
    shoff = struct.unpack_from("<Q", blob, 40)[0]
    entsize = struct.unpack_from("<H", blob, 58)[0]
    count = struct.unpack_from("<H", blob, 60)[0]
    str_index = struct.unpack_from("<H", blob, 62)[0]
    if entsize != 64 or count == 0 or str_index >= count:
        raise ValueError("Unexpected ELF section table")
    sections = [struct.unpack_from("<IIQQQQIIQQ", blob, shoff + i * entsize) for i in range(count)]
    def section_blob(sh):
        offset, size = sh[4], sh[5]
        if offset + size > len(blob):
            raise ValueError("Invalid ELF section bounds")
        return blob[offset:offset + size]
    section_names = section_blob(sections[str_index])
    names = {}
    for sh in sections:
        start = sh[0]
        if start >= len(section_names):
            raise ValueError("Bad section-name offset")
        end = section_names.find(b"\0", start)
        if end == -1:
            raise ValueError("Unterminated section name")
        names[section_names[start:end].decode("ascii", "replace")] = sh
    if "__versions" not in names:
        raise ValueError("Missing __versions section (module may not have CONFIG_MODVERSIONS)")
    data = section_blob(names["__versions"])
    if len(data) % 64:
        raise ValueError("Unsupported __versions entry layout")
    result = {}
    for i in range(0, len(data), 64):
        crc = struct.unpack_from("<Q", data, i)[0] & 0xFFFFFFFF
        name = data[i + 8:i + 64].split(b"\0", 1)[0].decode("ascii", "replace")
        if name:
            result[name] = crc
    return result


def load_symvers(path: Path):
    result = {}
    for number, line in enumerate(path.read_text(errors="replace").splitlines(), 1):
        cols = line.split()
        if not cols or cols[0].startswith("#"):
            continue
        if len(cols) < 3:
            raise ValueError(f"Bad Module.symvers line {number}")
        # Kernel-origin symbols only. Vendor dependencies belong to other .ko.
        if cols[2] == "vmlinux":
            result[cols[1]] = int(cols[0], 16) & 0xFFFFFFFF
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("module", type=Path, help="Local proprietary vendor .ko")
    p.add_argument("symvers", type=Path, help="Built GKI Module.symvers")
    args = p.parse_args()
    try:
        expected = load_versions(args.module)
        built = load_symvers(args.symvers)
    except (ValueError, OSError, struct.error) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    matches = sorted(set(expected) & set(built))
    mismatches = [(s, expected[s], built[s]) for s in matches if expected[s] != built[s]]
    unknown = sorted(set(expected) - set(built))
    print(f"Vendor module symbols with CRC: {len(expected)}")
    print(f"Compared with built vmlinux symbols: {len(matches)}")
    print(f"Matching vmlinux CRC: {len(matches) - len(mismatches)}")
    print(f"Mismatching vmlinux CRC: {len(mismatches)}")
    print(f"Not exported by this vmlinux: {len(unknown)} (can belong to vendor .ko)")
    for sym, old, new in mismatches[:40]:
        print(f"MISMATCH {sym}: module 0x{old:08x}, GKI 0x{new:08x}")
    if not matches:
        print("INCONCLUSIVE: no shared symbols found; check Module.symvers completeness")
        return 2
    if mismatches:
        print("FAIL: vendor module expects a different kernel ABI for shared symbols")
        return 1
    print("PASS for compared vmlinux CRCs ONLY; remaining symbols and boot are unverified")
    return 0


if __name__ == "__main__":
    sys.exit(main())
