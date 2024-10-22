import unittest
from unittest.mock import patch
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from src.get_data import scale_data, prepare_data, create_sequences

class TestGetData(unittest.TestCase):

    def setUp(self):
        # Sample data for testing
        self.train_data = pd.DataFrame({
            "Adj Close": [1, 2, 3, 4, 5]
        })
        self.test_data = pd.DataFrame({
            "Adj Close": [6, 7, 8, 9, 10]
        })
        self.scaler = MinMaxScaler()

    def test_range_of_scaled_values(self):
        # Example of proper training data
        train_data = pd.DataFrame({
            "Adj Close": [1, 2, 3, 4, 5]  # Variation in training data
        })
        test_data = pd.DataFrame({
            "Adj Close": [1, 2, 3, 4, 5]  # Match or stay within the training data range
        })
        
        # Scale the data
        train_scaled, test_scaled = scale_data(train_data, test_data)

        # Check if scaled values are within the range [0, 1]
        self.assertTrue((train_scaled >= 0).all() and (train_scaled <= 1).all(),
                        "All training scaled values should be in the range [0, 1]")
        self.assertTrue((test_scaled >= 0).all() and (test_scaled <= 1).all(),
                        "All test scaled values should be in the range [0, 1]")


    def test_preservation_of_relationships(self):
        # Using a small dataset
        small_train_data = pd.DataFrame({
            "Adj Close": [10, 20, 30]
        })
        small_test_data = pd.DataFrame({
            "Adj Close": [40, 50, 60]
        })
        
        # Scale the small data
        scaled_train, scaled_test = scale_data(small_train_data, small_test_data)

        # Check relationships
        self.assertTrue(scaled_train[0] < scaled_train[1] < scaled_train[2],
                        "Relationships between scaled training values should be preserved")
        self.assertTrue(scaled_test[0] < scaled_test[1] < scaled_test[2],
                        "Relationships between scaled test values should be preserved")

    def test_empty_data_scaling(self):
        empty_train_data = pd.DataFrame(columns=["Adj Close"])
        empty_test_data = pd.DataFrame(columns=["Adj Close"])
        with self.assertRaises(ValueError):
            # This assumes that the scaling function raises a ValueError for empty input
            scale_data(empty_train_data, empty_test_data)

    @patch('src.get_data.yf.download')  # Mock the yfinance download method
    def test_prepare_data(self, mock_download):
        # Mocked return value for Yahoo Finance API
        mock_download.return_value = pd.DataFrame({
            "Adj Close": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        }, index=pd.date_range(start='1/1/2020', periods=10, freq='h'))

        stock_name = "AAPL"
        train_data, test_data = prepare_data(stock_name, interval="1h")

        # Check that train_data and test_data are numpy arrays
        self.assertIsInstance(train_data, np.ndarray, "Training data should be a numpy array")
        self.assertIsInstance(test_data, np.ndarray, "Test data should be a numpy array")

        # Check that train_data is not empty
        self.assertGreater(train_data.shape[0], 0, "Training data should not be empty")
        # Check that test_data is not empty
        self.assertGreater(test_data.shape[0], 0, "Test data should not be empty")

        # Check the range of scaled values
        self.assertTrue((train_data >= 0).all() and (train_data <= 1).all(), "All training scaled values should be in the range [0, 1]")

        # Check shape consistency: assume 80% training and 20% testing
        expected_train_size = int(0.8 * 10)  # 10 total entries
        expected_test_size = 10 - expected_train_size

        self.assertEqual(train_data.shape[0], expected_train_size, "Training data size should be 80% of total data")
        self.assertEqual(test_data.shape[0], expected_test_size, "Testing data size should be 20% of total data")

    def test_create_sequences(self):
        data = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        x, y = create_sequences(data, seq_length=3)

        expected_x = np.array([
            [1, 2, 3],
            [2, 3, 4],
            [3, 4, 5],
            [4, 5, 6],
            [5, 6, 7],
            [6, 7, 8],
            [7, 8, 9]
        ])
        expected_y = np.array([4, 5, 6, 7, 8, 9, 10])

        # Assert that the generated sequences match the expected values
        np.testing.assert_array_equal(x, expected_x)
        np.testing.assert_array_equal(y, expected_y)

if __name__ == '__main__':
    unittest.main()