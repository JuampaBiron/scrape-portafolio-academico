from pathlib import Path
import yaml
from typing import Any, Dict

class Config:
    _instance = None
    _config: Dict[str, Any] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config()
        return cls._instance
    
    def _load_config(self) -> None:
        """Carga la configuración desde YAML"""
        config_path = Path(__file__).parent / "config.yaml"
        with open(config_path, 'r', encoding='utf-8') as f:
            self._config = yaml.safe_load(f)
            
        # Crear directorios necesarios
        for dir_path in self._config['paths'].values():
            Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    @property
    def api_base_url(self) -> str:
        return self._config['api']['base_url']
    
    @property
    def api_headers(self) -> Dict[str, str]:
        headers = self._config['api']['headers'].copy()
        headers['Authorization'] = self._config['api']['auth_token']
        return headers
    
    @property
    def endpoints(self) -> Dict[str, str]:
        return self._config['api']['endpoints']
    
    @property
    def scraping_config(self) -> Dict[str, Any]:
        return self._config['scraping']
    
    @property
    def paths(self) -> Dict[str, str]:
        return self._config['paths']
    
    @property
    def pagination(self) -> Dict[str, int]:
        return self._config['pagination']

# Ejemplo de uso:
if __name__ == "__main__":
    config = Config()
    print(f"API URL: {config.api_base_url}")
    print(f"Headers: {config.api_headers}")