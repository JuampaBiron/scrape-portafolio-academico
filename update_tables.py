from sqlalchemy import create_engine, text

def verificar_estructura():
    database_url = "postgresql://jpbiron:16DEmarzo@192.168.1.110:5432/postgres"
    engine = create_engine(database_url)
    
    try:
        with engine.connect() as conn:
            # Consulta para verificar la estructura de la tabla
            query = text("""
                SELECT column_name, data_type, character_maximum_length
                FROM information_schema.columns
                WHERE table_name = 'publicaciones';
            """)
            
            result = conn.execute(query)
            
            print("\nEstructura actual de la tabla publicaciones:")
            for row in result:
                print(f"Columna: {row[0]}")
                print(f"Tipo: {row[1]}")
                print(f"Longitud máxima: {row[2]}")
                print("-" * 30)
            
    except Exception as e:
        print(f"Error verificando la estructura: {str(e)}")
    
    finally:
        engine.dispose()

if __name__ == "__main__":
    verificar_estructura()