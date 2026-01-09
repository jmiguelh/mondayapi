from datetime import datetime
import os
import requests

from dotenv import load_dotenv

from coe import carregar_coe
from log.log import logar
from models.db import (
    db_session,
    Projeto,
    Controle,
    Comentario,
)  # noqa: F401

load_dotenv()


def carregar():
    apiUrl, headers, portifolio, coe = parametros()

    carregar_projetos(apiUrl, headers, portifolio)
    carregar_coe(apiUrl, headers, coe)

    atualizar()
    logar("MONDAY", "Concluído")


def parametros():
    apiKey = os.getenv("API_KEY")
    apiUrl = os.getenv("BASE_URL")
    headers = {"Authorization": apiKey}
    portifolio = os.getenv("BOARD_PORTFOLIO")
    coe = os.getenv("BOARD_COE")
    return apiUrl, headers, portifolio, coe


def carregar_projetos(apiUrl: "str", headers: "str", board: "str"):
    logar("PROJETOS", "Buscando projetos")
    query = """{
    boards(ids: %s) {
        groups {
            title
            items_page(limit:50) {
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
                        created_at
                        creator {
                            name
                        }
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
            equipe = (
                p["column_values"][6]["text"]
                if p["column_values"][6]["text"] is not None
                else ""
            )
            pcr = p["column_values"][7]["text"]
            atualizacao = p["updated_at"]
            data_lb = p["column_values"][8]["text"]
            diretor_responsavel = (
                p["column_values"][9]["text"]
                if p["column_values"][9]["text"] is not None
                else ""
            )
            logar("PROJETOS", f"Projetos: {projeto}")
            inserir_projeto(
                id,
                projeto,
                resposaveis,
                status,
                data,
                data_lb,
                evolucao,
                link,
                pcr,
                setor,
                atualizacao,
                diretor_responsavel,
                equipe,
            )
            for c in p["updates"]:
                id_comentario = c["id"]
                id_projeto = id
                autor = c["creator"]["name"]
                texto = c["text_body"]
                atualizacao = c["created_at"]
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
    data_lb: "str",
    evolucao: "int",
    link: "str",
    pcr: "str",
    setor: "str",
    atualizacao: "str",
    diretor_responsavel: "str",
    equipe: "str",
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
                diretor_responsavel=diretor_responsavel,
                equipe=equipe,
            )
        else:
            logar("PROJETO", f"Projeto alterado: {projeto}")
            p.projeto = projeto
            p.resposaveis = resposaveis
            p.status = status
            p.status_agurpado = stautus_agrupado(status)
            if data != "":
                data_old = p.data.strftime("%Y-%m-%d") if p.data is not None else ""
                if data != data_old:
                    criar_comentario(
                        id,
                        data_old,
                        datetime.strptime(data, "%Y-%m-%d"),
                    )
                p.data = datetime.strptime(data, "%Y-%m-%d")
            if data_lb != "":
                p.data_lb = datetime.strptime(data_lb, "%Y-%m-%d")
            p.evolucao = evolucao
            p.link = link
            p.pcr = pcr
            p.setor = setor
            p.atualizacao = datetime.strptime(atualizacao, "%Y-%m-%dT%H:%M:%S%z")
            p.diretor_responsavel = diretor_responsavel
            p.equipe = equipe


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
        case "Em validação":
            retorno = "Execução"
        case "Não iniciado":
            retorno = "Não iniciado"
        case "Em análise":
            retorno = "Não iniciado"
        case "Atualizar projeto":
            retorno = "Não iniciado"
        case "Aguardando Aprovação":
            retorno = "Não iniciado"
        case "Cancelado":
            retorno = "Concluído"
        case _:
            retorno = status

    return retorno


def criar_comentario(
    id_projeto: "str",
    data_old: "datetime",
    data_new: "datetime",
):
    apiUrl, headers, portifolio, coe = parametros()

    if data_old != "":
        comentario = f"Atualização da data de conclusão do projeto:<br>Data antiga: {data_old.strftime('%d/%m/%Y')}<br>Data nova: {data_new.strftime('%d/%m/%Y')}"
    else:
        comentario = f"Atualização da data de conclusão do projeto:<br>Data antiga: N/A<br>Data nova: {data_new.strftime('%d/%m/%Y')}"

    query = """mutation {
                create_update(
                    item_id: %s
                    body: "%s"
                ) {
                    id
                    body
                    created_at
                }
                }""" % (
        id_projeto,
        comentario,
    )

    pesquisa = {"query": query}
    r = requests.post(url=apiUrl, json=pesquisa, headers=headers)
    logar("PROJETO", f"Cometário adicionado: {comentario}")
    return r.json()


if __name__ == "__main__":
    carregar()
