import os
from datetime import datetime

from dotenv import load_dotenv
from pony.orm import Database, Optional, PrimaryKey, Required, db_session


db = Database()


class Projeto(db.Entity):
    _table_ = "projeto"
    id = PrimaryKey(str, 15)
    projeto = Required(str, 250)
    resposaveis = Optional(str, 255)
    status = Optional(str, 50)
    data = Optional(datetime)
    evolucao = Optional(int, default=0)
    link = Optional(str, 255)
    pcr = Optional(str)
    setor = Optional(str, 100)
    atualizacao = Optional(datetime)
    status_agurpado = Optional(str, 50)
    diretor_responsavel = Optional(str)
    equipe = Optional(str)


class Controle(db.Entity):
    _table_ = "controle"
    atualizacao = Optional(datetime)


class Comentario(db.Entity):
    _table_ = "comentario"
    id = PrimaryKey(str, 15, auto=True)
    id_projeto = Required(str, 15)
    autor = Required(str, 50)
    texto = Optional(str)
    atualizacao = Required(datetime)


@db_session
def ultima_atualzacao() -> datetime:
    c = Controle.get(id=1)
    return c.atualizacao.strftime("%d/%m/%Y %H:%M:%S")


class Robo(db.Entity):
    _table_ = "robo"
    id = PrimaryKey(str, 15)
    robo = Required(str, 250)
    resposaveis = Optional(str, 255)
    status_agurpado = Optional(str, 50)
    status = Optional(str, 50)
    fte = Optional(float)
    evolucao = Optional(str, 50)
    setor = Optional(str, 100)
    ano = Optional(int, default=0)
    atualizacao = Optional(datetime)


load_dotenv()

db.bind(
    provider="postgres",
    user=os.getenv("POSTGRESQL_USR"),
    password=os.getenv("POSTGRESQL_PWD"),
    host="sf.lunelli.com.br",
    database=os.getenv("POSTGRESQL_DB"),
)

db.generate_mapping(create_tables=True)
