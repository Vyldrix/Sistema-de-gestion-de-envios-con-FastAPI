# gestor_de_envios.py
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import create_engine, Column, String, Integer, Text, DateTime
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from sqlalchemy.sql import func
from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic import BaseModel
from datetime import datetime
import uuid

app = FastAPI()

# --- Configuración de la base de datos ---
connection_string = (
    "mssql+pyodbc://@localhost/"
    "gestor_envios?"
    "driver=ODBC+Driver+17+for+SQL+Server&"
    "trusted_connection=yes"
)

engine = create_engine(connection_string)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- Modelo SQLAlchemy (actualizado para coincidir con tu SQL) ---
class Envio(Base):
    __tablename__ = "envios"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    tracking_number = Column(String(50), unique=True, nullable=False)
    destinatario = Column(String(255), nullable=False)
    estado = Column(String(100), nullable=False)
    historial = Column(Text, nullable=False)
    fecha_registro = Column(DateTime, server_default=func.now())

# --- Seguridad JWT ---
SECRET_KEY = "clave_secreta_super_segura_gestor_envios"  # Cambiar en producción
ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# --- Datos de usuarios (reemplazar con DB real en producción) ---
fake_users_db = {
    "admin": {
        "username": "admin",
        "hashed_password": pwd_context.hash("admin123"),
        "role": "administrador"
    }
}

# --- Esquemas Pydantic ---
class User(BaseModel):
    username: str
    role: str

class Token(BaseModel):
    access_token: str
    token_type: str

class EnvioCreate(BaseModel):
    destinatario: str
    estado: str = "Registrado"
    historial: str = "Creado por sistema"

class EnvioResponse(BaseModel):
    tracking_number: str
    destinatario: str
    estado: str
    fecha_registro: datetime

    class Config:
        orm_mode = True

# --- Funciones de ayuda ---
def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def authenticate_user(username: str, password: str):
    user = fake_users_db.get(username)
    if not user or not verify_password(password, user["hashed_password"]):
        return None
    return user

def create_access_token(data: dict):
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

# --- Dependencias ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas"
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = fake_users_db.get(username)
    if user is None:
        raise credentials_exception
    return user

# --- Endpoints ---
@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos"
        )
    access_token = create_access_token(data={"sub": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/envios/", response_model=EnvioResponse)
async def crear_envio(
    envio_data: EnvioCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    tracking_number = str(uuid.uuid4())[:8]
    nuevo_envio = Envio(
        tracking_number=tracking_number,
        destinatario=envio_data.destinatario,
        estado=envio_data.estado,
        historial=f"{envio_data.historial} | Por: {current_user['username']}"
    )
    db.add(nuevo_envio)
    db.commit()
    db.refresh(nuevo_envio)
    return nuevo_envio

@app.get("/envios/{tracking_number}", response_model=EnvioResponse)
async def obtener_envio(
    tracking_number: str,
    db: Session = Depends(get_db)
):
    envio = db.query(Envio).filter(Envio.tracking_number == tracking_number).first()
    if not envio:
        raise HTTPException(status_code=404, detail="Envío no encontrado")
    return envio

@app.get("/envios/", response_model=list[EnvioResponse])
async def listar_envios(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    return db.query(Envio).offset(skip).limit(limit).all()

# Crear tablas al iniciar (solo para desarrollo)
Base.metadata.create_all(bind=engine)