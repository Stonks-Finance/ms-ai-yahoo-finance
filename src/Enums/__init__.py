import pkgutil
import importlib

# Dynamically import all modules in the package
__all__ = [name for _, name, _ in pkgutil.iter_modules(__path__)]

for module in __all__:
    importlib.import_module(f"src.Enums.{module}")
