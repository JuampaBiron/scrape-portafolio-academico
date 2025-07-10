from enum import Enum, auto
import logging
from pathlib import Path
from config import Config
from get_profesors import ScraperAcademicos
from get_publicaciones import PublicacionesScraper
from get_projects import ProyectosScraper
from get_unidades import UnidadesScraper

class ScrapingState(Enum):
    """Estados del proceso de scraping"""
    INIT = auto()
    UNIDADES = auto()
    PROFESORES = auto()
    PUBLICACIONES = auto()
    PROYECTOS = auto()


class PortafolioScraper:
    def __init__(self):
        self.config = Config()
        # Configurar logging primero
        self._setup_logging()
        # Crear logger específico para esta clase
        self.logger = logging.getLogger(self.__class__.__name__)
        # Crear directorios necesarios
        self._init_process()
        # Inicializar scrapers
        self.unidades_scraper = UnidadesScraper()
        self.academicos_scraper = ScraperAcademicos()
        self.publicaciones_scraper = PublicacionesScraper()
        self.project_scraper = ProyectosScraper()

    def _init_process(self):
        """Limpia las carpetas de salida y crea las necesarias"""
        import shutil
        
        self.logger.info("Iniciando limpieza de directorios")
        total_paths = len(self.config.paths)
        
        # Limpiar y crear directorios necesarios
        for idx, (path_name, path) in enumerate(self.config.paths.items(), 1):
            path_obj = Path(path)
            
            # Si el directorio existe, eliminarlo completamente
            if path_obj.exists():
                file_count = len(list(path_obj.rglob('*'))) if path_obj.is_dir() else 0
                shutil.rmtree(path_obj)
                self.logger.info(f"[{idx}/{total_paths}] Directorio '{path_name}' limpiado: {path} ({file_count} archivos eliminados)")
            else:
                self.logger.info(f"[{idx}/{total_paths}] Directorio '{path_name}' no existía: {path}")
            
            # Crear el directorio limpio
            path_obj.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"[{idx}/{total_paths}] Directorio '{path_name}' creado: {path}")
        
        self.logger.info(f"Limpieza completada - {total_paths} directorios procesados")
        return True

    def _setup_logging(self):
        """Configura el logging para toda la aplicación"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - [%(levelname)s] - %(name)s.%(funcName)s:%(lineno)d - %(message)s',
            handlers=[logging.StreamHandler()]
        )

    def _scrape_unidades(self) -> bool:
        """Obtiene la lista de unidades/reparticiones"""
        self.logger.info("Obteniendo reparticiones")
        return self.unidades_scraper.get_unidades()

    def _scrape_profesores(self) -> bool:
        """Obtiene la lista de profesores"""
        self.logger.info("Obteniendo profesores para cada repartición")
        return self.academicos_scraper.run_workflow()

    def _scrape_publicaciones(self) -> bool:
        """Obtiene las publicaciones"""
        self.logger.info("******* Obteniendo publicaciones *******")
        return self.publicaciones_scraper.run_workflow()
    
    def _scrape_proyectos(self) -> bool:
        """Obtiene los proyectos"""
        self.logger.info("******* Obteniendo proyectos *******")
        return self.project_scraper.run_workflow()
    
    def run(self) -> None:
        """Ejecuta el proceso completo de scraping"""
        import time
        start_time = time.time()
        
        self.logger.info("="*60)
        self.logger.info("INICIANDO PROCESO DE SCRAPING DEL PORTAFOLIO ACADÉMICO")
        self.logger.info("="*60)
        
        # Mapeo de estados a funciones
        state_processors = {
            ScrapingState.INIT: self._init_process,
            ScrapingState.UNIDADES: self._scrape_unidades,
            ScrapingState.PROFESORES: self._scrape_profesores,
            ScrapingState.PUBLICACIONES: self._scrape_publicaciones,
            ScrapingState.PROYECTOS: self._scrape_proyectos,
        }

        total_states = len(ScrapingState)
        
        # Ejecutar cada proceso en orden
        for idx, state in enumerate(ScrapingState, 1):
            step_start_time = time.time()
            self.logger.info(f"📋 PASO {idx}/{total_states}: {state.name}")
            self.logger.info("-" * 40)
            
            if state in state_processors:
                try:
                    success = state_processors[state]()
                    step_duration = time.time() - step_start_time
                    
                    if not success:
                        self.logger.error(f"❌ FALLO en {state.name} después de {step_duration:.2f}s")
                        self.logger.error("🛑 Deteniendo proceso por error")
                        return False
                    
                    self.logger.info(f"✅ {state.name} completado en {step_duration:.2f}s")
                    
                except Exception as e:
                    step_duration = time.time() - step_start_time
                    self.logger.error(f"💥 EXCEPCIÓN en {state.name} después de {step_duration:.2f}s: {str(e)}")
                    self.logger.error("🛑 Deteniendo proceso por excepción", exc_info=True)
                    return False
            else:
                self.logger.warning(f"⚠️  No hay procesador definido para {state.name}")
            
            self.logger.info("")  # Línea en blanco para separar pasos
        
        total_duration = time.time() - start_time
        self.logger.info("="*60)
        self.logger.info(f"🎉 PROCESO COMPLETO FINALIZADO EXITOSAMENTE")
        self.logger.info(f"⏱️  Tiempo total: {total_duration:.2f} segundos ({total_duration/60:.1f} minutos)")
        self.logger.info("="*60)
        return True

if __name__ == "__main__":
    import time
    script_start = time.time()
    
    scraper = PortafolioScraper()
    success = scraper.run()
    
    script_duration = time.time() - script_start
    
    if success:
        scraper.logger.info(f"🏆 SCRAPING COMPLETADO CON ÉXITO en {script_duration:.2f}s")
    else:
        scraper.logger.error(f"💀 SCRAPING FALLÓ después de {script_duration:.2f}s")
        exit(1)