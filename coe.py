from datetime import datetime
import requests

from models.db import db_session, Robo
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
    }""" % (
        board
    )
    pesquisa = {"query": query}

    r = requests.post(url=apiUrl, json=pesquisa, headers=headers)  # make request

    setor = "COE"
    for s in r.json()["data"]["boards"][0]["groups"]:
        status_agurpado = s["title"]
        for p in s["items_page"]["items"]:
            id = p["id"]
            robo = p["name"]
            resposaveis = p["column_values"][1]["text"]
            status = p["column_values"][3]["text"]
            fte = p["column_values"][4]["text"]
            evolucao = ""
            ano = p["column_values"][12]["text"]
            atualizacao = p["updated_at"]
            logar("ROBÔ", f"Robô: {robo}")
            inserir_robo(
                id,
                robo,
                resposaveis,
                status_agurpado,
                status,
                fte if fte != "" else 0,
                evolucao,
                setor,
                ano,
                atualizacao,
            )
    logar("ROBÔ", "Concluído robôs")


def inserir_robo(
    id: "str",
    robo: "str",
    resposaveis: "str",
    status_agurpado: "str",
    status: "str",
    fte: "float",
    evolucao: "int",
    setor: "str",
    ano: "int",
    atualizacao: "str",
):
    with db_session(optimistic=False):
        p = Robo.get(id=id)
        if p is None:
            logar("ROBÔ", f"Robô incluído: {robo}")
            Robo(
                id=id,
                robo=robo,
                resposaveis=resposaveis,
                status_agurpado=status_agurpado,
                status=status,
                fte=fte,
                evolucao=evolucao,
                setor=setor,
                ano=ano,
                atualizacao=datetime.strptime(atualizacao, "%Y-%m-%dT%H:%M:%S%z"),
            )
        else:
            logar("ROBO", f"Robô alterado: {robo}")
            p.robo = robo
            p.resposaveis = resposaveis
            p.status_agurpado = status_agurpado
            p.status = status
            p.fte = fte
            p.evolucao = evolucao
            p.setor = setor
            p.ano = ano
            p.atualizacao = datetime.strptime(atualizacao, "%Y-%m-%dT%H:%M:%S%z")
