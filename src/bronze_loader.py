import json
import hashlib
import os
import sys
import logging
import psycopg2
from psycopg2 import sql, Error  # Para manejo de errores
from pathlib import Path
from contextlib import contextmanager
from config import Config

class BronzeLoader:
    def __init__(self):
        self.config = Config()
        self.paths = self.config.paths
        self.logger = self._setup_logger()
        self.unidades_folder = Path(self.paths['unidades_raw_data'])
        self.profesores_folder = Path(self.paths['academics_raw_data'])
        self.publicaciones_folder = Path(self.paths['publications_raw_data'])
        self.proyectos_folder = Path(self.paths['projects_raw_data'])
        self.db_host = os.getenv('DB_HOST')
        self.db_name = os.getenv('DB_NAME')
        self.db_user = os.getenv('DB_USER')
        self.db_password = os.getenv('DB_PASSWORD')
    
    def _setup_logger(self) -> logging.Logger:
        """Retorna el logger configurado"""
        return logging.getLogger('bronze_loader')
    
    @contextmanager
    def get_connection(self):
        """Context manager para conexiones de base de datos"""
        conn = None
        try:
            self.logger.info("Estableciendo conexión a la base de datos")
            conn_string = f"host={self.db_host} dbname={self.db_name} user={self.db_user} password={self.db_password}"
            conn = psycopg2.connect(conn_string)
            self.logger.info("Conexión exitosa a la base de datos")
            yield conn
        except Error as e:
            self.logger.error(f"Error al conectar a la base de datos: {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()
                self.logger.info("Conexión cerrada")
        
    def test_table_access(self, conn, table_name):
        """Testea que la tabla existe y tenemos permisos"""
        self.logger.info(f"Probando acceso a la tabla bronze.{table_name}")
        try:
            with conn.cursor() as cursor:
                # Test básico: verificar que la tabla existe y podemos leer
                cursor.execute(f"SELECT COUNT(*) FROM bronze.{table_name} LIMIT 1;")
                cursor.fetchone()
                self.logger.info(f"Acceso a tabla bronze.{table_name} verificado")
                return True
        except Exception as e:
            self.logger.error(f"Error accediendo tabla bronze.{table_name}: {e}")
            return False    
        
    def load_unidades(self):
        """Carga unidades.json a bronze.unidades_raw"""
        self.logger.info("Cargando unidades desde JSON a la base de datos")
        
        with self.get_connection() as conn:
            if not self.test_table_access(conn, 'unidades_raw'):
                return False
            
            source_system = 'portafolio_academico'
            file_name = os.path.join(self.unidades_folder, "unidades.json")
            if not os.path.exists(file_name):
                self.logger.error(f"Archivo no encontrado: {file_name}")
                return False
            
            raw_json = json.load(open(file_name, 'r', encoding='utf-8'))
            # Calcular hash del JSON para detectar duplicados
            record_hash = hashlib.sha256(json.dumps(raw_json, sort_keys=True).encode('utf-8')).hexdigest()
            
            try:
                with conn.cursor() as cursor:
                    # Insertar datos en la tabla bronze.unidades_raw
                    insert_query = """
                    INSERT INTO bronze.unidades_raw (source_system, raw_json, file_name, record_hash)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (record_hash) DO NOTHING;
                    """
                    cursor.execute(insert_query, (source_system, json.dumps(raw_json), file_name, record_hash))
                conn.commit()
                self.logger.info(f"Datos de unidades cargados exitosamente desde {file_name}")
                return True
            except Exception as e:
                self.logger.error(f"Error al cargar datos de unidades: {str(e)}")
                conn.rollback()
                return False
    
    def load_academics(self):
        """Carga académicos a bronze.academics_raw"""
        self.logger.info("Cargando académicos desde JSON a la base de datos")
        
        with self.get_connection() as conn:
            if not self.test_table_access(conn, 'academics_raw'):
                return False
            
            for academic_file in self.profesores_folder.glob("*.json"):
                if not academic_file.is_file():
                    self.logger.error(f"Archivo no encontrado: {academic_file}")
                    continue
                unidad_id = academic_file.stem.split('_')[0]
                if not unidad_id.isdigit():
                    self.logger.error(f"ID de unidad inválido en el nombre del archivo: {academic_file}")
                    continue
                unidad_id = int(unidad_id)
                with open(academic_file, 'r', encoding='utf-8') as f:
                    raw_json = json.load(f)
                # Calcular hash del JSON para detectar duplicados
                record_hash = hashlib.sha256(json.dumps(raw_json, sort_keys=True).encode('utf-8')).hexdigest()
                source_system = 'portafolio_academico'
                file_name = str(academic_file)

                try:
                    with conn.cursor() as cursor:
                        # Insertar datos en la tabla bronze.academics_raw
                        insert_query = """
                        INSERT INTO bronze.academics_raw (unidad_id, source_system, raw_json, file_name, record_hash)
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (record_hash) DO NOTHING;
                        """
                        cursor.execute(insert_query, (unidad_id, source_system, json.dumps(raw_json), file_name, record_hash))
                    conn.commit()
                    self.logger.info(f"Datos de académicos cargados exitosamente desde {file_name}")
                except Exception as e:
                    self.logger.error(f"Error al cargar datos de académicos: {str(e)}")
                    conn.rollback()
                    return False
            return True
    
    def load_publications(self):
        """Carga publicaciones a bronze.publications_raw"""
        self.logger.info("Cargando publicaciones desde JSON a la base de datos")
        
        with self.get_connection() as conn:
            if not self.test_table_access(conn, 'publications_raw'):
                return False
            
            for publication_file in self.publicaciones_folder.glob("*.json"):
                if not publication_file.is_file():
                    self.logger.error(f"Archivo no encontrado: {publication_file}")
                    continue
                #obtener el ID de la unidad desde el nombre del archivo raw_data\academics\420_academicos_raw.json
                academic_id = publication_file.stem.split('_')[0]
                if not academic_id.isdigit():
                    self.logger.error(f"ID de unidad inválido en el nombre del archivo: {publication_file}")
                    continue
                #transformar unidad_id a entero
                academic_id = int(academic_id)
                with open(publication_file, 'r', encoding='utf-8') as f:
                    raw_json = json.load(f)
                # Calcular hash del JSON para detectar duplicados
                record_hash = hashlib.sha256(json.dumps(raw_json, sort_keys=True).encode('utf-8')).hexdigest()
                source_system = 'portafolio_academico'
                file_name = str(publication_file)
                int_total_publications = raw_json.get('total_resultado', 0)

                try:
                    with conn.cursor() as cursor:
                        # Insertar datos en la tabla bronze.publications_raw
                        insert_query = """
                        INSERT INTO bronze.publications_raw (academic_id, source_system, total_publications, raw_json, file_name, record_hash)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON CONFLICT (record_hash) DO NOTHING;
                        """
                        cursor.execute(insert_query, (academic_id, source_system, int_total_publications, json.dumps(raw_json), file_name, record_hash))
                    conn.commit()
                    self.logger.info(f"Datos de publicaciones cargados exitosamente desde {file_name}")
                except Exception as e:
                    self.logger.error(f"Error al cargar datos de publicaciones: {str(e)}")
                    conn.rollback()
                    return False
            return True
    
    def load_projects(self):
        """Carga proyectos a bronze.projects_raw"""
        self.logger.info("Iniciando carga de proyectos")
        
        with self.get_connection() as conn:
            # Verificar archivos antes de procesar
            files = list(self.proyectos_folder.glob("*.json"))
            if not files:
                self.logger.warning(f"No se encontraron archivos JSON en: {self.proyectos_folder}")
                return False
            
            if not self.test_table_access(conn, 'projects_raw'):
                return False
            
            self.logger.info(f"Procesando {len(files)} archivos de proyectos")
            processed_count = 0
            
            try:
                for i, project_file in enumerate(files, 1):
                    try:
                        # Extraer academic_id
                        academic_id = project_file.stem.split('_')[0]
                        if not academic_id.isdigit():
                            self.logger.error(f"ID inválido: {project_file.name}")
                            continue
                        
                        academic_id = int(academic_id)
                        
                        with open(project_file, 'r', encoding='utf-8') as f:
                            raw_json = json.load(f)
                        
                        # Preparar datos
                        record_hash = hashlib.sha256(json.dumps(raw_json, sort_keys=True).encode('utf-8')).hexdigest()
                        source_system = 'portafolio_academico'
                        total_projects = raw_json.get('total_resultado', 0)
                        
                        # Insertar en BD
                        with conn.cursor() as cursor:
                            insert_query = """
                            INSERT INTO bronze.projects_raw (academic_id, source_system, total_projects, raw_json, file_name, record_hash)
                            VALUES (%s, %s, %s, %s, %s, %s)
                            ON CONFLICT (record_hash) DO NOTHING;
                            """
                            cursor.execute(insert_query, (academic_id, source_system, total_projects, json.dumps(raw_json), str(project_file), record_hash))
                        
                        processed_count += 1
                        self.logger.info(f"Procesado [{i}/{len(files)}]: {project_file.name} - Académico {academic_id}")
                        
                    except Exception as e:
                        self.logger.error(f"Error procesando {project_file.name}: {e}")
                        # Continúa con el siguiente archivo sin romper todo
                        continue
                
                # Commit final de todos los inserts
                conn.commit()
                self.logger.info(f"Carga completada: {processed_count} archivos procesados exitosamente")
                return True
            
            except Exception as e:
                self.logger.error(f"Error crítico en carga de proyectos: {e}")
                conn.rollback()
                return False

    def run_workflow(self):
        """Ejecuta el flujo de trabajo de carga de datos"""
        try:
            self.logger.info("Iniciando flujo de trabajo de carga de datos")
            # Aquí puedes llamar a los métodos de carga con los archivos correspondientes
            # Por ejemplo:
            self.load_unidades()
            self.load_academics()
            self.load_publications()
            self.load_projects()
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
    loader = BronzeLoader()
    loader.run_workflow()