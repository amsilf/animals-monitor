import yaml
from pathlib import Path
from dotenv import load_dotenv
import os

class ConfigLoader:
    def __init__(self, config_path="config/config.yaml"):
        # Load environment variables
        load_dotenv()
        
        # Load YAML config
        with open(config_path, 'r') as file:
            self.config = yaml.safe_load(file)
    
    def get_camera_config(self):
        return self.config.get('camera', {})
    
    def get_storage_config(self):
        return self.config.get('storage', {})
    
    def get_aws_config(self):
        return self.config.get('aws', {})