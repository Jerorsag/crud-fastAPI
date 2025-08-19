import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

# DEBUG: Mostrar todas las variables de entorno
print("=== DEBUG: Variables de entorno disponibles ===")
mysql_vars = {k: v for k, v in os.environ.items() if 'MYSQL' in k or 'DATABASE' in k or 'RAILWAY' in k}
for key, value in mysql_vars.items():
    print(f"{key}: {value}")
print("=" * 50)

# Detectar si estamos en Railway
if os.getenv("RAILWAY_ENVIRONMENT") or os.getenv("MYSQL_URL"):
    print("Detectado entorno Railway")

    # Leer la URL de la base de datos de la variable que creaste
    DATABASE_URL = os.getenv("MYSQL_URL")

    # Validar que la variable existe
    if not DATABASE_URL:
        raise ValueError("Missing MYSQL_URL variable in Railway")

    # Asegurarse de usar el driver pymysql
    if "mysql://" in DATABASE_URL and not "mysql+pymysql://" in DATABASE_URL:
        DATABASE_URL = DATABASE_URL.replace("mysql://", "mysql+pymysql://")
    elif "mysql+pymysql://" in DATABASE_URL:
        pass  # La URL ya tiene el driver correcto
    else:
        # En caso de que la URL no empiece con mysql://
        raise ValueError("MYSQL_URL has an unexpected format.")

    print(f"Railway DB Config: {DATABASE_URL}")

    # Crear el motor de la base de datos
    engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_recycle=300)

else:
    # Desarrollo local
    print("Detectado entorno local")
    MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "password")
    MYSQL_DB = os.getenv("MYSQL_DB", "crud_demo")

    DATABASE_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
    engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_recycle=300)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Dependencia para obtener la sesión de DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()