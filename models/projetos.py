import os

from dotenv import load_dotenv
from pony.orm import Database, db_session
import pandas as pd


db = Database()

load_dotenv()


@db_session
def carregar_projetos(mail) -> pd.DataFrame:
    portifolio = os.getenv("BOARD_PORTFOLIO")
    sql = f"""SELECT id, projeto, resposaveis, status, data, data_lb,
                evolucao, replace(link,'Projeto - ','') as link, 
                pcr, setor, status_agurpado, 
                'https://lunelli-pmo.monday.com/boards/{portifolio}/pulses/'||id as cometarios,
                diretor_responsavel, equipe
            FROM projeto """
    if mail is not None:
        sql = f"""{sql} WHERE equipe like '%{mail}%';"""
    result = db.select(sql)
    df = pd.DataFrame(
        result,
        columns=[
            "id",
            "Projeto",
            "Responsável",
            "Status",
            "Data Final",
            "Data LB",
            "% Evolução",
            "Link",
            "PCR",
            "Setor",
            "Status Agrupado",
            "Comentários",
            "Diretor Responsável",
            "Equipe",
        ],
    )
    df = df.set_index("id")

    return df


@db_session
def carregar_comentarios(id_projeto) -> pd.DataFrame:
    sql = f"""select c.id, c.autor, c.texto, c.atualizacao 
                from comentario c
                where c.id_projeto ='{id_projeto}'
                order by c.atualizacao desc;"""
    result = db.select(sql)
    df = pd.DataFrame(
        result,
        columns=[
            "id",
            "Autor",
            "Comentário",
            "Data",
        ],
    )
    df = df.set_index("id")
    df["Data"] = pd.to_datetime(df["Data"]).dt.strftime("%d/%m/%Y %H:%M:%S")

    return df


@db_session
def carregar_analistas() -> pd.DataFrame:
    sql = """select
                u.nome,	u.mail
            from
                usuarios u
            where
                u.mail in(
                select distinct analista
                from projeto p, 
                    REGEXP_SPLIT_TO_TABLE(p.equipe, ', ?') as analista);"""
    result = db.select(sql)
    df = pd.DataFrame(
        result,
        columns=[
            "Nome",
            "E-mail",
        ],
    )
    return df


db.bind(
    provider="postgres",
    user=os.getenv("POSTGRESQL_USR"),
    password=os.getenv("POSTGRESQL_PWD"),
    host="sf.lunelli.com.br",
    database=os.getenv("POSTGRESQL_DB"),
)

db.generate_mapping(create_tables=True)
