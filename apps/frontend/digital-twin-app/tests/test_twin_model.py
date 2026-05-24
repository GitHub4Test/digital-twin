"""
Twin Model Unit Tests - Frontend
Tests for twin_model.py covering temperature prediction using linear regression
"""

import sys
import os
import unittest
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../apps/frontend/digital-twin-app/src'))
from digital_twin_app.twin_model import predict_next


class TestPredictNext(unittest.TestCase):
    """Test suite for temperature prediction model"""

    def test_predict_next_single_value(self):
        """With single value, should return that value"""
        result = predict_next([10])
        self.assertEqual(result, 10)

    def test_predict_next_two_values(self):
        """With two values, should return last value"""
        result = predict_next([1, 2])
        self.assertEqual(result, 2)

    def test_predict_next_returns_float(self):
        """Result should be a float"""
        result = predict_next([1, 2, 3])
        self.assertIsInstance(result, (int, float))

    def test_predict_next_linear_ascending(self):
        """Linear ascending sequence should predict correctly"""
        values = [1, 2, 3, 4, 5]
        prediction = predict_next(values)
        self.assertAlmostEqual(prediction, 6.0, places=1)

    def test_predict_next_linear_descending(self):
        """Linear descending sequence should predict correctly"""
        values = [10, 8, 6, 4, 2]
        prediction = predict_next(values)
        self.assertAlmostEqual(prediction, 0.0, places=1)

    def test_predict_next_constant_values(self):
        """Constant values should predict the same value"""
        values = [5.0, 5.0, 5.0, 5.0, 5.0]
        prediction = predict_next(values)
        self.assertAlmostEqual(prediction, 5.0, places=1)

    def test_predict_next_float_values(self):
        """Should handle float values correctly"""
        values = [1.5, 2.5, 3.5, 4.5]
        prediction = predict_next(values)
        self.assertIsInstance(prediction, (int, float))
        self.assertGreater(prediction, 4.0)

    def test_predict_next_negative_values(self):
        """Should handle negative values"""
        values = [-10, -5, 0, 5, 10]
        prediction = predict_next(values)
        self.assertAlmostEqual(prediction, 15.0, places=1)

    def test_predict_next_mixed_signs(self):
        """Should handle values with mixed signs"""
        values = [-2, -1, 0, 1, 2]
        prediction = predict_next(values)
        self.assertAlmostEqual(prediction, 3.0, places=1)

    def test_predict_next_large_values(self):
        """Should handle large values"""
        values = [1000, 2000, 3000, 4000, 5000]
        prediction = predict_next(values)
        self.assertAlmostEqual(prediction, 6000.0, places=0)

    def test_predict_next_small_decimal_values(self):
        """Should handle small decimal values"""
        values = [0.1, 0.2, 0.3, 0.4]
        prediction = predict_next(values)
        self.assertGreater(prediction, 0.4)

    def test_predict_next_returns_rounded_to_2_decimals(self):
        """Result should be rounded to 2 decimal places"""
        values = [1.111, 2.222, 3.333]
        prediction = predict_next(values)
        decimal_places = len(str(prediction).split('.')[-1]) if '.' in str(prediction) else 0
        self.assertLessEqual(decimal_places, 2)

    def test_predict_next_with_noise(self):
        """Should still predict reasonable trend with noisy data"""
        values = [1, 1.9, 3.1, 4.0, 5.1]
        prediction = predict_next(values)
        self.assertGreater(prediction, 5)
        self.assertLess(prediction, 8)

    def test_predict_next_realistic_temperature_trend(self):
        """Should predict temperature trend realistically"""
        values = [20.0, 21.5, 23.0, 24.5, 26.0]
        prediction = predict_next(values)
        self.assertGreater(prediction, 26.0)
        self.assertLess(prediction, 28.0)

    def test_predict_next_cooling_trend(self):
        """Should predict decreasing temperature"""
        values = [30.0, 28.5, 27.0, 25.5, 24.0]
        prediction = predict_next(values)
        self.assertLess(prediction, 24.0)
        self.assertGreater(prediction, 20.0)

    def test_predict_next_three_values_minimum(self):
        """Should work with exactly 3 values"""
        values = [1, 2, 3]
        prediction = predict_next(values)
        self.assertAlmostEqual(prediction, 4.0, places=1)

    def test_predict_next_many_values(self):
        """Should work with many values"""
        values = list(range(1, 101))
        prediction = predict_next(values)
        self.assertAlmostEqual(prediction, 101.0, places=0)

    def test_predict_next_empty_list_raises_error(self):
        """Empty list should raise an error or handle gracefully"""
        with self.assertRaises((IndexError, ValueError)):
            predict_next([])

    def test_predict_next_consistency(self):
        """Same input should always produce same output"""
        values = [1, 2, 3, 4, 5]
        result1 = predict_next(values)
        result2 = predict_next(values)
        self.assertEqual(result1, result2)

    def test_predict_next_with_numpy_array(self):
        """Should work with numpy array input"""
        values = np.array([1, 2, 3, 4, 5])
        prediction = predict_next(values)
        self.assertAlmostEqual(prediction, 6.0, places=1)

    def test_predict_next_rapid_oscillation(self):
        """Should handle rapid oscillations"""
        values = [1, 100, 2, 99, 3, 98]
        prediction = predict_next(values)
        self.assertIsInstance(prediction, (int, float))

    def test_predict_next_polynomial_like_data(self):
        """Linear regression should fit polynomial-like data with deviation"""
        values = [1, 4, 9, 16, 25]  # x^2 values
        prediction = predict_next(values)
        self.assertIsInstance(prediction, (int, float))
        self.assertGreater(prediction, 25)

    def test_predict_next_sensor_reading_sequence(self):
        """Should predict next temperature from typical sensor readings"""
        temp_readings = [22.1, 22.3, 22.5, 22.8, 23.0]
        prediction = predict_next(temp_readings)
        self.assertGreater(prediction, 23.0)
        self.assertLess(prediction, 23.5)


if __name__ == '__main__':
    unittest.main()
