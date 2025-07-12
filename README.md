# Portafolio Académico Scraper

Scraper robusto y modular para el Portafolio Académico de la Universidad de Chile, diseñado para recopilar información completa sobre académicos, publicaciones, proyectos de investigación y tesis dirigidas.

## Características

- **Extracción completa**: Académicos, publicaciones, proyectos y tesis
- **Arquitectura modular**: Scrapers independientes y reutilizables
- **Sistema robusto**: Reintentos automáticos y manejo de errores
- **Configuración flexible**: Archivo YAML centralizado
- **Múltiples formatos**: Salida en JSON y CSV
- **Rate limiting**: Respeta los límites del servidor
- **Logging detallado**: Seguimiento completo del proceso

## Arquitectura

### Desafío técnico resuelto
Un reto significativo fue la **decodificación de respuestas del servidor**, que venían en un formato codificado específico. Se desarrolló el módulo `api_client.py` que maneja automáticamente esta decodificación.

### Estructura del proyecto
```
├── main.py                 # Orquestador principal
├── src/
│   ├── config.py          # Gestión de configuración
│   ├── config.yaml        # Parámetros del sistema
│   ├── api_client.py      # Cliente API con decodificación
│   ├── get_unidades.py    # Scraper de unidades académicas
│   ├── get_profesors.py   # Scraper de académicos
│   ├── get_publicaciones.py # Scraper de publicaciones
│   ├── get_projects.py    # Scraper de proyectos
│   └── get_tesis.py       # Scraper de tesis
├── raw_data/              # Datos en bruto (JSON)
├── process_data/          # Datos procesados (CSV)
└── output/                # Resultados finales
```

## Prerequisitos

- Python 3.7+
- Conexión a internet estable
- Acceso a la API del Portafolio Académico UCH

## Instalación

1. **Clonar el repositorio:**
   ```bash
   git clone <repository-url>
   cd portafolio-academico-scraper
   ```

2. **Crear entorno virtual:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # o
   venv\Scripts\activate     # Windows
   ```

3. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

## Uso

### Proceso completo automático
```bash
python main.py
```

### Ejecución modular

1. **Obtener unidades académicas disponibles:**
   ```bash
   python src/get_unidades.py
   ```

2. **Extraer académicos por unidad:**
   ```bash
   python src/get_profesors.py
   ```

3. **Recopilar publicaciones:**
   ```bash
   python src/get_publicaciones.py
   ```

4. **Obtener proyectos de investigación:**
   ```bash
   python src/get_projects.py
   ```

5. **Extraer tesis dirigidas:**
   ```bash
   python src/get_tesis.py
   ```

## Unidades Académicas Disponibles

| ID | Unidad Académica |
|----|------------------|
| 328 | Facultad de Arquitectura y Urbanismo |
| 420 | Facultad de Artes |
| 526 | Facultad de Ciencias |
| 560 | Facultad de Ciencias Agronómicas |
| 788 | Facultad de Ciencias Físicas y Matemáticas |
| 915 | Facultad de Ciencias Químicas y Farmacéuticas |
| 943 | Facultad de Ciencias Sociales |
| 1023 | Facultad de Ciencias Veterinarias y Pecuarias |
| 1108 | Facultad de Derecho |
| 649 | Facultad de Economía y Negocios |
| 1212 | Facultad de Filosofía y Humanidades |
| 1261 | Facultad de Medicina |
| 1560 | Facultad de Odontología |
| ... | *[Ver get_unidades.py para lista completa]* |

## Configuración

El archivo `src/config.yaml` permite personalizar:

```yaml
scraping:
  delay: 0.2          # Delay entre requests (segundos)
  max_retries: 2      # Intentos máximos por request
  timeout: 30         # Timeout de requests
  batch_size: 10      # Tamaño de lote para procesamiento

pagination:
  default_limit: 200  # Límite por defecto
  max_limit: 500      # Límite máximo
```

## Estructura de Datos de Salida

### Archivos JSON (raw_data/)
- `unidades.json`: Lista de unidades académicas
- `{id_unidad}_academicos_raw.json`: Académicos por unidad
- `{id_persona}_publications.json`: Publicaciones por académico
- `{id_persona}_projects.json`: Proyectos por académico

### Archivos CSV (process_data/)
- `todas_las_publicaciones.csv`: Consolidado de publicaciones
- `todos_los_proyectos.csv`: Consolidado de proyectos
- `todas_las_tesis.csv`: Consolidado de tesis dirigidas (coming soon)

## Personalización

### Filtrar unidades específicas
Edita `src/config.yaml` o modifica directamente `unidades.json` para procesar solo las unidades de interés.

### Parámetros de búsqueda
Los scrapers incluyen parámetros configurables:
- **Proyectos**: Filtro por año desde 2015, resolución específica
- **Tesis**: Solo tesis verificadas (id_estado_verif: 3) (coming soon)
- **Publicaciones**: Sin filtros adicionales por defecto

## Monitoreo y Logs

El sistema proporciona logging detallado:
- Progreso por unidad académica
- Contadores de registros procesados
- Alertas de errores y reintentos
- Resumen final de ejecución

## Contribuir

1. Fork del proyecto
2. Crear rama feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## Consideraciones Éticas

Este scraper está diseñado para:
- Respetar rate limits del servidor
- Usar delays apropiados entre requests
- Manejar errores sin sobrecargar el sistema
- Cumplir con términos de uso del Portafolio Académico

## Licencia

MIT License - ver archivo `LICENSE` para detalles.
