import requests
import json
from typing import Dict, Any
from pathlib import Path
import logging
from api_client import APIClient
from config import Config
import time

class AcademicosScraper:
    def __init__(self):
        self.config = Config()
        self.logger = self._setup_logger()
        self.api_client = APIClient()

    def _setup_logger(self) -> logging.Logger:
        """Configura y retorna un logger"""
        logger = logging.getLogger('academicos_scraper')
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger

    def get_academicos(self, reparticion: int) -> Dict[str, Any]:
        """
        Obtiene la lista completa de académicos para una repartición
        
        Args:
            reparticion: ID de la repartición académica
            
        Returns:
            Dict con los datos de los académicos o diccionario vacío si hay error
        """
        url = f"{self.config.api_base_url}{self.config.endpoints['academicos']}"
        
        params = {
            'reparticion': reparticion,
            'limite': self.config.pagination['max_limit'],
            'pagina': 1
        }

        for retry in range(self.config.scraping_config['max_retries']):
            try:
                response = requests.get(
                    url,
                    headers=self.config.api_headers,
                    params=params,
                    timeout=self.config.scraping_config['timeout']
                )

                if response.status_code == 200:
                    return self.api_client._decode_response(response.text)
                
                self.logger.warning(
                    f"Intento {retry + 1}: Error {response.status_code} al obtener académicos"
                )
                if retry < self.config.scraping_config['max_retries'] - 1:
                    time.sleep(self.config.scraping_config['delay'])
                    
            except Exception as e:
                self.logger.error(f"Error en intento {retry + 1}: {str(e)}")
                if retry < self.config.scraping_config['max_retries'] - 1:
                    time.sleep(self.config.scraping_config['delay'])
                    
        return {}

    def save_academicos(self, reparticion: int) -> bool:
        """
        Obtiene y guarda la lista de académicos en un archivo JSON
        
        Args:
            reparticion: ID de la repartición académica
            
        Returns:
            bool: True si el proceso fue exitoso, False en caso contrario
        """
        # Crear directorio si no existe
        output_path = Path(self.config.paths['data_dir'])
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Obtener datos
        data = self.get_academicos(reparticion)
        
        if not data:
            self.logger.error("No se obtuvieron datos de académicos")
            return False
            
        try:
            # Guardar datos
            output_file = output_path / 'academicos_raw.json'
            total_academicos = data.get('total_resultado', 0)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
            self.logger.info(f"Total de académicos encontrados: {total_academicos}")
            self.logger.info(f"Datos guardados en: {output_file}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error guardando datos: {str(e)}")
            return False

def main():
    # Configuración inicial
    reparticion = 788
    
    # Crear y ejecutar el scraper
    scraper = AcademicosScraper()
    success = scraper.save_academicos(reparticion)
    
    if not success:
        logging.error("El proceso de obtención de académicos falló")
        exit(1)

if __name__ == "__main__":
    main()