import os
import requests
from dotenv import load_dotenv

from models.db import *
from log.log import *
from models.db import *


def carregar():
    load_dotenv()

    apiKey = os.getenv("API_KEY")
    apiUrl = os.getenv("BASE_URL")
    headers = {"Authorization": apiKey}
    board = "5808464075"

    logar("MONDAY", f"Buscando projetos")
    query = """{
    boards(ids: %s) {
        groups {
            id
            title
            position
            color
            items_page(limit: 100) {
                items {
                    id
                    name
                    column_values {
                        column {
                            title
                        }
                        text
                    }
                  }
              }
            }
        }
    }""" % (
        board
    )
    data = {"query": query}

    r = requests.post(url=apiUrl, json=data, headers=headers)  # make request

    for s in r.json()["data"]["boards"][0]["groups"]:
        setor = s["title"]
        for p in s["items_page"]["items"]:
            id = p["id"]
            projeto = p["name"]
            resposaveis = p["column_values"][1]["text"]
            status = p["column_values"][2]["text"]
            data = p["column_values"][3]["text"]
            evolucao = p["column_values"][4]["text"]
            link = p["column_values"][5]["text"]
            pcr = p["column_values"][6]["text"]

            inserir_projeto(
                id, projeto, resposaveis, status, data, evolucao, link, pcr, setor
            )
    atualizar()
    logar("MONDAY", f"Concluído")


def inserir_projeto(
    id: "str",
    projeto: "str",
    resposaveis: "str",
    status: "str",
    data: "str",
    evolucao: "int",
    link: "str",
    pcr: "str",
    setor: "str",
):
    with db_session(optimistic=False):
        p = Projeto.get(id=id)
        if p == None:
            logar("PROJETO", f"Projeto incluído: {projeto}")
            Projeto(
                id=id,
                projeto=projeto,
                resposaveis=resposaveis,
                status=status,
                data=data,
                evolucao=evolucao,
                link=link,
                pcr=pcr,
                setor=setor,
            )
        else:
            logar("PROJETO", f"Projeto alterado: {projeto}")
            p.projeto = projeto
            p.resposaveis = resposaveis
            p.status = status
            p.data = data
            p.evolucao = evolucao
            p.link = link
            p.pcr = pcr
            p.setor = setor


def atualizar():
    with db_session(optimistic=False):
        c = Controle.get(id=1)
        c.atualizacao = datetime.now()


if __name__ == "__main__":
    carregar()
