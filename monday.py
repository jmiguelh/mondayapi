import os
import requests
from dotenv import load_dotenv
from datetime import datetime

# from models.db import *
from log.log import logar
from models.db import db_session, Projeto, Controle, Comentario


def carregar():
    load_dotenv()

    apiKey = os.getenv("API_KEY")
    apiUrl = os.getenv("BASE_URL")
    headers = {"Authorization": apiKey}
    board = "5808464075"

    carregar_projetos(apiUrl, headers, board)
    carregar_comentarios(apiUrl, headers)
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


def atualizar():
    with db_session(optimistic=False):
        c = Controle.get(id=1)
        c.atualizacao = datetime.now()


def carregar_comentarios(apiUrl: "str", headers: "str"):
    logar("COMENTÁROS", "Buscando comentários")
    query = """{
            updates(limit: 1000) {
                id
                item_id
                creator {
                name
                }
                text_body
                created_at
            }
        }"""
    pesquisa = {"query": query}

    r = requests.post(url=apiUrl, json=pesquisa, headers=headers)  # make request

    for c in r.json()["data"]["updates"]:
        id = c["id"]
        id_projeto = c["item_id"]
        autor = c["creator"]["name"]
        texto = c["text_body"]
        atualizacao = c["created_at"]
        with db_session(optimistic=False):
            p = Projeto.get(id=id_projeto)
            if p is not None:
                logar("COMENTÁROS", f"Projetos: {p.projeto}")

                inserir_comentario(
                    id,
                    id_projeto,
                    autor,
                    texto,
                    atualizacao,
                )
    logar("COMENTÁROS", "Concluído comentários")


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


if __name__ == "__main__":
    carregar()
