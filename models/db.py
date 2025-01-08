from datetime import datetime
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


db.bind(
    provider="postgres",
    user="monday",
    password="monday@2024",
    host="sf.lunelli.com.br",
    database="monday",
)
# db.bind(provider="sqlite", filename="../data/db.sqlite", create_db=True)

db.generate_mapping()
