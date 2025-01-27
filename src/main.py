from enum import Enum, auto
import logging
from pathlib import Path
from config import Config
from get_profesors import AcademicosScraper
from get_publicaciones import PublicacionesScraper
from get_projects import ProyectosScraper

class ScrapingState(Enum):
    """Estados del proceso de scraping"""
    PROFESORES = auto()
    PUBLICACIONES = auto()
    PROYECTOS = auto()


class PortafolioScraper:
    def __init__(self, reparticion: int):
        self.config = Config()
        self.reparticion = reparticion
        
        # Inicializar scrapers
        self.academicos_scraper = AcademicosScraper()
        self.publicaciones_scraper = PublicacionesScraper()
        self.project_scraper = ProyectosScraper()

    def _scrape_profesores(self) -> bool:
        """Obtiene la lista de profesores"""
        logging.info(f"Obteniendo profesores para repartición {self.reparticion}")
        return self.academicos_scraper.save_academicos(self.reparticion)

    def _scrape_publicaciones(self) -> bool:
        """Obtiene las publicaciones"""
        logging.info("*******Obteniendo publicaciones*******")
        return self.publicaciones_scraper.build_publicaciones_file()
    
    def _scrape_proyectos(self) -> bool:
        """Obtiene los proyectos"""
        logging.info("*******Obteniendo proyectos*******")
        return self.project_scraper.build_proyectos_file()
    
    def run(self) -> None:
        """Ejecuta el proceso completo de scraping"""
        # Crear directorios necesarios
        for path in self.config.paths.values():
            Path(path).mkdir(exist_ok=True)

        # Mapeo de estados a funciones
        state_processors = {
            ScrapingState.PROFESORES: self._scrape_profesores,
            ScrapingState.PUBLICACIONES: self._scrape_publicaciones,
            ScrapingState.PROYECTOS: self._scrape_proyectos,
        }

        # Ejecutar cada proceso en orden
        for state in ScrapingState:
            logging.info(f"Iniciando proceso: {state.name}")
            
            if state in state_processors:
                success = state_processors[state]()
                if not success:
                    logging.error(f"Error en {state.name}. Deteniendo proceso.")
                    break
            
            logging.info(f"Proceso {state.name} completado")

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