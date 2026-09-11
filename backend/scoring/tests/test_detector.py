import pytest
import os
from backend.scoring.vasp_detector import VaspDetector

def test_vasp_detector(tmp_path):
    # Create mock known_vasps.csv
    csv_file = tmp_path / "known_vasps.csv"
    csv_file.write_text("address,vasp_name\nVASP001,Exchange Alpha\nVASP002,Binance\n")
    
    detector = VaspDetector(str(csv_file))
    
    assert detector.get_vasp_name("VASP001") == "Exchange Alpha"
    assert detector.get_vasp_name("VASP002") == "Binance"
    assert detector.get_vasp_name("UNKNOWN") is None
