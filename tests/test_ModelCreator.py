import unittest
from unittest.mock import patch, MagicMock
from src.ModelCreator import ModelCreator
from keras.models import Sequential

class TestModelCreator(unittest.TestCase):

    @patch('src.ModelCreator.Tuner')
    def setUp(self, MockTuner):
        # Create a mock for Tuner
        self.tuner_mock = MockTuner.return_value
        self.model_creator = ModelCreator(
            project_name='TestProject',
            stock_symbol='AAPL',
            fmt='.h5',
            intervals=['1d', '1wk']
        )

    def test_initialization(self):
        self.assertEqual(self.model_creator.project_name, 'TestProject')
        self.assertEqual(self.model_creator.stock_symbol, 'AAPL')
        self.assertEqual(self.model_creator.intervals, ['1d', '1wk'])
        self.assertIsNone(self.model_creator.models)

    @patch('src.ModelCreator.keras.Model.save')
    def test_save_models(self, mock_save):
        self.model_creator.models = {
            '1d_AAPL_model': Sequential(),  # Mocking a model
            '1wk_AAPL_model': Sequential()
        }
        self.model_creator.save_models('models/')
        self.assertEqual(mock_save.call_count, 2)

    @patch('src.ModelCreator.ModelCreator.tune')
    def test_train_tune(self, mock_tune):
        mock_tune.return_value = Sequential()  # Mocking the returned model
        models = self.model_creator.train_tune()
        self.assertEqual(len(models), 2)  # Expecting two models for two intervals
        self.assertIn('1d_AAPL_model', models)
        self.assertIn('1wk_AAPL_model', models)

if __name__ == '__main__':
    unittest.main()