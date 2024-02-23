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


db.bind(provider="sqlite", filename="../data/db.sqlite", create_db=True)

db.generate_mapping()
