import requests
import json
from typing import Dict, Any, List
from pathlib import Path
import csv
import logging
import time
from config import Config
from api_client import APIClient
from urllib.parse import urlencode

class ProyectosScraper:
    """
    Obtiene los proyectos de los académicos de la lista de académicos descargadas desde get_professors.py para una unidad definida.
    """
    def __init__(self):
        self.config = Config()
        self.api_client = APIClient()
        self.unidades_file = Path(self.config.paths['unidades_raw_data']) / "unidades.json"
        # Inicializar el logger
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        """Retorna el logger configurado"""
        logger = logging.getLogger('proyectos_scraper')        
        return logger

    def get_proyectos(self, id_persona: int) -> List[Dict[str, Any]]:
        """Obtiene los proyectos de un académico"""
        url = f"{self.config.api_base_url}{self.config.endpoints['proyectos']}"
        params = {
            'id_persona': id_persona,
            'limite': 30,
            'pagina': 1,
            'ano_desde': 2015,
            'id_resolucion': 2
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
                    # Verificar cada nivel de la estructura
                    if not result:
                        self.logger.info(f"Resultado vacío para académico {id_persona}")
                        return []
                    if 'academicos' not in result:
                        self.logger.info(f"No hay clave 'academicos' para académico {id_persona}")
                        return []
                    academicos = result['academicos']
                    projects_file = Path(self.config.paths['projects_raw_data']) / f"{id_persona}_projects.json"
                    projects_file.parent.mkdir(parents=True, exist_ok=True)
                    with open(projects_file, 'w', encoding = 'utf-8') as file:
                        json.dump(result, file, ensure_ascii=False, indent=4)
                    
                    if not isinstance(academicos, dict) or not academicos:
                        self.logger.info(f"'academicos' no es lista o está vacía para académico {id_persona}")
                        return []
                    # Obtener proyectos con get() para evitar KeyError
                    proyectos = academicos.get('proyectos', [])
                    if not proyectos:
                        self.logger.info(f"No hay proyectos para académico {id_persona}")
                        return []
                    return proyectos
                elif response.status_code == 204:
                    self.logger.info(f"No hay contenido (204) para académico {id_persona}")
                    return []
                self.logger.warning(
                    f"Intento {retry + 1}: Error {response.status_code} para académico {id_persona}"
                )
                if retry < self.config.scraping_config['max_retries'] - 1:
                    time.sleep(self.config.scraping_config['delay'])     
            except Exception as e:
                self.logger.error(f"Error en solicitud para académico {id_persona}: {str(e)}")
                if retry < self.config.scraping_config['max_retries'] - 1:
                    time.sleep(self.config.scraping_config['delay'])
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
                    proyectos_file = Path(self.config.paths['projects_raw_data']) / f"{id_persona}_projects.json"
                    self.logger.info(f"Obteniendo proyectos para {nombre_completo} (ID: {id_persona})")
                    if not Path.exists(proyectos_file):
                        proyectos = self.get_proyectos(id_persona)
                        if proyectos:
                            self.logger.info(f"Se encontraron {len(proyectos)} publicaciones para {nombre_completo}")
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
    # Configurar logging cuando se ejecuta directamente
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )
    
    scrapper = ProyectosScraper()
    scrapper.run_workflow()