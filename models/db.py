from datetime import datetime
from pony.orm import *


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
    setor = Optional(str, 20)
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


class Robo(db.Entity):
    _table_ = "robo"
    id = PrimaryKey(str, 15)
    grupo = Required(str, 50)
    robo = Required(str, 250)
    resposaveis = Optional(str, 255)
    codigo = Optional(str, 10)
    link = Optional(str, 255)
    status = Optional(str, 50)
    fte = Optional(float)
    setor = Optional(str, 255)
    usuario = Optional(str, 255)


@db_session
def ultima_atualzacao() -> datetime:
    c = Controle.get(id=1)
    return c.atualizacao.strftime("%d/%m/%Y %H:%M:%S")


db.bind(provider="sqlite", filename="../data/db.sqlite", create_db=True)

db.generate_mapping()
