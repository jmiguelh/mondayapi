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


def carregar(projetos=True, robos=True, id_projeto=0, demandas=True):
    apiUrl, headers, portifolio, coe, demanda = parametros()
    if id_projeto != 0:
        carregar_projeto(apiUrl, headers, id_projeto)
    else:
        if projetos:
            carregar_projetos(apiUrl, headers, portifolio)
        if demandas:
            carregar_demandas(apiUrl, headers, demanda)
        if robos:
            carregar_coe(apiUrl, headers, coe)
        atualizar()
    logar("MONDAY", "Concluído")


def parametros():
    apiKey = os.getenv("API_KEY")
    apiUrl = os.getenv("BASE_URL")
    headers = {"Authorization": apiKey}
    portifolio = os.getenv("BOARD_PORTFOLIO")
    coe = os.getenv("BOARD_COE")
    demanda = os.getenv("BOARD_DEMANDAS")
    return apiUrl, headers, portifolio, coe, demanda


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
            salvar_projeto(setor, p)
    logar("PROJETOS", "Concluído projetos")


def salvar_projeto(setor, p):
    id = p["id"]
    projeto = p["name"]
    atualizacao = p["updated_at"]
    for c in p["column_values"]:
        if c["column"]["title"] == "Equipe":
            equipe = c["text"] if c["text"] is not None else ""
        elif c["column"]["title"] == "Pessoa":
            resposaveis = c["text"]
        elif c["column"]["title"] == "Status":
            status = c["text"]
        elif c["column"]["title"] == "Data Final":
            data = c["text"]
        elif c["column"]["title"] == "% Evolução":
            evolucao = c["text"]
        elif c["column"]["title"] == "Link":
            link = c["text"]
        elif c["column"]["title"] == "PCR":
            pcr = c["text"]
        elif c["column"]["title"] == "Data final LB":
            data_lb = c["text"]
        elif c["column"]["title"] == "Diretor Responsável":
            diretor_responsavel = c["text"] if c["text"] is not None else ""
        elif c["column"]["title"] == "Prioridade":
            if c["text"] == "":
                prioridade = "-"
            else:
                if len(c["text"]) < 2:
                    prioridade = "0" + c["text"]
                else:
                    prioridade = c["text"]
    pcr = "Não"

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
        str(prioridade),
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
    prioridade: "str",
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
                prioridade=prioridade,
            )
        else:
            logar("PROJETO", f"Projeto alterado: {projeto}")
            p.projeto = projeto
            p.resposaveis = resposaveis
            p.status = status
            p.status_agurpado = stautus_agrupado(status)
            data_old = p.data.strftime("%Y-%m-%d") if p.data is not None else ""
            if data != data_old:
                criar_comentario(
                    id,
                    comentario_alteracao_data_fim(
                        (
                            datetime.strptime(data_old, "%Y-%m-%d")
                            if data_old != ""
                            else None
                        ),
                        datetime.strptime(data, "%Y-%m-%d") if data != "" else None,
                    ),
                )
            p.data = datetime.strptime(data, "%Y-%m-%d") if data != "" else None
            p.data_lb = (
                datetime.strptime(data_lb, "%Y-%m-%d") if data_lb != "" else None
            )
            p.evolucao = evolucao
            p.link = link
            p.pcr = pcr
            p.setor = setor if setor != "" else p.setor
            p.atualizacao = datetime.strptime(atualizacao, "%Y-%m-%dT%H:%M:%S%z")
            p.diretor_responsavel = diretor_responsavel
            p.equipe = equipe
            p.prioridade = prioridade


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
        case "Aguardando orçamento":
            retorno = "Execução"

        # Demandas
        case "Sum":
            retorno = "Execução"
        case "Desenvolvimento":
            retorno = "Execução"
        case "Backlog":
            retorno = "Não iniciado"
        case "Corretiva":
            retorno = "Execução"
        case "Aprov. pendente":
            retorno = "Não iniciado"
        case "Orçamento":
            retorno = "Não iniciado"
        case "Homologação":
            retorno = "Execução"
        case "Erro":
            retorno = "Execução"
        case "Levantamento":
            retorno = "Execução"
        # Fim demandas

        case _:
            retorno = status

    return retorno


