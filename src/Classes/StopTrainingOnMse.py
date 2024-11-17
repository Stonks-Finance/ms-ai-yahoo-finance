import tensorflow as tf


class StopTrainingOnMSE(tf.keras.callbacks.Callback):
    
    def __init__ (self, threshold: float = 0.02):
        super().__init__()
        self.threshold = threshold
    
    def on_epoch_end (self, logs=None):
        if logs and logs.get("val_loss") is not None:
            val_loss = logs.get("val_loss")
            if val_loss < self.threshold:
                print(f"Stopping training as val_loss has reached below {self.threshold:.4f}")
                self.model.stop_training = True