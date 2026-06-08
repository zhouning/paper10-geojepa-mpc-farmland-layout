"""Region-agnostic factory for CountyLevelEnv.

The bundled repository-level ``county_env.py`` is hardwired to Bishan
(DLTB_PATH, BLOCK_DIR,
ALL_TOWNSHIPS, TOWNSHIP_CODES are module-level constants). Rather than
fork the 900-line file, we monkey-patch those four constants before
instantiating CountyLevelEnv -- the same trick proven to work in
neijiang_cross_region/county_env_neijiang.py.

This module also captures the per-parcel BSM (the Third-National-Survey
patch ID) onto the env instance, so that after MPC the caller can map
env-internal parcel indices back to DLTB.shp rows by BSM lookup.

Public surface:
    make_env(prepared_dir, total_budget=500, swaps_per_step=5, proj_crs=None,
             **env_kwargs) -> CountyLevelEnv

`prepared_dir` must contain:
    DLTB_with_slope.gpkg                  (one parcel layer)
    blocks/township_<code>/block_compositions.json
    blocks/township_<code>/block_features.json   (compactness)
    blocks/township_<code>/parcel_block_mapping.csv (optional, not used here)
    townships.json                         {code: label, ...}

`townships.json` is the only new artifact this layout requires versus the
existing Bishan layout under results_real/blocks/. It is a 1-line
file recording which township codes the region contains. For the built-in
Bishan smoke test we synthesize it on the fly from county_env.ALL_TOWNSHIPS
(see _ensure_townships_json).
"""
import json
import os
import sys
from pathlib import Path
from typing import Optional


# Default UTM zone 48N (CGCS2000 / WGS84) -- works for most of central-west
# China including Chongqing (Bishan), Sichuan (Neijiang), Yunnan, etc. Users
# in other zones (NE / NW / SE coast) MUST override via proj_crs argument.
DEFAULT_PROJ_CRS = "EPSG:32648"
REPO_ROOT = Path(__file__).resolve().parents[2]

# Bishan canonical layout, used as a default when the smoke test is run
# without a prepared_dir.
BISHAN_DEFAULT_PREPARED = REPO_ROOT


def _ensure_townships_json(prepared_dir: Path, fallback_dict: Optional[dict] = None):
    """If townships.json doesn't exist, write one from a fallback dict.

    Returns the loaded dict (code -> label).
    """
    p = prepared_dir / "townships.json"
    if p.exists():
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    if fallback_dict is None:
        raise FileNotFoundError(
            f"{p} not found and no fallback provided. Tool 1 should produce "
            "townships.json alongside blocks/."
        )
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(fallback_dict, f, ensure_ascii=False, indent=2)
    return dict(fallback_dict)


