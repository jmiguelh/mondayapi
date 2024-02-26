from datetime import datetime
from pony.orm import *


db = Database()


class Projeto(db.Entity):
    _table_ = "projeto"
    id = PrimaryKey(str, 15)
    projeto = Required(str, 250)
    resposaveis = Optional(str, 255)
    status = Optional(str, 50)
    data = Optional(str)
    evolucao = Optional(int, default=0)
    link = Optional(str, 255)
    pcr = Optional(str)
    setor = Optional(str, 20)


class Controle(db.Entity):
    _table_ = "controle"
    atualizacao = Optional(datetime)


@db_session
def ultima_atualzacao() -> datetime:
    c = Controle.get(id=1)
    return c.atualizacao.strftime("%d/%m/%Y %H:%M:%S")


db.bind(provider="sqlite", filename="../data/db.sqlite", create_db=True)

db.generate_mapping()
