from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

import src.app as app_module


@pytest.fixture(autouse=True)
def isolamento_atividades(monkeypatch):
    monkeypatch.setattr(app_module, "activities", deepcopy(app_module.activities))


@pytest.fixture
def cliente():
    with TestClient(app_module.app) as test_client:
        yield test_client


def test_raiz_redireciona_para_pagina_estatica(cliente):
    # Preparação
    url = "/"

    # Ação
    resposta = cliente.get(url, follow_redirects=False)

    # Verificação
    assert resposta.status_code == 307
    assert resposta.headers["location"] == "/static/index.html"


def test_lista_atividades(cliente):
    # Preparação
    atividades_esperadas = app_module.activities

    # Ação
    resposta = cliente.get("/activities")

    # Verificação
    assert resposta.status_code == 200
    assert resposta.json() == atividades_esperadas


def test_inscreve_estudante_em_atividade(cliente):
    # Preparação
    nome_atividade = "Basketball Team"
    email = "aluno@mergington.edu"

    # Ação
    resposta = cliente.post(
        f"/activities/{nome_atividade}/signup",
        params={"email": email},
    )

    # Verificação
    assert resposta.status_code == 200
    assert resposta.json() == {
        "message": f"Signed up {email} for {nome_atividade}"
    }
    assert email in app_module.activities[nome_atividade]["participants"]


def test_inscricao_rejeita_atividade_inexistente(cliente):
    # Preparação
    nome_atividade = "Atividade inexistente"

    # Ação
    resposta = cliente.post(
        f"/activities/{nome_atividade}/signup",
        params={"email": "aluno@mergington.edu"},
    )

    # Verificação
    assert resposta.status_code == 404
    assert resposta.json() == {"detail": "Activity not found"}


def test_inscricao_rejeita_estudante_ja_inscrito(cliente):
    # Preparação
    nome_atividade = "Chess Club"
    email = "michael@mergington.edu"

    # Ação
    resposta = cliente.post(
        f"/activities/{nome_atividade}/signup",
        params={"email": email},
    )

    # Verificação
    assert resposta.status_code == 400
    assert resposta.json() == {
        "detail": "Student already signed up for this activity"
    }


def test_cancela_inscricao_de_estudante(cliente):
    # Preparação
    nome_atividade = "Chess Club"
    email = "michael@mergington.edu"

    # Ação
    resposta = cliente.delete(
        f"/activities/{nome_atividade}/participants",
        params={"email": email},
    )

    # Verificação
    assert resposta.status_code == 200
    assert resposta.json() == {
        "message": f"Inscrição de {email} cancelada em {nome_atividade}."
    }
    assert email not in app_module.activities[nome_atividade]["participants"]


def test_cancelamento_rejeita_atividade_inexistente(cliente):
    # Preparação
    nome_atividade = "Atividade inexistente"

    # Ação
    resposta = cliente.delete(
        f"/activities/{nome_atividade}/participants",
        params={"email": "aluno@mergington.edu"},
    )

    # Verificação
    assert resposta.status_code == 404
    assert resposta.json() == {"detail": "Atividade não encontrada"}


def test_cancelamento_rejeita_participante_nao_inscrito(cliente):
    # Preparação
    nome_atividade = "Chess Club"
    email = "aluno@mergington.edu"

    # Ação
    resposta = cliente.delete(
        f"/activities/{nome_atividade}/participants",
        params={"email": email},
    )

    # Verificação
    assert resposta.status_code == 404
    assert resposta.json() == {
        "detail": "Participante não está inscrito nesta atividade"
    }