import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from paper10_geojepa_mpc.training.data_io import summarize_npz_headers


SMOKE_TOOL2 = (
    ROOT / "arcgis_toolbox_paper9" / "_scratch" / "tool1_smoke" / "prepared" / "tool2"
)


def main() -> None:
    for dataset_name in ("transitions", "pairwise"):
        path = SMOKE_TOOL2 / f"{dataset_name}.npz"
        print(f"{dataset_name}: {path}")
        print(json.dumps(summarize_npz_headers(path), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
