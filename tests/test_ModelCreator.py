import os
import unittest
from unittest.mock import patch
from src.Classes.ModelCreator import ModelCreator
from keras.models import Sequential

class TestModelCreator(unittest.TestCase):

    @patch('src.Classes.ModelCreator.Tuner')
    def setUp(self, MockTuner):
        self.tuner_mock = MockTuner.return_value
        self.model_creator = ModelCreator(
            stock_symbol='AAPL',
            fmt='.h5',
            intervals=['1d', '1wk']
        )

    def test_initialization(self):
        self.assertEqual(self.model_creator.stock_symbol, 'AAPL')
        self.assertEqual(self.model_creator.fmt, '.h5')
        self.assertEqual(self.model_creator.intervals, ['1d', '1wk'])
        self.assertEqual(self.model_creator.models,
                         os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, "models")))

    @patch('src.Classes.ModelCreator.keras.Model.save')
    def test_save_models(self, mock_save):
        self.model_creator.models = {
            '1d_AAPL_model': Sequential(),  # Mocking a model
            '1wk_AAPL_model': Sequential()
        }

        for model_name, model in self.model_creator.models.items():
            model.save(
                os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, "models",
                             f"{model_name}.h5")))

        self.assertEqual(mock_save.call_count, 2)

    @patch('src.Classes.ModelCreator.ModelCreator.train_tune')
    def test_train_tune(self, mock_tune):
        mock_model = Sequential()
        mock_tune.return_value = {
            '1d_AAPL_model': mock_model,
            '1wk_AAPL_model': mock_model
        }
        models = self.model_creator.train_tune()
        self.assertEqual(len(models), 2)  # Expecting two models for two intervals
        self.assertIn('1d_AAPL_model', models)
        self.assertIn('1wk_AAPL_model', models)

if __name__ == '__main__':
    unittest.main()