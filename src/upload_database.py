import pandas as pd
import json
from sqlalchemy import create_engine, text
from pathlib import Path
from datetime import datetime
import logging
from typing import Optional

class DataLoader:
    def __init__(self):
        database_url = "postgresql://jpbiron:16DEmarzo@192.168.1.110:5432/postgres"
        self.engine = create_engine(database_url)
        self.setup_logging()
        
    def setup_logging(self):
        """Configura el logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def cargar_academicos(self, json_path: Path) -> bool:
        """Carga académicos desde JSON a la base de datos"""
        try:
            with open(json_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                academicos = data['academicos']
            
            with self.engine.connect() as conn:
                # Limpiar tabla
                conn.execute(text("DELETE FROM academicos"))
                
                for academico in academicos:
                    valores = {
                        'id_persona': academico['id_persona'],
                        'nombres': academico['nombres'],
                        'paterno': academico['paterno'],
                        'materno': academico['materno'],
                        'nombre_completo': academico['nombre_completo'],
                        'url_foto': academico.get('url_foto', ''),
                        'foto_base_64': academico.get('foto_base_64', ''),
                        'correo': academico.get('correo', ''),
                        'reparticion': academico.get('reparticion', '')
                    }
                    
                    query = text("""
                        INSERT INTO academicos 
                        (id_persona, nombres, paterno, materno, nombre_completo, 
                         url_foto, foto_base_64, correo, reparticion)
                        VALUES 
                        (:id_persona, :nombres, :paterno, :materno, :nombre_completo,
                         :url_foto, :foto_base_64, :correo, :reparticion)
                    """)
                    
                    conn.execute(query, valores)
                conn.commit()
            
            self.logger.info(f"Cargados {len(academicos)} académicos")
            return True
        
        except Exception as e:
            self.logger.error(f"Error cargando académicos: {str(e)}")
            return False
    
    def cargar_publicaciones(self, csv_path: Path) -> bool:
        """Carga publicaciones desde CSV a la base de datos"""
        try:
            df = pd.read_csv(csv_path)
            df = df.rename(columns={
                'ID Academico': 'id_academico',
                'Nombre Academico': 'nombre_academico',
                'Título': 'titulo',
                'Año': 'anio',
                'Autores': 'autores',
                'Revista': 'revista',
                'DOI': 'doi',
                'Link': 'url'
            })
            
            df = df.fillna('')
            
            with self.engine.connect() as conn:
                conn.execute(text("DELETE FROM publicaciones"))
                
                for _, row in df.iterrows():
                    valores = {
                        'id_academico': row['id_academico'],
                        'nombre_academico': row['nombre_academico'],
                        'titulo': row['titulo'],
                        'anio': row['anio'],
                        'revista': row['revista'],
                        'autores': row['autores'],
                        'doi': row['doi'],
                        'url': row['url']
                    }
                    
                    query = text("""
                        INSERT INTO publicaciones 
                        (id_academico, nombre_academico, titulo, anio, revista, 
                        autores, doi, url)
                        VALUES 
                        (:id_academico, :nombre_academico, :titulo, :anio, :revista,
                        :autores, :doi, :url)
                    """)
                    
                    conn.execute(query, valores)
                conn.commit()
            
            self.logger.info(f"Cargadas {len(df)} publicaciones")
            return True
        
        except Exception as e:
            self.logger.error(f"Error cargando publicaciones: {str(e)}")
            return False
    def cargar_proyectos(self, csv_path: Path) -> bool:
        """Carga proyectos desde CSV a la base de datos"""
        try:
            df = pd.read_csv(csv_path)
            df = df.rename(columns={
                'ID Académico': 'id_academico',
                'Nombre Academico': 'nombre_academico',
                'Código': 'codigo',
                'Título': 'titulo',
                'Fecha Inicio': 'fecha_inicio',
                'Fecha Término': 'fecha_termino',
                'Investigadores': 'investigadores',
                'Institución': 'institucion',
                'Programa': 'programa',
                'Fuente': 'fuente'
            })
            
            df['fecha_inicio'] = pd.to_datetime(df['fecha_inicio'])
            df['fecha_termino'] = pd.to_datetime(df['fecha_termino'])
            
            with self.engine.connect() as conn:
                conn.execute(text("DELETE FROM proyectos"))
                
                for _, row in df.iterrows():
                    query = text("""
                        INSERT INTO proyectos 
                        (id_academico, nombre_academico, codigo, titulo, 
                         fecha_inicio, fecha_termino, investigadores, institucion,
                         programa, fuente)
                        VALUES 
                        (:id_academico, :nombre_academico, :codigo, :titulo,
                         :fecha_inicio, :fecha_termino, :investigadores, :institucion,
                         :programa, :fuente)
                    """)
                    
                    valores = row.to_dict()
                    valores['fecha_inicio'] = valores['fecha_inicio'].strftime('%Y-%m-%d')
                    valores['fecha_termino'] = valores['fecha_termino'].strftime('%Y-%m-%d')
                    
                    conn.execute(query, valores)
                conn.commit()
            
            self.logger.info(f"Cargados {len(df)} proyectos")
            return True
            
        except Exception as e:
            self.logger.error(f"Error cargando proyectos: {str(e)}")
            return False

    def upload_data(self):
        """Carga todos los datos a la base de datos"""
        # Configuración
        DATABASE_URL = "postgresql://jpbiron:16DEmarzo@192.168.1.110:5432/postgres"
        
        # Paths
        data_dir = Path('process_data')
        academicos_path = data_dir / 'academicos_raw.json'
        publicaciones_path = data_dir / 'todas_las_publicaciones.csv'
        proyectos_path = data_dir / 'todos_los_proyectos.csv'
        
        # Carga de datos
        print("\nIniciando carga de datos...")
        
        if self.cargar_academicos(academicos_path):
            print("Académicos cargados exitosamente")
        
        if self.cargar_publicaciones(publicaciones_path):
            print("Publicaciones cargadas exitosamente")
        
        if self.cargar_proyectos(proyectos_path):
            print("Proyectos cargados exitosamente")
        
        print("\nProceso completado!")

if __name__ == "__main__":
    DataLoader().upload_data()