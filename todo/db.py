from todo import settings
from sqlmodel import create_engine, SQLModel, Session

conn_str = str(settings.DATABASE_URL_POSTGRES).replace(
    "postgresql", "postgresql+psycopg"
)
engine = create_engine(conn_str,  pool_recycle=300)


def create_db_table()->None:
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session