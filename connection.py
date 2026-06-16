from sqlalchemy import create_engine,String
from sqlalchemy.orm import DeclarativeBase,Mapped, mapped_column

DATABASE_URL="sqlite:///./sql_app.db"
engine=create_engine(DATABASE_URL,echo=True)

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__="users"

    id:Mapped[int]=mapped_column(primary_key=True)
    name:Mapped[str]=mapped_column(String(30))
    email:Mapped[str]=mapped_column(String(30), unique=True)

    def __repr__(self)->str:

        return f"User (id={self.id}),name='{self.name}',email='{self.email}'"

print("creating the tables..")
Base.metadata.create_all(engine)
print("all tables are created")

        