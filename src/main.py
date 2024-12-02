from enum import Enum, auto
import logging
from pathlib import Path
from config import Config
from get_profesors import AcademicosScraper
from get_publicaciones import PublicacionesScraper

class ScrapingState(Enum):
    """Estados del proceso de scraping"""
    PROFESORES = auto()
    PUBLICACIONES = auto()
    PROFESORES_2 = auto()

class PortafolioScraper:
    def __init__(self, reparticion: int):
        self.config = Config()
        self.reparticion = reparticion
        self.logger = self._setup_logger()
        
        # Inicializar scrapers
        self.academicos_scraper = AcademicosScraper()
        self.publicaciones_scraper = PublicacionesScraper()

    def _setup_logger(self) -> logging.Logger:
        logger = logging.getLogger('portafolio_scraper')
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger

    def _scrape_profesores(self) -> bool:
        """Obtiene la lista de profesores"""
        self.logger.info(f"Obteniendo profesores para repartición {self.reparticion}")
        return self.academicos_scraper.save_academicos(self.reparticion)

    def _scrape_publicaciones(self) -> bool:
        """Obtiene las publicaciones"""
        self.logger.info("Obteniendo publicaciones")
        return self.publicaciones_scraper.build_publicaciones_file()

    def run(self) -> None:
        """Ejecuta el proceso completo de scraping"""
        # Crear directorios necesarios
        for path in self.config.paths.values():
            Path(path).mkdir(exist_ok=True)

        # Mapeo de estados a funciones
        state_processors = {
            ScrapingState.PROFESORES: self._scrape_profesores,
            ScrapingState.PUBLICACIONES: self._scrape_publicaciones,
            ScrapingState.PROFESORES_2: self._scrape_profesores,
        }

        # Ejecutar cada proceso en orden
        for state in ScrapingState:
            self.logger.info(f"Iniciando proceso: {state.name}")
            
            if state in state_processors:
                success = state_processors[state]()
                if not success:
                    self.logger.error(f"Error en {state.name}. Deteniendo proceso.")
                    break
            
            self.logger.info(f"Proceso {state.name} completado")

def main():
    # Configuración inicial
    REPARTICION = 788

    try:
        # Crear y ejecutar scraper
        scraper = PortafolioScraper(reparticion=REPARTICION)
        scraper.run()
        
    except Exception as e:
        logging.error(f"Error en el proceso principal: {str(e)}")
        raise

if __name__ == "__main__":
    main()