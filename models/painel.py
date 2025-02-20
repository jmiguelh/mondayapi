import os

from dotenv import load_dotenv
from pony.orm import Database, db_session
import pandas as pd


db = Database()


@db_session
def carregar_projetos() -> pd.DataFrame:
    sql = """SELECT id, projeto, resposaveis, status, data, evolucao, link, pcr, setor, status_agurpado
            FROM projeto;"""
    result = db.select(sql)
    df = pd.DataFrame(
        result,
        columns=[
            "id",
            "Projeto",
            "Resposaveis",
            "Status",
            "Data",
            "% Evolução",
            "Link",
            "PCR",
            "Setor",
            "Status Agrupado",
        ],
    )
    df = df.set_index("id")
    return df


load_dotenv()

db.bind(
    provider="postgres",
    user=os.getenv("POSTGRESQL_USR"),
    password=os.getenv("POSTGRESQL_PWD"),
    host="sf.lunelli.com.br",
    database=os.getenv("POSTGRESQL_DB"),
)
# db.bind(provider="sqlite", filename="../data/db.sqlite", create_db=True)

db.generate_mapping(create_tables=True)
