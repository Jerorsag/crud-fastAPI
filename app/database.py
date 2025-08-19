import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

# DEBUG: Mostrar todas las variables de entorno que empiecen con MYSQL
print("=== DEBUG: Variables de entorno disponibles ===")
mysql_vars = {k: v for k, v in os.environ.items() if 'MYSQL' in k or 'DATABASE' in k or 'RAILWAY' in k}
for key, value in mysql_vars.items():
    print(f"{key}: {value}")
print("=" * 50)

# Detectar si estamos en Railway o local
if os.getenv("RAILWAY_ENVIRONMENT") or os.getenv("MYSQLHOST"):
    # Producción en Railway - MySQL automático
    print("Detectado entorno Railway")

    # Railway usa estos nombres exactos
    MYSQL_HOST = os.getenv("MYSQLHOST")
    MYSQL_PORT = os.getenv("MYSQLPORT") or "3306"  # Fallback si es None
    MYSQL_USER = os.getenv("MYSQLUSER")
    MYSQL_PASSWORD = os.getenv("MYSQLPASSWORD")
    MYSQL_DB = os.getenv("MYSQLDATABASE")

    print(f"MYSQL_HOST: {MYSQL_HOST}")
    print(f"MYSQL_PORT: {MYSQL_PORT}")
    print(f"MYSQL_USER: {MYSQL_USER}")
    print(f"MYSQL_PASSWORD: {'***' if MYSQL_PASSWORD else None}")
    print(f"MYSQL_DB: {MYSQL_DB}")

    # Validar que todas las variables existen
    if not all([MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB]):
        print("ERROR: Faltan variables de MySQL en Railway")
        print("¿Agregaste el servicio MySQL en Railway?")
        raise ValueError(f"Missing MySQL variables: HOST={MYSQL_HOST}, USER={MYSQL_USER}, DB={MYSQL_DB}")

    # Asegurarse que el puerto es un número válido
    try:
        MYSQL_PORT = int(MYSQL_PORT)
    except (ValueError, TypeError):
        MYSQL_PORT = 3306

    print(f"Railway DB Config: {MYSQL_USER}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}")

    DATABASE_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
    engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_recycle=300)
else:
    # Desarrollo local - MySQL
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