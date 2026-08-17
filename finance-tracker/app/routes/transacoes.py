from datetime import datetime, date
from decimal import Decimal, InvalidOperation

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from app import db
from app.models import Transacao, Categoria

transacoes_bp = Blueprint("transacoes", __name__, url_prefix="/transacoes")


def _parse_data(valor_str, padrao=None):
    try:
        return datetime.strptime(valor_str, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return padrao


@transacoes_bp.route("/")
@login_required
def listar():
    tipo = request.args.get("tipo", "")
    categoria_id = request.args.get("categoria_id", "")
    data_inicio = _parse_data(request.args.get("data_inicio"))
    data_fim = _parse_data(request.args.get("data_fim"))

    query = Transacao.query.filter_by(usuario_id=current_user.id)

    if tipo in ("receita", "despesa"):
        query = query.filter_by(tipo=tipo)
    if categoria_id.isdigit():
        query = query.filter_by(categoria_id=int(categoria_id))
    if data_inicio:
        query = query.filter(Transacao.data >= data_inicio)
    if data_fim:
        query = query.filter(Transacao.data <= data_fim)

    transacoes = query.order_by(Transacao.data.desc(), Transacao.id.desc()).all()
    categorias = Categoria.query.filter_by(usuario_id=current_user.id).order_by(Categoria.nome).all()

    total_receitas = sum((t.valor for t in transacoes if t.tipo == "receita"), Decimal("0"))
    total_despesas = sum((t.valor for t in transacoes if t.tipo == "despesa"), Decimal("0"))

    return render_template(
        "transacoes.html",
        transacoes=transacoes,
        categorias=categorias,
        filtros={
            "tipo": tipo,
            "categoria_id": categoria_id,
            "data_inicio": request.args.get("data_inicio", ""),
            "data_fim": request.args.get("data_fim", ""),
        },
        total_receitas=total_receitas,
        total_despesas=total_despesas,
    )


def _form_para_template(descricao="", valor="", tipo="", data_str="", categoria_id=""):
    return {
        "descricao": descricao,
        "valor": valor,
        "tipo": tipo,
        "data": data_str,
        "categoria_id": categoria_id,
    }


@transacoes_bp.route("/nova", methods=["GET", "POST"])
@login_required
def nova():
    categorias = Categoria.query.filter_by(usuario_id=current_user.id).order_by(Categoria.nome).all()

    if request.method == "POST":
        erro = _validar_formulario(request.form)
        if erro:
            flash(erro, "error")
            form = _form_para_template(
                request.form.get("descricao", ""),
                request.form.get("valor", ""),
                request.form.get("tipo", ""),
                request.form.get("data", ""),
                request.form.get("categoria_id", ""),
            )
            return render_template("form_transacao.html", categorias=categorias, form=form)

        transacao = Transacao(
            descricao=request.form["descricao"].strip(),
            valor=Decimal(request.form["valor"].replace(",", ".")),
            tipo=request.form["tipo"],
            data=_parse_data(request.form["data"], date.today()),
            categoria_id=int(request.form["categoria_id"]) if request.form.get("categoria_id") else None,
            usuario_id=current_user.id,
        )
        db.session.add(transacao)
        db.session.commit()
        flash("Transação adicionada.", "success")
        return redirect(url_for("transacoes.listar"))

    form = _form_para_template(data_str=date.today().isoformat())
    return render_template("form_transacao.html", categorias=categorias, form=form)


@transacoes_bp.route("/<int:transacao_id>/editar", methods=["GET", "POST"])
@login_required
def editar(transacao_id):
    transacao = Transacao.query.filter_by(id=transacao_id, usuario_id=current_user.id).first_or_404()
    categorias = Categoria.query.filter_by(usuario_id=current_user.id).order_by(Categoria.nome).all()

    if request.method == "POST":
        erro = _validar_formulario(request.form)
        if erro:
            flash(erro, "error")
            form = _form_para_template(
                request.form.get("descricao", ""),
                request.form.get("valor", ""),
                request.form.get("tipo", ""),
                request.form.get("data", ""),
                request.form.get("categoria_id", ""),
            )
            return render_template(
                "form_transacao.html", categorias=categorias, form=form, editando=transacao
            )

        transacao.descricao = request.form["descricao"].strip()
        transacao.valor = Decimal(request.form["valor"].replace(",", "."))
        transacao.tipo = request.form["tipo"]
        transacao.data = _parse_data(request.form["data"], transacao.data)
        transacao.categoria_id = int(request.form["categoria_id"]) if request.form.get("categoria_id") else None

        db.session.commit()
        flash("Transação atualizada.", "success")
        return redirect(url_for("transacoes.listar"))

    form = _form_para_template(
        transacao.descricao,
        f"{transacao.valor:.2f}",
        transacao.tipo,
        transacao.data.isoformat(),
        str(transacao.categoria_id) if transacao.categoria_id else "",
    )
    return render_template("form_transacao.html", categorias=categorias, form=form, editando=transacao)


@transacoes_bp.route("/<int:transacao_id>/excluir", methods=["POST"])
@login_required
def excluir(transacao_id):
    transacao = Transacao.query.filter_by(id=transacao_id, usuario_id=current_user.id).first_or_404()
    db.session.delete(transacao)
    db.session.commit()
    flash("Transação excluída.", "info")
    return redirect(url_for("transacoes.listar"))


def _validar_formulario(form):
    if not form.get("descricao", "").strip():
        return "Informe uma descrição."
    if form.get("tipo") not in ("receita", "despesa"):
        return "Selecione o tipo (receita ou despesa)."
    try:
        valor = Decimal(form.get("valor", "0").replace(",", "."))
        if valor <= 0:
            return "O valor precisa ser maior que zero."
    except (InvalidOperation, AttributeError):
        return "Informe um valor numérico válido."
    if not _parse_data(form.get("data")):
        return "Informe uma data válida."
    return None
