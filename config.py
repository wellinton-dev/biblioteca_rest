from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

#Cria uma instância do banco de dados.
engine = create_engine("sqlite:///biblioteca.db")

#Cria um sessão com o banco o banco de dados.
session = scoped_session(sessionmaker(bind=engine))