def comentario_alteracao_data_fim(
    data_old: "datetime",
    data_new: "datetime",
):
    if data_old is None:
        return f"Atualização da data de conclusão do projeto:<br>Data antiga: N/a<br>Data nova: {data_new.strftime("%d/%m/%Y")}"
    elif data_new is None:
        return f"Atualização da data de conclusão do projeto:<br>Data antiga: {data_old.strftime("%d/%m/%Y")}<br>Data nova: N/A"
    else:
        return f"Atualização da data de conclusão do projeto:<br>Data antiga: {data_old.strftime("%d/%m/%Y")}<br>Data nova: {data_new.strftime("%d/%m/%Y")}"


def criar_comentario(id_projeto: "str", comentario: "str"):
    apiUrl, headers, portifolio, coe, demanda = parametros()

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
        comentario.replace("\n", "\\n"),
    )
    # logar("PROJETO", f"{query}")
    pesquisa = {"query": query}
    r = requests.post(url=apiUrl, json=pesquisa, headers=headers)
    return r.json()


def alterar_projeto(id_projeto: "str", evolucao: "str", status: "str", data_fim: "str"):
    apiUrl, headers, portifolio, _ = parametros()

    query = """mutation {
                change_multiple_column_values(
                    board_id: %s
                    item_id: %s
                    column_values: "{\\"n_meros\\":%s, \\"status\\":{\\"label\\":\\"%s\\"}, \\"data\\":\\"%s\\"}"
                ) {
                    id
                }
                }""" % (
        portifolio,
        id_projeto,
        evolucao,
        status,
        data_fim,
    )
    # logar("PROJETO", f"{query}")
    pesquisa = {"query": query}
    r = requests.post(url=apiUrl, json=pesquisa, headers=headers)
    return r.json()


def carregar_projeto(apiUrl: "str", headers: "str", id_projeto: "str"):
    logar("PROJETOS", "Buscando projetos")
    query = """{
            items(ids: %s) {
                id
                name
                email
                updated_at
                column_values {
                column {
                    id
                    title
                }
                id
                text
                }
                updates {
                id
                body
                text_body
                updated_at
                created_at
                creator {
                    name
                    email
                }
                }
            }
    }""" % (
        id_projeto
    )
    pesquisa = {"query": query}

    r = requests.post(url=apiUrl, json=pesquisa, headers=headers)  # make request

    for p in r.json()["data"]["items"]:
        salvar_projeto("", p)
    logar("PROJETOS", "Concluído projetos")


def carregar_demandas(apiUrl: "str", headers: "str", board: "str"):
    logar("DEMANDAS", "Buscando demandas")
    query = """{
        boards(ids: %s) {
            groups {
                title
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

    for s in r.json()["data"]["boards"][0]["groups"]:
        setor = "Sistemas"
        area = s["title"]
        for p in s["items_page"]["items"]:
            salvar_demanda(setor, p, area)
    logar("DEMANDAS", "Concluído demandas")


def salvar_demanda(setor, p, area):
    id = p["id"]
    projeto = area + " - " + p["name"]
    atualizacao = p["updated_at"]
    for c in p["column_values"]:
        if c["column"]["title"] == "Pessoa":
            resposaveis = c["text"]
        elif c["column"]["title"] == "Status":
            status = c["text"]
        elif c["column"]["title"] == "Data":
            data = c["text"]
        elif c["column"]["title"] == "PCR":
            pcr = c["text"]
        elif c["column"]["title"] == "Data LB":
            data_lb = c["text"]
        elif c["column"]["title"] == "Prioridade":
            if c["text"] == "":
                prioridade = "-"
            else:
                if len(c["text"]) < 2:
                    prioridade = "0" + c["text"]
                else:
                    prioridade = c["text"]
    pcr = "Não"

    logar("DEMANDAS", f"Demandas: {projeto}")
    inserir_projeto(
        id,
        projeto,
        resposaveis,
        status,
        data,
        data_lb,
        evolucao_demanda(status),
        "",  # link,
        pcr,
        setor,
        atualizacao,
        "",  # diretor_responsavel,
        "",  # equipe,
        str(prioridade),
    )


def evolucao_demanda(status: "str") -> str:
    match status:
        case "Sum":
            retorno = 75
        case "Desenvolvimento":
            retorno = 50
        case "Backlog":
            retorno = 0
        case "Corretiva":
            retorno = 50
        case "Aprov. pendente":
            retorno = 0
        case "Orçamento":
            retorno = 0
        case "Parado":
            retorno = 0
        case "Homologação":
            retorno = 50
        case "Cancelado":
            retorno = 100
        case "Erro":
            retorno = 50
        case "Levantamento":
            retorno = 50
        case "Feito":
            retorno = 100
        case _:
            retorno = 0

    return retorno


if __name__ == "__main__":
    carregar()
