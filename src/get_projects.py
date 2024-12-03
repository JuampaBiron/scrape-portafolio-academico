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
    def __init__(self):
        self.config = Config()
        self.logger = self._setup_logger()
        self.api_client = APIClient()

    def _setup_logger(self) -> logging.Logger:
        """Configura y retorna un logger"""
        logger = logging.getLogger('proyectos_scraper')
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger

    def get_proyectos(self, id_persona: int) -> List[Dict[str, Any]]:
        """Obtiene los proyectos de un académico"""
        url = f"{self.config.api_base_url}{self.config.endpoints['proyectos']}"
        
        params = {
            'id_persona': id_persona,
            'limite': 30,
            'pagina': 1,
            'ano_desde': 2013,
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
                    
                    # Guardar datos crudos si existe el directorio
                    #raw_data_path = Path(self.config.paths['raw_data'])
                    #if raw_data_path.exists():
                    #    raw_file = raw_data_path / f'proyectos_{id_persona}_raw.json'
                    #    with open(raw_file, 'w', encoding='utf-8') as f:
                    #        json.dump(result, f, indent=2, ensure_ascii=False)
                    
                    # Debug log para ver la estructura
                    self.logger.debug(f"Estructura de respuesta: {json.dumps(result, indent=2)}")
                    
                    # Verificar cada nivel de la estructura
                    if not result:
                        self.logger.debug(f"Resultado vacío para académico {id_persona}")
                        return []
                        
                    if 'academicos' not in result:
                        self.logger.debug(f"No hay clave 'academicos' para académico {id_persona}")
                        return []
                        
                    academicos = result['academicos']
                    if not isinstance(academicos, dict) or not academicos:
                        self.logger.debug(f"'academicos' no es lista o está vacía para académico {id_persona}")
                        return []
                        
                        
                    # Obtener proyectos con get() para evitar KeyError
                    proyectos = academicos.get('proyectos', [])
                    if not proyectos:
                        self.logger.debug(f"No hay proyectos para académico {id_persona}")
                        return []
                        
                    return proyectos
                
                elif response.status_code == 204:
                    self.logger.debug(f"No hay contenido (204) para académico {id_persona}")
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

    def build_proyectos_file(self) -> bool:
        """Construye un archivo CSV con todos los proyectos"""
        try:
            # Crear directorios necesarios
            Path(self.config.paths['raw_data']).mkdir(exist_ok=True)
            Path(self.config.paths['data_dir']).mkdir(exist_ok=True)
            json_path = Path(self.config.paths['data_dir']) / "academicos_raw.json"
            
            # Corregido: Abrir el archivo JSON correctamente
            with open(json_path, 'r', encoding='utf-8') as file:
                academicos_list = json.load(file).get("academicos")

            if not academicos_list:
                self.logger.error("No se encontraron académicos en el archivo JSON")
                return False
                
            total_ids = len(academicos_list)
            self.logger.info(f"Procesando proyectos para {total_ids} académicos...")
            
            output_file = Path(self.config.paths['data_dir']) / 'todos_los_proyectos.csv'
            
            # Crear/abrir archivo CSV principal
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'ID Académico', 'Nombre Academico', 'Código', 'Título', 'Fecha Inicio',
                    'Fecha Término', 'Investigadores', 'Institución',
                    'Programa', 'Fuente'
                ])
                
                # Procesar cada académico
                total_proyectos = 0
                academicos_procesados = 0
                
                for i, json_academico in enumerate(academicos_list, 1):
                    id_academico = json_academico.get("id_persona")
                    nombre_academico = json_academico.get("nombre_completo")
                    self.logger.info(f"Procesando académico {i}/{total_ids} (Nombre: {nombre_academico})")
                    
                    try:
                        proyectos = self.get_proyectos(id_academico)
                        academicos_procesados += 1
                        
                        if proyectos:  # Solo escribir si hay proyectos
                            for proyecto in proyectos:
                                writer.writerow([
                                    id_academico,
                                    nombre_academico,
                                    proyecto.get('codigo', ''),
                                    proyecto.get('titulo', ''),
                                    proyecto.get('fecha_inicio', ''),
                                    proyecto.get('fecha_fin', ''),
                                    proyecto.get('investigadores', ''),
                                    proyecto.get('institucion', ''),
                                    proyecto.get('programa', ''),
                                    proyecto.get('fuente', '')
                                ])
                                total_proyectos += 1
                        
                        if i % self.config.scraping_config['batch_size'] == 0:
                            self.logger.info(f"Progreso: {i}/{total_ids} académicos procesados")
                            self.logger.info(f"Total de proyectos hasta ahora: {total_proyectos}")
                        
                        time.sleep(self.config.scraping_config['delay'])
                        
                    except Exception as e:
                        self.logger.error(f"Error procesando académico {id_academico}: {str(e)}")
                        continue
            
            self.logger.info("\nProceso completado!")
            self.logger.info(f"Total de académicos procesados: {academicos_procesados}/{total_ids}")
            self.logger.info(f"Total de proyectos recopilados: {total_proyectos}")
            self.logger.info(f"Archivo guardado como: {output_file}")
            
            # Consideramos exitoso si procesamos al menos algunos académicos
            return academicos_procesados > 0
            
        except Exception as e:
            self.logger.error(f"Error crítico en el proceso de proyectos: {str(e)}")
            return False

def main():
    scraper = ProyectosScraper()
    #print(scraper.get_all_ids())
    success = scraper.build_proyectos_file()
    
    if not success:
        logging.error("El proceso de obtención de proyectos falló")
        exit(1)

if __name__ == "__main__":
    main()