from datetime import date
from pony.orm import *


db = Database()


class Projeto(db.Entity):
    _table_ = "projeto"
    id = PrimaryKey(int, auto=True)
    projeto = Required(str, 250)
    resposaveis = Optional(str, 255)
    status = Optional(str, 50)
    data = Optional(date)
    evolucao = Optional(int, default=0)
    link = Optional(str, 255)
    pcr = Optional(str)


db.generate_mapping()
