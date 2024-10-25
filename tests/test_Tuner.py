import unittest
from unittest.mock import patch, MagicMock
from src.Tuner import Tuner


class TestTuner(unittest.TestCase):

    @patch('src.Tuner.keras.models.Sequential')
    def setUp(self, MockModel):
        self.tuner = Tuner(
            project_name='TestProject',
            fmt='.keras',
            max_trials=5,
            executions_per_trial=2
        )

    def test_initialization(self):
        self.assertEqual(self.tuner.project_name, 'TestProject')
        self.assertEqual(self.tuner.max_trials, 5)

    def test_build_model(self):
        hp_mock = MagicMock()
        hp_mock.Int.return_value = 64  # Mocking the hyperparameter return
        model = self.tuner.build_model(hp_mock)
        self.assertIsNotNone(model)

    @patch('src.Tuner.prepare_data')
    @patch('src.Tuner.create_sequences')
    @patch('src.Tuner.RandomSearch')
    def test_tune(self, MockRandomSearch, mock_create_sequences, mock_prepare_data):
        mock_prepare_data.return_value = (MagicMock(), MagicMock())
        mock_create_sequences.return_value = (MagicMock(), MagicMock())
        mock_tuner_instance = MockRandomSearch.return_value

        best_model = self.tuner.tune('AAPL', '1d')
        self.assertIsNotNone(best_model)


if __name__ == '__main__':
    unittest.main()

