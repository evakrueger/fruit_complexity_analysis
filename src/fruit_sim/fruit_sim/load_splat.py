"""Launch Isaac Sim and open a Gaussian splat USD file.

Run with Isaac Sim's Python (use scripts/run_splat.sh, which sets this up):
    ~/isaacsim-env/bin/python load_splat.py /path/to/splat.usdc
"""
import os
import sys

import isaacsim
from isaacsim import SimulationApp

# Start the full Isaac Sim editor (same app as the `isaacsim` command).
full_app = os.path.join(os.path.dirname(isaacsim.__file__), "apps", "isaacsim.exp.full.kit")
app = SimulationApp({"headless": False}, experience=full_app)

import omni.usd  # noqa: E402  (must be imported after SimulationApp starts)

usd_path = os.path.abspath(sys.argv[1])
print(f"Opening {usd_path}")
omni.usd.get_context().open_stage(usd_path)

while app.is_running():
    app.update()

app.close()
