"""Crop a Gaussian splat .ply to an oriented box.

The box is given in the splat's own coordinates (Z-up, meters), which are the
same as Isaac Sim world coordinates for data/gaussian_splats/splat.usdc.

    python crop_splat.py in.ply out.ply --center X Y Z --size SX SY SZ [--yaw DEG]

--size is the full box extent (not half). --yaw rotates the box about Z.
Use --dry-run to only report how many splats fall inside.
"""
import argparse
import sys

import numpy as np

PLY_TYPES = {
    "float": "f4", "float32": "f4", "double": "f8", "float64": "f8",
    "uchar": "u1", "uint8": "u1", "char": "i1", "int8": "i1",
    "ushort": "u2", "uint16": "u2", "short": "i2", "int16": "i2",
    "uint": "u4", "uint32": "u4", "int": "i4", "int32": "i4",
}


def read_ply(path):
    with open(path, "rb") as f:
        header = []
        while True:
            line = f.readline()
            if not line:
                sys.exit(f"{path}: no end_header found")
            header.append(line)
            if line.strip() == b"end_header":
                break
        offset = f.tell()

    if b"binary_little_endian" not in header[1]:
        sys.exit(f"{path}: only binary_little_endian PLY is supported")

    count, fields, in_vertex = None, [], False
    for line in header:
        parts = line.decode("ascii", "replace").split()
        if parts[:1] == ["element"]:
            in_vertex = parts[1] == "vertex"
            if in_vertex:
                count = int(parts[2])
            elif count is not None:
                sys.exit(f"{path}: elements after 'vertex' are not supported")
        elif parts[:1] == ["property"] and in_vertex:
            if parts[1] == "list":
                sys.exit(f"{path}: list properties are not supported")
            fields.append((parts[2], "<" + PLY_TYPES[parts[1]]))

    data = np.memmap(path, dtype=np.dtype(fields), mode="r", offset=offset, shape=(count,))
    return header, data


def write_ply(path, header, data):
    with open(path, "wb") as f:
        for line in header:
            if line.startswith(b"element vertex"):
                line = f"element vertex {len(data)}\n".encode()
            elif line.startswith((b"comment min", b"comment max")):
                continue  # stale bounds; drop them
            f.write(line)
        data.tofile(f)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input")
    ap.add_argument("output", nargs="?")
    ap.add_argument("--center", type=float, nargs=3, required=True, metavar=("X", "Y", "Z"))
    ap.add_argument("--size", type=float, nargs=3, required=True, metavar=("SX", "SY", "SZ"))
    ap.add_argument("--yaw", type=float, default=0.0, help="box rotation about Z, degrees")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    if not args.dry_run and not args.output:
        ap.error("output path required unless --dry-run")

    header, data = read_ply(args.input)
    print(f"Loaded {len(data):,} splats from {args.input}")

    # Move points into the box frame: subtract center, rotate by -yaw.
    c, s = np.cos(np.radians(args.yaw)), np.sin(np.radians(args.yaw))
    dx = data["x"] - args.center[0]
    dy = data["y"] - args.center[1]
    dz = data["z"] - args.center[2]
    lx = c * dx + s * dy
    ly = -s * dx + c * dy
    half = np.asarray(args.size) / 2
    mask = (np.abs(lx) <= half[0]) & (np.abs(ly) <= half[1]) & (np.abs(dz) <= half[2])

    kept = data[mask]
    print(f"Kept {len(kept):,} splats ({100 * len(kept) / len(data):.1f}%)")
    if len(kept) == 0:
        sys.exit("Box contains no splats; check center/size/yaw")
    if not args.dry_run:
        write_ply(args.output, header, np.ascontiguousarray(kept))
        print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
