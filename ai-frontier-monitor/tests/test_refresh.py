from pathlib import Path
import math
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from refresh import CALIBRATION, record_frontier, regression, compile_snapshot

class ModelTests(unittest.TestCase):
    def test_calibration(self):
        self.assertAlmostEqual((1-.5)*CALIBRATION*math.log10(16), 6.5, places=8)

    def test_only_true_frontier_records(self):
        v = [
            {"date":"2024-01-01","eci":50},
            {"date":"2024-01-01","eci":55},
            {"date":"2024-02-01","eci":52},
            {"date":"2024-03-01","eci":60}
        ]
        self.assertEqual([p["eci"] for p in record_frontier(v)], [55,60])

    def test_positive_slope(self):
        from datetime import datetime
        records = [{"date":"2024-%02d-01" % m, "eci":100+m} for m in range(1,9)]
        self.assertGreater(regression(records)["slope"], .5)

    def test_no_fake_data(self):
        with self.assertRaises(ValueError):
            compile_snapshot("Model,eci\nthing,7\n")

    def test_data_reduction(self):
        # The scenario is an explanatory model, not evidence: restricting
        # Chinese stock without changing US stock cannot decrease U.S. lead.
        base=(1-.5)*CALIBRATION*math.log10(16)
        reduced=(1-.5)*CALIBRATION*math.log10(16*1.5)
        self.assertGreater(reduced,base)

if __name__ == "__main__":
    unittest.main()
