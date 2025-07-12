import requests
import json
import csv
from typing import Dict, Any, List
from pathlib import Path
import time
from config import Config
import logging
from api_client import APIClient

# Configurar el logging al inicio del archivo
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

class TesisScraper:
    def __init__(self):
        self.config = Config()
        self.api_client = APIClient()

    def get_tesis(self, id_persona: int) -> List[Dict[str, Any]]:
        """Obtiene las tesis de un académico"""
        url = f"{self.config.api_base_url}{self.config.endpoints['tesis']}"
        
        params = {
            'id_persona': id_persona,
            'id_estado_verif': 3,
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
                    if 'academicos' in result and len(result['academicos']) > 0:
                        return result['academicos'][0].get('tesis', [])
                    return []
                
                logging.warning(
                    f"Intento {retry + 1}: Error {response.status_code} para académico {id_persona}"
                )
                time.sleep(self.config.scraping_config['delay'])
                
            except Exception as e:
                logging.error(f"Error obteniendo tesis para {id_persona}: {str(e)}")
                if retry < self.config.scraping_config['max_retries'] - 1:
                    time.sleep(self.config.scraping_config['delay'])
                continue
                
        return []

    def build_tesis_file(self) -> bool:
        """Construye un archivo CSV con todas las tesis"""
        try:
            # Crear directorios necesarios
            Path(self.config.paths['raw_data']).mkdir(exist_ok=True)
            Path(self.config.paths['data_dir']).mkdir(exist_ok=True)
            json_path = Path(self.config.paths['data_dir']) / "academicos_raw.json"
            
            # Abrir el archivo JSON de académicos
            with open(json_path, 'r', encoding='utf-8') as file:
                academicos_list = json.load(file).get("academicos")

            total_ids = len(academicos_list)
            logging.info(f"Procesando tesis para {total_ids} académicos...")
            
            output_file = Path(self.config.paths['data_dir']) / 'todas_las_tesis.csv'
            
            # Crear/abrir archivo CSV principal
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'ID Académico',
                    'Nombre Académico',
                    'Autores',
                    'Título',
                    'Año',
                    'Facultad',
                    'Profesor Guía',
                    'Comisión',
                    'URL',
                    'Fuente'
                ])
                
                # Procesar cada académico
                total_tesis = 0
                academicos_procesados = 0
                
                for i, json_academico in enumerate(academicos_list[0:10], 1):
                    id_academico = json_academico.get("id_persona")
                    nombre_academico = json_academico.get("nombre_completo")
                    logging.info(f"Procesando académico {i}/{total_ids} (Nombre: {nombre_academico})")
                    
                    tesis_list = self.get_tesis(id_academico)
                    academicos_procesados += 1
                    
                    # Escribir tesis en el CSV si existen
                    for tesis in tesis_list:
                        writer.writerow([
                            id_academico,
                            nombre_academico,
                            tesis.get('autores', ''),
                            tesis.get('titulo', ''),
                            tesis.get('anio', ''),
                            tesis.get('facultad', ''),
                            tesis.get('profesor_guia', ''),
                            tesis.get('comision', ''),
                            tesis.get('url', ''),
                            tesis.get('fuente', '')
                        ])
                        total_tesis += 1
                    
                    if i % self.config.scraping_config['batch_size'] == 0:
                        logging.info(f"Progreso: {i}/{total_ids} académicos procesados")
                        logging.info(f"Total de tesis hasta ahora: {total_tesis}")
            
            logging.info("\nProceso completado!")
            logging.info(f"Total de académicos procesados: {academicos_procesados}/{total_ids}")
            logging.info(f"Total de tesis recopiladas: {total_tesis}")
            logging.info(f"Archivo guardado como: {output_file}")
            
            return academicos_procesados == total_ids
            
        except Exception as e:
            logging.error(f"Error crítico en el proceso de tesis: {str(e)}")
            return False

if __name__ == "__main__":
    scraper = TesisScraper()
    scraper.build_tesis_file()