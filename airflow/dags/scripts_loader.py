"""Module for dynamically loading and executing scripts in Airflow DAGs."""
import importlib.util
import os

from airflow.utils.log.logging_mixin import LoggingMixin


class ScriptLoader:
    """Initialize and executes a script given its file path."""

    def __init__(self, script_path: str):
        """Initialize Script Loader with the path to the script."""
        self.script_path = script_path
        self.log = LoggingMixin().log

    def load_and_run(self):
        """Load and execute a script dynamically."""
        if not os.path.exists(self.script_path):
            raise FileNotFoundError(f"Script not found: {self.script_path}")

        # Load the module dynamically
        spec = importlib.util.spec_from_file_location(
            "dynamic_script", self.script_path
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        self.log.info(f"Executing script: {self.script_path}...")

        # Ejecutar el módulo (suponiendo que el script tiene una función 'main')
        try:
            module.main()
        except AttributeError:
            self.log.error(
                f"The script {self.script_path} does not have a 'main' function."
            )
            raise

        self.log.info(f"Script {self.script_path} completed successfully")
