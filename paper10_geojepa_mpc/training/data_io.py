from pathlib import Path
from typing import Dict, Tuple
import zipfile

from numpy.lib import format as np_format


def _read_npy_header(file_obj) -> Tuple[tuple, str]:
    version = np_format.read_magic(file_obj)
    if version == (1, 0):
        shape, _, dtype = np_format.read_array_header_1_0(file_obj)
    else:
        shape, _, dtype = np_format.read_array_header_2_0(file_obj)
    return tuple(shape), str(dtype)


def summarize_npz_headers(path: str | Path) -> Dict[str, Dict[str, object]]:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(path)

    summary = {}
    with zipfile.ZipFile(path) as archive:
        for name in archive.namelist():
            key = name[:-4] if name.endswith(".npy") else name
            with archive.open(name) as file_obj:
                shape, dtype = _read_npy_header(file_obj)
            summary[key] = {"shape": shape, "dtype": dtype}
    return summary
