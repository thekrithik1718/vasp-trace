import csv
import os
from typing import Optional

def load_known_vasps(filepath: str) -> dict:
    vasp_dict = {}
    if not os.path.exists(filepath):
        return vasp_dict
    with open(filepath, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            vasp_dict[row['address']] = row['vasp_name']
    return vasp_dict

class VaspDetector:
    def __init__(self, data_filepath: str):
        self.known_vasps = load_known_vasps(data_filepath)

    def get_vasp_name(self, address: str) -> Optional[str]:
        """
        Checks if an address is a known VASP.
        Returns the VASP name if found, else None.
        """
        return self.known_vasps.get(address)
