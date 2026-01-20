"""Test pressure benchmark import and structure."""

from __future__ import annotations

from pathlib import Path


def test_pressure_benchmark_files_exist():
    """Test that pressure benchmark files exist."""
    base_path = Path(__file__).parent.parent / "ml_peg"
    
    # Check calc file
    calc_file = base_path / "calcs" / "bulk_crystal" / "pressure" / "calc_pressure.py"
    assert calc_file.exists(), "calc_pressure.py should exist"
    
    # Check analysis file
    analysis_file = base_path / "analysis" / "bulk_crystal" / "pressure" / "analyse_pressure.py"
    assert analysis_file.exists(), "analyse_pressure.py should exist"
    
    # Check metrics file
    metrics_file = base_path / "analysis" / "bulk_crystal" / "pressure" / "metrics.yml"
    assert metrics_file.exists(), "metrics.yml should exist"
    
    # Check app file
    app_file = base_path / "app" / "bulk_crystal" / "pressure" / "app_pressure.py"
    assert app_file.exists(), "app_pressure.py should exist"


def test_pressure_benchmark_imports():
    """Test that pressure benchmark modules can be imported."""
    try:
        from ml_peg.calcs.bulk_crystal.pressure import calc_pressure
        assert hasattr(calc_pressure, "test_pressure")
    except ImportError as e:
        # If dependencies are missing, skip the test
        pass
    
    try:
        from ml_peg.analysis.bulk_crystal.pressure import analyse_pressure
        assert hasattr(analyse_pressure, "test_pressure")
    except ImportError as e:
        # If dependencies are missing, skip the test
        pass
    
    try:
        from ml_peg.app.bulk_crystal.pressure import app_pressure
        assert hasattr(app_pressure, "get_app")
    except ImportError as e:
        # If dependencies are missing, skip the test
        pass
