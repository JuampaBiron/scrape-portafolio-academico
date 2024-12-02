
import requests
import base64
import json
import urllib.parse
import csv
from typing import Dict, Any


def get_tesis(id_persona: int):
    """Obtiene las tesis de un académico"""
    url = "https://portafolio-academico.uchile.cl/api/academicos/tesis"
    
    headers = {
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Authorization': 'Basic ZGlyZWN0b3JpbzphY2FkZW1pY28=',
        'Connection': 'keep-alive',
        'Referer': f'https://portafolio-academico.uchile.cl/perfil/{id_persona}',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    params = {
        'id_persona': id_persona,
        'id_estado_verif': 3,
        'limite': 100,
        'pagina': 1
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            result = decode_response(response.text)
            
            # Guardar datos crudos
            with open(f'tesis_{id_persona}_raw.json', 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"\nDatos completos guardados en 'tesis_{id_persona}_raw.json'")
            
            # Procesar las tesis
            if 'academicos' in result and len(result['academicos']) > 0:
                tesis_list = result['academicos'][0].get('tesis', [])
                total = result.get('total_resultado', 0)
                
                if tesis_list:
                    # Guardar en CSV
                    with open(f'tesis_{id_persona}.csv', 'w', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        
                        # Headers
                        writer.writerow([
                            'ID Académico',
                            'Autores',
                            'Título',
                            'Año',
                            'Facultad',
                            'Profesor Guía',
                            'Comisión',
                            'URL',
                            'Fuente'
                        ])
                        
                        # Data
                        for tesis in tesis_list:
                            writer.writerow([
                                id_persona,
                                tesis.get('autores', ''),
                                tesis.get('titulo', ''),
                                tesis.get('anio', ''),
                                tesis.get('facultad', ''),
                                tesis.get('profesor_guia', ''),
                                tesis.get('comision', ''),
                                tesis.get('url', ''),
                                tesis.get('fuente', '')
                            ])
                    
                    print(f"\nSe encontraron {total} tesis")
                    print(f"Datos guardados en 'tesis_{id_persona}.csv'")
                    
                    # Mostrar resumen
                    print("\nResumen de tesis:")
                    print("-" * 80)
                    for tesis in tesis_list:
                        print(f"Título: {tesis.get('titulo', 'No especificado')}")
                        print(f"Autor(es): {tesis.get('autores', 'No especificado')}")
                        print(f"Año: {tesis.get('anio', 'No especificado')}")
                        print(f"Facultad: {tesis.get('facultad', 'No especificado')}")
                        print(f"Profesor Guía: {tesis.get('profesor_guia', 'No especificado')}")
                        if tesis.get('url'):
                            print(f"URL: {tesis.get('url')}")
                        print("-" * 80)
                else:
                    print("\nNo se encontraron tesis para este académico")
            
            return result
            
        else:
            print(f"Error en la petición: {response.status_code}")
            return {}
            
    except Exception as e:
        print(f"Error obteniendo tesis: {e}")
        return {}

if __name__ == "__main__":
    # ID del académico Andrés Abeliuk
    ID_ACADEMICO = 328029
    print(f"Obteniendo tesis del académico {ID_ACADEMICO}...")
    get_tesis(ID_ACADEMICO)
