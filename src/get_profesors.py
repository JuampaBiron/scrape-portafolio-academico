import requests
import json
import sys
from typing import Dict, Any
from pathlib import Path
import logging
import time
# Agregar el directorio raíz del proyecto al path de Python
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
from api_client import APIClient
from config import Config


class ScraperAcademicos:
    def __init__(self):
        self.config = Config()
        self.logger = self._setup_logger()
        self.api_client = APIClient()
        self.unidades_file = Path(self.config.paths['unidades_raw_data']) / "unidades.json"

    def _setup_logger(self) -> logging.Logger:
        """Retorna el logger configurado"""
        return logging.getLogger('academicos_scraper')

    def get_academicos(self, reparticion: int) -> Dict[str, Any]:
        """
        Obtiene la lista completa de académicos para una repartición
        
        Args:
            reparticion: ID de la repartición académica
            
        Returns:
            Dict con los datos de los académicos o diccionario vacío si hay error
        """
        self.logger.info(f"Buscando académicos para repartición: {reparticion}")
        url = f"{self.config.api_base_url}{self.config.endpoints['academicos']}"
        self.logger.info(f"URL de la API: {url}")
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
                    self.logger.info(f"Datos obtenidos exitosamente para repartición {reparticion}")
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

    def save_academicos(self, reparticion: int, out_path:str) -> bool:
        """
        Obtiene y guarda la lista de académicos en un archivo JSON
        
        Args:
            reparticion: ID de la repartición académica
            
        Returns:
            bool: True si el proceso fue exitoso, False en caso contrario
        """        
        # Obtener datos
        data = self.get_academicos(reparticion)
        
        if not data:
            self.logger.error("No se obtuvieron datos de académicos")
            return False
            
        try:
            # Guardar datos
            
            total_academicos = data.get('total_resultado', 0)
            
            with open(out_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
            self.logger.info(f"Total de académicos encontrados: {total_academicos}")
            self.logger.info(f"Datos guardados en: {out_path}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error guardando datos: {str(e)}")
            return False

    def run_workflow(self):
        """
        Ejecuta el flujo de trabajo para obtener y guardar académicos
        """
        self.logger.info(f"Leyendo unidades desde: {self.unidades_file}")
        with open(self.unidades_file, 'r', encoding='utf-8') as file:
            try:
                unidades = json.load(file)
            except json.JSONDecodeError as e:
                self.logger.error(f"Error decodificando JSON: {str(e)}")
                return False

        for unidad in unidades:
            unidad_id = unidad.get('id')
            if not unidad_id:
                self.logger.warning(f"Unidad sin ID: {unidad}")
                continue
            try:            
                    # Crear archivo de salida
                    department_academics_file = Path(self.config.paths['academics_raw_data']) / f"{unidad_id}_academicos_raw.json"
                    if Path.exists(department_academics_file):
                        self.logger.info(f"Archivo ya existe: {department_academics_file}, omitiendo...")
                        continue
                    
                    # Obtener y guardar académicos
                    success = self.save_academicos(reparticion=unidad_id, out_path=department_academics_file)
                    
                    if success:
                        self.logger.info(f"✅ Académicos guardados para {unidad_id}")
                    else:
                        self.logger.error(f"❌ Error obteniendo académicos para {unidad_id}")

            except Exception as e:
                self.logger.error(f"Error leyendo archivo {self.unidades_file}: {str(e)}")
                continue
        
        self.logger.info("Flujo de trabajo completado exitosamente")
        return True

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )
    
    scraper = ScraperAcademicos()
    success = scraper.run_workflow()