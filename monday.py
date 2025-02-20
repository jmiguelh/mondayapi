from datetime import datetime
import os
import requests

from dotenv import load_dotenv

from coe import carregar_coe
from log.log import logar
from models.db import db_session, Projeto, Controle, Comentario, ultima_atualzacao  # noqa: F401

load_dotenv()


def carregar():
    apiKey = os.getenv("API_KEY")
    apiUrl = os.getenv("BASE_URL")
    headers = {"Authorization": apiKey}
    portifolio = os.getenv("BOARD_PORTFOLIO")
    coe = os.getenv("BOARD_COE")

    carregar_projetos(apiUrl, headers, portifolio)
    carregar_coe(apiUrl, headers, coe)

    atualizar()
    logar("MONDAY", "Concluído")


def carregar_projetos(apiUrl: "str", headers: "str", board: "str"):
    logar("PROJETOS", "Buscando projetos")
    query = """{
    boards(ids: %s) {
        groups {
            id
            title
            position
            color
            items_page {
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
                    updates {
                        id
                        text_body
                        updated_at
                        creator {
                        name
                        }
                    }
                  }
              }
            }
        }
    }""" % (board)
    pesquisa = {"query": query}

    r = requests.post(url=apiUrl, json=pesquisa, headers=headers)  # make request

    for s in r.json()["data"]["boards"][0]["groups"]:
        setor = s["title"].replace("PLANO ESTRATÉGICO TI E DIGITAL   - ", "")
        for p in s["items_page"]["items"]:
            id = p["id"]
            projeto = p["name"]
            resposaveis = p["column_values"][1]["text"]
            status = p["column_values"][2]["text"]
            data = p["column_values"][3]["text"]
            evolucao = p["column_values"][4]["text"]
            link = p["column_values"][5]["text"]
            pcr = p["column_values"][6]["text"]
            atualizacao = p["updated_at"]
            logar("PROJETOS", f"Projetos: {projeto}")
            inserir_projeto(
                id,
                projeto,
                resposaveis,
                status,
                data,
                evolucao,
                link,
                pcr,
                setor,
                atualizacao,
            )
            for c in p["updates"]:
                id_comentario = c["id"]
                id_projeto = id
                autor = c["creator"]["name"]
                texto = c["text_body"]
                atualizacao = c["updated_at"]
                logar("COMENTÁROS", f"Projetos: {projeto}")

                inserir_comentario(
                    id_comentario,
                    id_projeto,
                    autor,
                    texto,
                    atualizacao,
                )
    logar("PROJETOS", "Concluído projetos")


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
            logar("PROJETO", f"Projeto incluído: {projeto}")
            Projeto(
                id=id,
                projeto=projeto,
                resposaveis=resposaveis,
                status=status,
                status_agurpado=stautus_agrupado(status),
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
            p.status_agurpado = stautus_agrupado(status)
            if data != "":
                p.data = datetime.strptime(data, "%Y-%m-%d")
            p.evolucao = evolucao
            p.link = link
            p.pcr = pcr
            p.setor = setor
            p.atualizacao = datetime.strptime(atualizacao, "%Y-%m-%dT%H:%M:%S%z")


def atualizar():
    with db_session(optimistic=False):
        c = Controle.get(id=1)
        c.atualizacao = datetime.now()


def inserir_comentario(
    id: "str",
    id_projeto: "str",
    autor: "str",
    texto: "str",
    atualizacao: "str",
):
    with db_session(optimistic=False):
        c = Comentario.get(id=id)
        if c is None:
            Comentario(
                id=id,
                id_projeto=id_projeto,
                autor=autor,
                texto=texto,
                atualizacao=datetime.strptime(atualizacao, "%Y-%m-%dT%H:%M:%S.%fZ"),
            )
        else:
            c.id_projeto = id_projeto
            c.autor = autor
            c.texto = texto
            c.atualizacao = datetime.strptime(atualizacao, "%Y-%m-%dT%H:%M:%S.%fZ")


def stautus_agrupado(status: "str") -> str:
    match status:
        case "Em progresso":
            retorno = "Execução"
        case "Parado":
            retorno = "Parado"
        case "Feito":
            retorno = "Concluído"
        case "Em planejamento":
            retorno = "Execução"
        case "Não iniciado":
            retorno = "Não iniciado"
        case "Em análise":
            retorno = "Não iniciado"
        case "Atualizar projeto":
            retorno = "Não iniciado"
        case "Aguardando Aprovação":
            retorno = "Não iniciado"

    return retorno


if __name__ == "__main__":
    carregar()
