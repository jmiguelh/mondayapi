from datetime import datetime
import requests

from models.db import db_session, Projeto
from log.log import logar


def carregar_coe(apiUrl: "str", headers: "str", board: "str"):
    logar("COE", "Buscando robôs")
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
                    updated_at
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
    }""" % (board)
    pesquisa = {"query": query}

    r = requests.post(url=apiUrl, json=pesquisa, headers=headers)  # make request

    setor = "COE"
    for s in r.json()["data"]["boards"][0]["groups"]:
        status = s["title"]
        for p in s["items_page"]["items"]:
            if p["column_values"][11]["text"] == "2025":
                id = p["id"]
                projeto = p["name"]
                resposaveis = p["column_values"][1]["text"]
                # status = p["column_values"][3]["text"]
                # fte = p["column_values"][4]["text"]
                # link = p["column_values"][5]["text"]
                # pcr = p["column_values"][6]["text"]
                atualizacao = p["updated_at"]
                logar("ROBÔ", f"Robô: {projeto}")
                inserir_projeto(
                    id,
                    projeto,
                    resposaveis,
                    status,
                    "",
                    0,
                    "",
                    "",
                    setor,
                    atualizacao,
                )
    logar("ROBÔ", "Concluído robôs")


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
    atualizacao: "str",
):
    with db_session(optimistic=False):
        p = Projeto.get(id=id)
        if p is None:
            logar("ROBÔ", f"Robô incluído: {projeto}")
            Projeto(
                id=id,
                projeto=projeto,
                resposaveis=resposaveis,
                status=status,
                evolucao=evolucao,
                link=link,
                pcr=pcr,
                setor=setor,
                atualizacao=datetime.strptime(atualizacao, "%Y-%m-%dT%H:%M:%S%z"),
            )
        else:
            logar("PROJETO", f"Projeto alterado: {projeto}")
            p.projeto = projeto
            p.resposaveis = resposaveis
            p.status = status
            if data != "":
                p.data = datetime.strptime(data, "%Y-%m-%d")
            p.evolucao = evolucao
            p.link = link
            p.pcr = pcr
            p.setor = setor
            p.atualizacao = datetime.strptime(atualizacao, "%Y-%m-%dT%H:%M:%S%z")
