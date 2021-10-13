from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime
from config import engine, session
from sqlalchemy.orm import relationship

from datetime import datetime


Base = declarative_base()
Base.query = session.query_property()


class Obras(Base):
    __tablename__ = 'obras'

    id = Column(Integer, primary_key=True)
    titulo = Column(String(120))
    editora = Column(String(120))
    foto = Column(Text)
    date_create = Column(DateTime, nullable=False, default=datetime.now())
    autores = relationship("Autores", back_populates="obra", cascade="all, delete-orphan")

    def __repr__(self):
        return f'Obras <{self.id}>'

#Metódos para manipulação dos dados!
    def save(self):
        session.add(self)
        session.commit()

    def delete(self):
        session.delete(self)
        session.commit()

    def update(self):
        session.commit()


class Autores(Base):
    __tablename__ = 'autores'

    id = Column(Integer, primary_key=True)
    autor = Column(String(120))
    obra_id = Column(Integer, ForeignKey('obras.id'))
    obra = relationship("Obras", back_populates="autores")

    def __repr__(self):
        return f'Autores <{self.id}>'

    def save(self):
        session.add(self)
        session.commit()

    def delete(self):
        session.delete(self)
        session.commit()

    def update(self):
        session.commit()

#Metédo para criação das tabelas!
def init_db():
    Base.metadata.create_all(bind=engine)


if __name__ == '__main__':
    init_db()
