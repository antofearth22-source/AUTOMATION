import unittest
import os
import sys
from pathlib import Path

# Add the project root to the path to allow imports from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils.paths import resource_path

class TestPaths(unittest.TestCase):

    def test_resource_path_resolves_correctly(self):
        """
        Tests that resource_path returns an absolute Path object.
        """
        path = resource_path()
        self.assertIsInstance(path, Path)
        self.assertTrue(path.is_absolute())

    def test_resource_path_finds_existing_file(self):
        """
        Tests that resource_path can correctly locate a known data file.
        """
        # We know this file should exist
        station_file_path = resource_path('data', 'stationlist.json')
        self.assertTrue(station_file_path.exists(), f"File not found at {station_file_path}")
        self.assertTrue(station_file_path.is_file())

    def test_resource_path_joins_parts(self):
        """
        Tests that resource_path correctly joins multiple path components.
        """
        expected_end = os.path.join('data', 'test.json')
        resolved_path = resource_path('data', 'test.json')
        self.assertTrue(str(resolved_path).endswith(expected_end))

if __name__ == '__main__':
    unittest.main()
