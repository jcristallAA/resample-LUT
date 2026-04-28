"""Resample CET LUT files to 16/32/64/128 distinct colors while keeping 256 total entries.

Each source color is picked with stride = 256/N and repeated N times so Leapfrog
still sees a 256-entry LUT but the colorbar shows only N visible bands.
"""

import os
import re

DIR = r"C:\Python\LUT"
INPUT_FILES = ["CET-D01A.lut", "CET-R2.lut", "CET-R4.lut"]
TARGETS = [16, 32, 64, 128]


def parse_lut(path):
    with open(path, "r") as f:
        text = f.read()

    name = re.search(r'Name\s*=\s*"([^"]*)"', text).group(1)
    desc = re.search(r'Description\s*=\s*"([^"]*)"', text).group(1)

    entries = []
    in_lut = False
    for line in text.splitlines():
        if "LUT" in line and "{" in line:
            in_lut = True
            continue
        if in_lut and "}" in line:
            break
        if in_lut:
            parts = line.split()
            if len(parts) == 4:
                _, r, g, b = (int(p) for p in parts)
                entries.append((r, g, b))

    if len(entries) != 256:
        raise ValueError(f"{path}: expected 256 entries, got {len(entries)}")
    return name, desc, entries


def write_lut(path, name, desc, entries):
    with open(path, "w", newline="\n") as f:
        f.write("LookUpTable Begin\n")
        f.write(f'    Name        = "{name}"\n')
        f.write(f'    Description = "{desc}"\n')
        f.write(f"    NrEntries   = 256\n")
        f.write("    LUT = {\n")
        for i, (r, g, b) in enumerate(entries):
            f.write(f"    {i:4d}{r:9d}{g:9d}{b:9d}\n")
        f.write("    }\n")
        f.write("LookUpTable End\n")


def resample(entries, n):
    stride = 256 // n
    out = []
    for i in range(n):
        color = entries[i * stride]
        out.extend([color] * stride)
    return out


def main():
    for fname in INPUT_FILES:
        src = os.path.join(DIR, fname)
        name, desc, entries = parse_lut(src)
        base = os.path.splitext(fname)[0]

        for n in TARGETS:
            new_entries = resample(entries, n)
            new_name = f"{name}-{n}"
            new_desc = desc if desc else f"Resampled to {n} distinct colors"
            out_path = os.path.join(DIR, f"{base}_{n}.lut")
            write_lut(out_path, new_name, new_desc, new_entries)
            print(f"Wrote {out_path}  ({n} distinct colors x {256 // n} repeats)")


if __name__ == "__main__":
    main()
