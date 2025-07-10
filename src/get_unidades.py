import requests
import json
from typing import Dict, Any
from pathlib import Path
import logging
from api_client import APIClient
from config import Config
import time
# Configurar el logging al inicio del archivo
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
class UnidadesScraper:
    """
    Obtiene la lista completa de las unidades de la Universidad de Chile en Portafolio Académico. 
    No forma parte del main pero es un recurso para investigar la ids de las unidades que se quiera escrapear.
    A la fecha, las unidades corresponden a las siguientes:
    2264   Centro de Extensión Artística y Cultural "D. S. C."
    328   Facultad de Arquitectura y Urbanismo
    420   Facultad de Artes
    526   Facultad de Ciencias
    560   Facultad de Ciencias Agronómicas
    882   Facultad de Ciencias Forestales y de la Conservación de la Naturalez
    788   Facultad de Ciencias Físicas y Matemáticas
    915   Facultad de Ciencias Químicas y Farmacéuticas
    943   Facultad de Ciencias Sociales
    1023   Facultad de Ciencias Veterinarias y Pecuarias
    2683   Facultad de Comunicación e Imagen
    1108   Facultad de Derecho
    649   Facultad de Economía y Negocios
    1212   Facultad de Filosofía y Humanidades
    2682   Facultad de Gobierno
    1261   Facultad de Medicina
    1560   Facultad de Odontología
    2058   Hospital Clínico
    1929   Instituto de Asuntos Públicos
    1975   Instituto de Estudios Avanzados en Educación
    1849   Instituto de Estudios Internacionales
    1803   Instituto de Nutrición y Tecnología de los Alimentos, Profesor Doctor Fernando Mönckeberg Barros
    297   Vicerrectoría de Asuntos Estudiantiles y Comunitarios
    """
    def __init__(self):
        self.config = Config()
        self.api_client = APIClient()

    def get_unidades(self) -> Dict[str, Any]:
        """
        Obtiene la lista completa de académicos para una repartición
        
        Args:
            reparticion: ID de la repartición académica
            
        Returns:
            Dict con los datos de los académicos o diccionario vacío si hay error
        """
        url = f"{self.config.api_base_url}{self.config.endpoints['unidades']}"
        logging.info(f"Buscando url: {url}")
        params = {
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
                    dic_unidades = self.api_client._decode_response(response.text)
                    #for elemento in dic_unidades:
                        #print(elemento['id']," ", elemento["nombre"])
                    # Guardar la respuesta cruda en un archivo JSON
                    raw_unidades_path = Path(self.config.paths['unidades_raw_data'])
                    raw_unidades_path.mkdir(parents=True, exist_ok=True)
                    with open(raw_unidades_path / 'unidades.json', 'w', encoding='utf-8') as file:
                        json.dump(dic_unidades, file, ensure_ascii=False, indent=4)
                    return self.api_client._decode_response(response.text)
                
                logging.warning(
                    f"Intento {retry + 1}: Error {response.status_code} al obtener académicos"
                )
                if retry < self.config.scraping_config['max_retries'] - 1:
                    time.sleep(self.config.scraping_config['delay'])
                    
            except Exception as e:
                logging.error(f"Error en intento {retry + 1}: {str(e)}")
                if retry < self.config.scraping_config['max_retries'] - 1:
                    time.sleep(self.config.scraping_config['delay'])  
        return {}


if __name__ == "__main__":
    scrapper = UnidadesScraper()
    scrapper.get_unidades()