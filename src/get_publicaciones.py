import requests
import json
import csv
from typing import Dict, Any, List
from pathlib import Path
import time
from config import Config
import logging
from api_client import APIClient




class PublicacionesScraper:
    """
    Obtiene las publicaciones de los académicos de la lista de académicos descargadas desde get_professors.py para una unidad definida
    """
    def __init__(self):
        self.config = Config()
        self.api_client = APIClient()
        self.unidades_file = Path(self.config.paths['unidades_raw_data']) / "unidades.json"
        self.logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        """Retorna el logger configurado"""
        return logging.getLogger('publicaciones_scraper')

    def get_publicaciones(self, id_persona: int) -> List[Dict[str, Any]]:
        """Obtiene las publicaciones de un académico segun su ID"""
        url = f"{self.config.api_base_url}{self.config.endpoints['publicaciones']}"
        raw_publications = Path(self.config.paths['publications_raw_data'])/f"{id_persona}_publications.json"
        
        params = {
            'id_persona': id_persona,
            'limite': self.config.pagination['default_limit'],
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
                    result = self.api_client._decode_response(response.text)
                    # Guardar la respuesta cruda en un archivo JSON
                    raw_publications.parent.mkdir(parents=True, exist_ok=True)
                    with open(raw_publications, 'w', encoding = 'utf-8') as file:
                        json.dump(result, file, ensure_ascii=False, indent=4)
                    if 'academicos' in result and len(result['academicos']) > 0:
                        
                        return result['academicos'][0].get('publicaciones', [])
                    return []
                
                self.logger.warning(
                    f"Intento {retry + 1}: Error {response.status_code} para académico {id_persona}"
                )
                time.sleep(self.config.scraping_config['delay'])
                
            except Exception as e:
                self.logger.error(f"Error obteniendo publicaciones para {id_persona}: {str(e)}")
                if retry < self.config.scraping_config['max_retries'] - 1:
                    time.sleep(self.config.scraping_config['delay'])
                continue
                
        return []

    def run_workflow(self):
        """Ejecuta el flujo de trabajo para obtener publicaciones de todos los académicos"""
        try:

            unidades = json.load(open(self.unidades_file, 'r', encoding='utf-8'))

            for unidad in unidades:
                unidad_id = unidad.get('id')
                unidad_nombre = unidad.get('nombre')
                self.logger.info(f"** Procesando unidad: {unidad_nombre} **")
                profesores_file = Path(self.config.paths['academics_raw_data']) / f"{unidad_id}_academicos_raw.json"
                if not Path.exists(profesores_file):
                    self.logger.error(f"Archivo de académicos no encontrado para unidad {unidad_nombre} (ID: {unidad_id})")
                    continue
                profesores = json.load(open(profesores_file, 'r', encoding='utf-8')).get('academicos')
                for profesor in profesores:
                    id_persona = profesor.get('id_persona')
                    nombre_completo = profesor.get('nombre_completo')
                    publicaciones_file = Path(self.config.paths['publications_raw_data']) / f"{id_persona}_publications.json"
                    self.logger.info(f"Obteniendo publicaciones para {nombre_completo} (ID: {id_persona})")
                    if not Path.exists(publicaciones_file):
                        publicaciones = self.get_publicaciones(id_persona)
                        if publicaciones:
                            self.logger.info(f"Se encontraron {len(publicaciones)} publicaciones para {nombre_completo}")
                        else:
                            self.logger.info(f"No se encontraron publicaciones para {nombre_completo}")
                    else:
                        self.logger.info(f"Archivo de publicaciones ya existe para {nombre_completo}, omitiendo...")
        
            self.logger.info("Flujo de trabajo completado exitosamente")
            return True
        except Exception as e:
            self.logger.error(f"Error en el flujo de trabajo: {str(e)}")
            return False

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )
    
    scraper = PublicacionesScraper()
    scraper.run_workflow()
