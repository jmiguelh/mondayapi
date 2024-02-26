from pony.orm import *
import pandas as pd


db = Database()


@db_session
def carregar_projetos() -> pd.DataFrame:
    sql = """SELECT id, projeto, resposaveis, status, data, evolucao, link, pcr, setor
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
            "Evolução",
            "Link",
            "PCR",
            "Setor",
        ],
    )
    df = df.set_index("id")
    return df


db.bind(provider="sqlite", filename="../data/db.sqlite", create_db=True)

db.generate_mapping(create_tables=True)
