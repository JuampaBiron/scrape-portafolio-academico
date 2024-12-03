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
    def __init__(self):
        self.config = Config()
        self.logger = self._setup_logger()
        self.api_client = APIClient()

    def _setup_logger(self) -> logging.Logger:
        """Configura y retorna un logger"""
        logger = logging.getLogger('publicaciones_scraper')
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger

    def get_publicaciones(self, id_persona: int) -> List[Dict[str, Any]]:
        """Obtiene las publicaciones de un académico"""
        url = f"{self.config.api_base_url}{self.config.endpoints['publicaciones']}"
        
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
                    
                    # Guardar datos crudos si existe el directorio
                    #raw_data_path = Path(self.config.paths['raw_data'])
                    #if raw_data_path.exists():
                    #    raw_file = raw_data_path / f'publicaciones_{id_persona}_raw.json'
                    #    with open(raw_file, 'w', encoding='utf-8') as f:
                    #        json.dump(result, f, indent=2, ensure_ascii=False)
                    
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

    def build_publicaciones_file(self) -> bool:
        """Construye un archivo CSV con todas las publicaciones"""
        try:
            # Crear directorios necesarios
            Path(self.config.paths['raw_data']).mkdir(exist_ok=True)
            Path(self.config.paths['data_dir']).mkdir(exist_ok=True)
            json_path = Path(self.config.paths['data_dir']) / "academicos_raw.json"
            
            # Corregido: Abrir el archivo JSON correctamente
            with open(json_path, 'r', encoding='utf-8') as file:
                academicos_list = json.load(file).get("academicos")
            # Obtener lista de IDs

            total_ids = len(academicos_list)
            self.logger.info(f"Procesando publicaciones para {total_ids} académicos...")
            
            output_file = Path(self.config.paths['data_dir']) / 'todas_las_publicaciones.csv'
            
            # Crear/abrir archivo CSV principal
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'ID Academico', 'Nombre Academico', 'Autores', 'Título', 'Año',
                    'Revista', 'Tipo', 'Link', 'DOI'
                ])
                
                # Procesar cada académico
                total_publicaciones = 0
                academicos_procesados = 0
                
                for i, json_academico in enumerate(academicos_list, 1):
                    id_academico = json_academico.get("id_persona")
                    nombre_academico = json_academico.get("nombre_completo")
                    self.logger.info(f"Procesando académico {i}/{total_ids} (Nombre: {nombre_academico})")
                    
                    publicaciones = self.get_publicaciones(id_academico)
                    # Consideramos exitoso el procesamiento incluso si no hay publicaciones
                    academicos_procesados += 1
                    
                    # Escribir publicaciones en el CSV si existen
                    for pub in publicaciones:
                        writer.writerow([
                            id_academico,
                            nombre_academico,
                            pub.get('Autores', ''),
                            pub.get('titulo_publicacion', ''),
                            pub.get('ano', ''),
                            pub.get('titulo_revistas', ''),
                            pub.get('tipo_publicacion', ''),
                            pub.get('link', ''),
                            pub.get('doi', '')
                        ])
                        total_publicaciones += 1
                    
                    if i % self.config.scraping_config['batch_size'] == 0:
                        self.logger.info(f"Progreso: {i}/{total_ids} académicos procesados")
                        self.logger.info(f"Total de publicaciones hasta ahora: {total_publicaciones}")
            
            self.logger.info("\nProceso completado!")
            self.logger.info(f"Total de académicos procesados: {academicos_procesados}/{total_ids}")
            self.logger.info(f"Total de publicaciones recopiladas: {total_publicaciones}")
            self.logger.info(f"Archivo guardado como: {output_file}")
            
            # Consideramos exitoso el proceso si se procesaron todos los académicos
            return academicos_procesados == total_ids
            
        except Exception as e:
            self.logger.error(f"Error crítico en el proceso de publicaciones: {str(e)}")
            return False

def main():
    scraper = PublicacionesScraper()
    scraper.build_publicaciones_file()

if __name__ == "__main__":
    main()