import requests
import base64
import json
import urllib.parse
from api_client import APIClient

class UChileAPIClient:
    """
    Cliente para interactuar con la API de la Universidad de Chile
    """
    def __init__(self):
        self.base_url = "https://portafolio-academico.uchile.cl/api"
        self.headers = {
            "Authorization": "Basic ZGlyZWN0b3JpbzphY2FkZW1pY28=",
            "Accept": "*/*",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }


    def get_departamentos(self, unidad_id:int):
        """
        Obtiene la lista de departamentos de una unidad
        """
        try:
            response = requests.get(
                f"{self.base_url}/academicos/lista/departamento",
                params={"unidad": unidad_id},
                headers=self.headers
            )
            
            if response.status_code == 200:
                decoded_data = APIClient()._decode_response(response.text)
                return decoded_data
            else:
                return f"Error en la solicitud: {response.status_code}"
                
        except Exception as e:
            return f"Error: {str(e)}"
    
    def get_academicos_por_departamento(self, departamento_id):
        """
        Obtiene la lista de académicos de un departamento
        """
        try:
            response = requests.get(
                f"{self.base_url}/academicos/lista/academicos",
                params={"departamento": departamento_id},
                headers=self.headers
            )
            
            if response.status_code == 200:
                decoded_data = APIClient()._decode_response(response.text)
                return decoded_data
            else:
                return f"Error en la solicitud: {response.status_code}"
                
        except Exception as e:
            return f"Error: {str(e)}"

# Ejemplo de uso
if __name__ == "__main__":
    client = UChileAPIClient()
    
    print("\nObteniendo lista de departamentos...")
    departamentos = client.get_departamentos(unidad_id=788)
    
    if isinstance(departamentos, dict) and "departamentos" in departamentos:
        print(f"\nSe encontraron {len(departamentos['departamentos'])} departamentos:")
        for depto in departamentos['departamentos']:
            print(f"- {depto['nombre']} (ID: {depto['id']})")
            
        # Obtener académicos de un departamento específico
        print("\nObteniendo académicos del primer departamento...")
        primer_depto = departamentos['departamentos'][0]
        academicos = client.get_academicos_por_departamento(primer_depto['id'])
        print(f"\nAcadémicos de {primer_depto['nombre']}:")
        print(json.dumps(academicos, indent=2, ensure_ascii=False))
    else:
        print("Error obteniendo departamentos:", departamentos)