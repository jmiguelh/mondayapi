import os

from dotenv import load_dotenv
from pony.orm import Database, db_session
import pandas as pd

db = Database()

load_dotenv()


@db_session
def carregar_projetos() -> pd.DataFrame:
    portifolio = os.getenv("BOARD_PORTFOLIO")
    sql = f"""SELECT id, projeto, resposaveis, status, data,
                evolucao, replace(link,'Projeto - ','') as link, 
                pcr, setor, status_agurpado, 
                'https://lunelli-pmo.monday.com/boards/{portifolio}/pulses/'||id as cometarios
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
            "Comentários",
        ],
    )
    df = df.set_index("id")
    return df


@db_session
def carregar_robos() -> pd.DataFrame:
    sql = """SELECT id, robo, resposaveis, status_agurpado, status, fte, 
                evolucao, setor, ano
            FROM public.robo;"""
    result = db.select(sql)
    df = pd.DataFrame(
        result,
        columns=[
            "id",
            "Robô",
            "Resposaveis",
            "Status Agrupado",
            "Status",
            "FTE/Horas Mês",
            "% Evolução",
            "Setor",
            "Ano",
        ],
    )
    df = df.set_index("id")
    return df


db.bind(
    provider="postgres",
    user=os.getenv("POSTGRESQL_USR"),
    password=os.getenv("POSTGRESQL_PWD"),
    host="sf.lunelli.com.br",
    database=os.getenv("POSTGRESQL_DB"),
)
# db.bind(provider="sqlite", filename="../data/db.sqlite", create_db=True)

db.generate_mapping(create_tables=True)
