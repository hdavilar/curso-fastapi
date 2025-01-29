import os
from sqlalchemy import create_engine
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

#Nombre de la base de datos
sqliteName = "movies.sqlite"

#Obtener la ruta donde se guardará la bbdd
base_dir = os.path.dirname(os.path.realpath(__file__))

databaseUrl = f"sqlite:///{os.path.join(base_dir, sqliteName)}"

engine = create_engine(databaseUrl, echo=True)

Session = sessionmaker(bind=engine)

Base = declarative_base()

#Para ver la consexión de la BBDD, instalamos la extensión de VisualStudio Code: SQLite Viewer
