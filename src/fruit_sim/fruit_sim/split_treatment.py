"""Cut one treatment section out of the Roza row splat.

The Roza row has three treatment sections laid end to end along the row:
    1 = pruned_thinned, 2 = pruned, 3 = control
Section 1 is at the low-x end of the row.

The row's long axis is found from the splat itself (PCA on x/y). Positions
along that axis are normalized to 0..1 from one end of the canopy to the other.
By default the cuts are at 1/3 and 2/3; change them with --cuts.

    python split_treatment.py in.ply out.ply control [--cuts 0.333 0.667]
"""
import argparse
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from crop_splat import read_ply, write_ply  # noqa: E402

TREATMENTS = ["pruned_thinned", "pruned", "control"]


def along_row(x, y):
    """Position of each splat along the row's long axis, 0 at the low-x end."""
    xy = np.column_stack([x, y]).astype(np.float64)
    xy -= xy.mean(axis=0)
    axis = np.linalg.svd(xy[::max(1, len(xy) // 200_000)], full_matrices=False)[2][0]
    if axis[0] < 0:  # SVD sign is arbitrary; make the axis point toward +x
        axis = -axis
    return xy @ axis


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input")
    ap.add_argument("output")
    ap.add_argument("treatment", choices=TREATMENTS)
    ap.add_argument("--cuts", type=float, nargs=2, default=[1 / 3, 2 / 3], metavar=("A", "B"),
                    help="section boundaries as fractions of row length (default 1/3 2/3)")
    args = ap.parse_args()

    header, data = read_ply(args.input)
    t = along_row(data["x"], data["y"])
    # Normalize using the canopy extent, ignoring stray splats past the row ends.
    lo, hi = np.percentile(t, [0.5, 99.5])
    frac = (t - lo) / (hi - lo)

    edges = [-np.inf, args.cuts[0], args.cuts[1], np.inf]
    i = TREATMENTS.index(args.treatment)
    mask = (frac >= edges[i]) & (frac < edges[i + 1])

    kept = np.ascontiguousarray(data[mask])
    print(f"{args.treatment}: kept {len(kept):,} of {len(data):,} splats")
    write_ply(args.output, header, kept)


if __name__ == "__main__":
    main()
