from pathlib import Path
import sys

def resource_path(*parts: str) -> Path:
    """
    Get the absolute path to a resource, works for dev and for PyInstaller.
    This function should be used for all file paths to assets and data files.
    """
    # PyInstaller creates a temp folder and stores path in _MEIPASS.
    # We use getattr to safely access it, falling back to the project root.
    base_path = Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parents[2]))

    return base_path.joinpath(*parts)

if __name__ == '__main__':
    # Test that the path generation works
    print(f"Running from base path: {resource_path()}")
    print(f"Path to stationlist.json: {resource_path('data', 'stationlist.json')}")
    # Verify the file exists at the resolved path
    station_file = resource_path('data', 'stationlist.json')
    if station_file.exists():
        print("SUCCESS: stationlist.json found at the resolved path.")
    else:
        print("ERROR: stationlist.json not found.")
