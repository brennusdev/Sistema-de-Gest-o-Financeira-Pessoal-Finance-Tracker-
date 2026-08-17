from calendar import month_abbr
from datetime import date
from decimal import Decimal

from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from sqlalchemy import extract

from app import db
from app.models import Transacao, Categoria

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@login_required
def index():
    hoje = date.today()

    transacoes_mes = Transacao.query.filter(
        Transacao.usuario_id == current_user.id,
        extract("year", Transacao.data) == hoje.year,
        extract("month", Transacao.data) == hoje.month,
    ).all()

    receitas_mes = sum((t.valor for t in transacoes_mes if t.tipo == "receita"), Decimal("0"))
    despesas_mes = sum((t.valor for t in transacoes_mes if t.tipo == "despesa"), Decimal("0"))

    todas = Transacao.query.filter_by(usuario_id=current_user.id).all()
    saldo_total = sum((t.valor if t.tipo == "receita" else -t.valor for t in todas), Decimal("0"))

    ultimas = (
        Transacao.query.filter_by(usuario_id=current_user.id)
        .order_by(Transacao.data.desc(), Transacao.id.desc())
        .limit(6)
        .all()
    )

    return render_template(
        "dashboard.html",
        receitas_mes=receitas_mes,
        despesas_mes=despesas_mes,
        saldo_mes=receitas_mes - despesas_mes,
        saldo_total=saldo_total,
        ultimas=ultimas,
    )


@dashboard_bp.route("/api/gastos-por-categoria")
@login_required
def gastos_por_categoria():
    hoje = date.today()
    resultado = (
        db.session.query(Categoria.nome, db.func.sum(Transacao.valor))
        .join(Transacao, Transacao.categoria_id == Categoria.id)
        .filter(
            Transacao.usuario_id == current_user.id,
            Transacao.tipo == "despesa",
            extract("year", Transacao.data) == hoje.year,
            extract("month", Transacao.data) == hoje.month,
        )
        .group_by(Categoria.nome)
        .all()
    )
    return jsonify(
        {
            "labels": [nome for nome, _ in resultado],
            "valores": [float(valor) for _, valor in resultado],
        }
    )


@dashboard_bp.route("/api/evolucao-mensal")
@login_required
def evolucao_mensal():
    hoje = date.today()
    meses = []
    receitas = []
    despesas = []

    ano, mes = hoje.year, hoje.month
    sequencia = []
    for i in range(5, -1, -1):
        m = mes - i
        a = ano
        while m <= 0:
            m += 12
            a -= 1
        sequencia.append((a, m))

    for ano_ref, mes_ref in sequencia:
        registros = Transacao.query.filter(
            Transacao.usuario_id == current_user.id,
            extract("year", Transacao.data) == ano_ref,
            extract("month", Transacao.data) == mes_ref,
        ).all()
        r = sum((t.valor for t in registros if t.tipo == "receita"), Decimal("0"))
        d = sum((t.valor for t in registros if t.tipo == "despesa"), Decimal("0"))
        meses.append(f"{month_abbr[mes_ref]}/{str(ano_ref)[2:]}")
        receitas.append(float(r))
        despesas.append(float(d))

    return jsonify({"meses": meses, "receitas": receitas, "despesas": despesas})
