from fastapi import Path, Query, Request, HTTPException, Depends, APIRouter
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field
from typing import Optional
from user_jwt import validateToken
from bd.database import Base, Session, engine
from modelos.movie import Movie as ModelMovie

routerMovie = APIRouter()

Base.metadata.create_all(bind=engine)
db = Session()

#Clase para la validación
class Movie(BaseModel):
    id: Optional[int] = None
    title: str = Field(default="Titulo de la pelicula", min_length=5, max_length=60)
    overview: str = Field(default="Descripción de la pelicula", min_length=15, max_length=60)
    year: int = Field(default=2025)
    rating: float = Field(ge=1, le=10) #Mayor o igual que 0 y menor o igual que 10
    category: str = Field(default="Categoria", min_length=3, max_length=15)

    def to_dict(self):
        return{
            "id": self.id,
            "title": self.title,
            "overview": self.overview,
            "year": self.year,
            "rating": self.rating,
            "category": self.category
        }

#Clase para validar el token
class BearerJWT(HTTPBearer):
    async def __call__(self, request: Request):
        auth = await super().__call__(request)
        data = validateToken(auth.credentials)
        if data["email"] != "email": #Si no xoincide el email
            raise HTTPException(status_code=403, detail="Credenciales incorrectas")


#Ruta que devuelve un array de peliculas
@routerMovie.get("/movies", tags=["Peliculas"], dependencies=[Depends(BearerJWT())])
def get_pelis():
    #db = Session()
    data = db.query(ModelMovie).all()
    return jsonable_encoder(data) #Pasa el objeto a JSON

#Ruta que a traves de un parametro id devuelve una pelicula con el id establecido si se encuentra, en su defecto devuelve un array vacío
#Validamos los parámetros con el Path
@routerMovie.get("/movies/{id}", tags=["Peliculas"])
def get_peli(id: int = Path(ge=1, le=100)):
    data = db.query(ModelMovie).filter(ModelMovie.id == id).first()
    if not data:
        return JSONResponse(status_code=404, content={"mensaje": "Recurso no encontrado"})    
    return jsonable_encoder(data)

#Ruta que a traves de query params devuelve la categoria introducida
#Validamos los query con el Query
@routerMovie.get("/movies/", tags=["Peliculas"])
def get_peli_por_categoria(category: str = Query(min_length=3, max_length=15)):
    data = db.query(ModelMovie).filter(ModelMovie.category == category).all()
    if not data:
        return JSONResponse(status_code=404, content={"mensaje": "Recurso no encontrado"}) 
    return jsonable_encoder(data)

#Crear una pelicula
#Se utiliza la clase para reducir el código
@routerMovie.post("/movies", tags=["Peliculas"], status_code=201)
def create_movie(movie: Movie):
    #db = Session()
    newMovie = ModelMovie(**movie.to_dict())
    db.add(newMovie)
    db.commit()
    return JSONResponse(status_code=201, content={
        "mensaje": "Se ha creado una nueva película",
        #"pelicula": dict(movie)
        "pelicula": movie.to_dict()
        }
    )

#Actualizar una pelicula
@routerMovie.put("/movies/{id}", tags=["Peliculas"], status_code=200)
def update_movie(id: int, movie: Movie):
    data = db.query(ModelMovie).filter(ModelMovie.id == id).first()
    if not data:
        return JSONResponse(status_code=404, content={"mensaje": "Recurso no encontrado"})
    
    data.title = movie.title
    data.overview = movie.overview
    data.year = movie.year
    data.rating = movie.rating
    data.category = movie.category
    db.commit()

    return JSONResponse(content={"mensaje": "Se ha actualizado la película"})

@routerMovie.delete("/movies/{id}", tags=["Peliculas"], status_code=200)
def delete_movie(id: int):
    data = db.query(ModelMovie).filter(ModelMovie.id == id).first()
    if not data:
        return JSONResponse(status_code=404, content={"mensaje": "Recurso no encontrado"})

    db.delete(data)
    db.commit()
    
    return JSONResponse(content={
        "mensaje": "Se ha eliminado la película",
        "dato": jsonable_encoder(data)
        }
    )