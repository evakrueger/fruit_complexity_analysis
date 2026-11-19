# fruit_complexity_analysis

Load a Gaussian splat of the fruit scene into Isaac Sim 6.2.

## Setup (once)

```bash
python3 -m venv ~/isaacsim-env
~/isaacsim-env/bin/pip install "isaacsim[all,extscache]==6.2.0.0" --extra-index-url https://pypi.nvidia.com
```

Requires an NVIDIA GPU. RTX 50-series GPUs need the open driver (`nvidia-driver-580-open`).

## Run

```bash
src/fruit_sim/scripts/run_splat.sh                  # loads data/gaussian_splats/splat.usdc
src/fruit_sim/scripts/run_splat.sh other.usdc       # or any other .usdc
```

The first launch takes a few minutes while shaders compile. Once the scene loads, select `splat` in the Stage panel and press **F** to frame it.

## Convert a .ply splat to USD

```bash
python3 -m venv ~/gsplat-env
~/gsplat-env/bin/pip install "omniverse-gsplat-converter[usd]"
~/gsplat-env/bin/omni_gsplat_convert -i input.ply -o splat.usdc --up-axis Z -n splat
```

Use `.usdc`, not `.usdz`. Large `.usdz` files fail to open.

## Data

The splat files (`point_cloud*.ply`, `*.usdc`) are too large for GitHub and aren't in the repo. Put them in `data/gaussian_splats/` yourself.