def make_env(prepared_dir=None, total_budget=500, swaps_per_step=5,
             proj_crs=None, **env_kwargs):
    """Build a region-agnostic CountyLevelEnv via monkey-patching.

    Parameters
    ----------
    prepared_dir : str or Path or None
        Output directory of Tool 1. None = use the repository root layout
        (dem_slope_analysis/output/DLTB_with_slope.gpkg or .shp plus
         results_real/blocks/).
    total_budget, swaps_per_step : int
        Forwarded to CountyLevelEnv.
    proj_crs : str or None
        Override the projection used for area calculations. None =
        EPSG:32648 (UTM 48N). Set to EPSG:32649/47/etc. for other zones.
    **env_kwargs : dict
        Forwarded to CountyLevelEnv (slope_weight, baimu_weight, ...).
    """
    repo_root = str(REPO_ROOT)
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    import county_env

    prepared_dir = Path(prepared_dir) if prepared_dir else BISHAN_DEFAULT_PREPARED

    # Resolve dltb path under prepared_dir. Tool 1 v1.2+ writes .shp; the
    # original Bishan layout shipped a .gpkg. Prefer .shp when both exist.
    out_dir = prepared_dir / "dem_slope_analysis" / "output"
    shp_candidate = out_dir / "DLTB_with_slope.shp"
    gpkg_candidate = out_dir / "DLTB_with_slope.gpkg"
    if shp_candidate.exists():
        dltb_path = shp_candidate
    elif gpkg_candidate.exists():
        dltb_path = gpkg_candidate
    else:
        raise FileNotFoundError(
            f"DLTB layer not found under {out_dir} (looked for "
            f"DLTB_with_slope.shp and DLTB_with_slope.gpkg)"
        )
    block_dir = prepared_dir / "results_real" / "blocks"

    if not block_dir.exists():
        raise FileNotFoundError(f"Block dir not found: {block_dir}")

    # Resolve townships dict. Bishan default writes townships.json on first
    # run from county_env.ALL_TOWNSHIPS so that downstream code never has to
    # special-case Bishan vs prepared regions.
    if prepared_dir == BISHAN_DEFAULT_PREPARED:
        townships = _ensure_townships_json(prepared_dir, county_env.ALL_TOWNSHIPS)
    else:
        townships = _ensure_townships_json(prepared_dir)

    # Apply patches. Order: DLTB_PATH and BLOCK_DIR must be string paths,
    # not Path objects (county_env uses os.path.join with them).
    county_env.DLTB_PATH = str(dltb_path)
    county_env.BLOCK_DIR = str(block_dir)
    county_env.ALL_TOWNSHIPS = dict(townships)
    county_env.TOWNSHIP_CODES = sorted(townships.keys())
    if proj_crs:
        county_env.PROJ_CRS = proj_crs

    # Re-import the class after patching.
    from county_env import CountyLevelEnv

    # Instantiate. CountyLevelEnv reads the (now-patched) module globals
    # in its _load_data().
    env = CountyLevelEnv(total_budget=total_budget,
                         swaps_per_step=swaps_per_step, **env_kwargs)

    # Attach BSM array for shapefile write-back. CountyLevelEnv discards
    # the BSM column inside _load_data; recover it from the same gpkg
    # using the same WHERE filter so the row order matches.
    _attach_bsm(env, dltb_path, county_env.TOWNSHIP_CODES)

    # Record provenance for debugging
    env._prepared_dir = str(prepared_dir)
    env._dltb_path = str(dltb_path)
    env._block_dir = str(block_dir)
    env._townships = dict(townships)
    return env


def _attach_bsm(env, dltb_path, township_codes):
    """Read BSM column from the same DLTB gpkg using the same row order
    as CountyLevelEnv._load_data, and attach as env._parcel_bsm.

    CountyLevelEnv builds gdf_swap = gdf[type_code in {FARMLAND, FOREST}]
    then reset_index(drop=True). We replicate exactly that filter so the
    BSM array aligns with env's parcel indices 0..n_parcels-1.
    """
    import geopandas as gpd
    import numpy as np

    where = " OR ".join([f"QSDWDM LIKE '{c}%'" for c in township_codes])
    gdf = gpd.read_file(dltb_path, where=where)
    # CountyLevelEnv's _classify_type uses these same prefixes
    farm = gdf['DLBM'].astype(str).str.startswith(('011', '012', '013'))
    forest = gdf['DLBM'].astype(str).str.startswith(('031', '032', '033'))
    keep = farm | forest
    gdf_swap = gdf[keep].reset_index(drop=True)
    if len(gdf_swap) != env.n_parcels:
        raise RuntimeError(
            f"BSM alignment mismatch: gdf_swap has {len(gdf_swap)} rows but "
            f"env.n_parcels = {env.n_parcels}. Did the DLTB change between "
            "env build and BSM attach?"
        )
    if 'BSM' not in gdf_swap.columns:
        raise RuntimeError(
            f"DLTB gpkg missing required field 'BSM': {dltb_path}. "
            "Tool 1 must preserve BSM from the source shapefile."
        )
    env._parcel_bsm = gdf_swap['BSM'].values
