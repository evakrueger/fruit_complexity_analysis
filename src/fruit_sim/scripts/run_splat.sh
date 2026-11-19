#!/usr/bin/env bash
# Launch Isaac Sim with the Gaussian splat loaded.
# Usage: src/fruit_sim/scripts/run_splat.sh [path/to/splat.usdc]
set -e

REPO="$(cd "$(dirname "$0")/../../.." && pwd)"
ISAAC_PY="${ISAAC_PY:-$HOME/isaacsim-env/bin/python}"
SPLAT="${1:-$REPO/data/gaussian_splats/splat.usdc}"

# If no ROS 2 is sourced, use the ROS 2 Humble libraries bundled with Isaac Sim.
if [ -z "$ROS_DISTRO" ]; then
    ISAAC_DIR="$("$ISAAC_PY" -c 'import isaacsim, os; print(os.path.dirname(isaacsim.__file__))')"
    export ROS_DISTRO=humble
    export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
    export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:$ISAAC_DIR/exts/isaacsim.ros2.core/humble/lib"
fi

exec "$ISAAC_PY" "$REPO/src/fruit_sim/fruit_sim/load_splat.py" "$SPLAT"
