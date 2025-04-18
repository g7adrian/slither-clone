import unittest
import math
from snake import Snake # Import the class we want to test

class TestSnakeSizeCalculation(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Helper to run the calculation we are testing
        cls.calculate = Snake._calculate_size

    def test_monotonicity(self):
        """Test that radius and length are monotonically increasing with weight."""
        last_radius, last_length = self.calculate(1)
        # Use a slightly larger starting weight to avoid potential float issues at exactly 1
        last_radius, last_length = self.calculate(1.1)

        for weight in range(2, 1000000):
            # Test with float weights too for continuity
            float_weight = float(weight)
            current_radius, current_length = self.calculate(float_weight)

            # Use assertGreaterEqual allowing for tiny float inaccuracies
            self.assertGreaterEqual(current_radius, last_radius - 1e-9, f"Radius decreased at weight {float_weight}")
            self.assertGreaterEqual(current_length, last_length - 1e-9, f"Length decreased at weight {float_weight}")

            last_radius, last_length = current_radius, current_length

    def test_area_relationship_continuous(self):
        """Test the relationship weight = length * area for continuous length."""
        TOLERANCE = 1e-7 # Define tolerance for float comparison

        last_log = 0

        for weight in range(1, 1000001): # Test integer weights
            float_weight = float(weight)
            radius, length = self.calculate(float_weight)

            if math.floor(math.log10(weight)) != last_log:
                last_log = math.floor(math.log10(weight))
                print(f"Weight: {weight}, Radius: {radius}, Length: {length}")

            if radius <= 1e-9 or length <= 1e-9: continue # Avoid issues with near-zero values

            segment_area = math.pi * radius**2
            calculated_weight_low = length * segment_area
            calculated_weight_high = (length + 1) * segment_area
            # Assert that the calculated weight is almost equal to the input weight
            self.assertGreaterEqual(float_weight, calculated_weight_low,
                                   msg=f"Weight ({float_weight}) != length*area ({calculated_weight_low}) for R={radius}, L={length}")
            self.assertLessEqual(float_weight, calculated_weight_high,
                                   msg=f"Weight ({float_weight}) != length*area ({calculated_weight_high}) for R={radius}, L={length}")

if __name__ == '__main__':
    unittest.main() 