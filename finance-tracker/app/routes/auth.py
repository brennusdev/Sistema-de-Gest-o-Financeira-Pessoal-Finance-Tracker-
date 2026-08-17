from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user

from app import db
from app.models import Usuario, Categoria

auth_bp = Blueprint("auth", __name__)

CATEGORIAS_PADRAO = [
    ("Salário", "receita"),
    ("Freelance", "receita"),
    ("Investimentos", "receita"),
    ("Alimentação", "despesa"),
    ("Transporte", "despesa"),
    ("Moradia", "despesa"),
    ("Lazer", "despesa"),
    ("Saúde", "despesa"),
]


@auth_bp.route("/registro", methods=["GET", "POST"])
def registro():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        email = request.form.get("email", "").strip().lower()
        senha = request.form.get("senha", "")
        confirmar = request.form.get("confirmar_senha", "")

        erro = None
        if not nome or not email or not senha:
            erro = "Preencha todos os campos."
        elif senha != confirmar:
            erro = "As senhas não coincidem."
        elif len(senha) < 6:
            erro = "A senha precisa ter pelo menos 6 caracteres."
        elif Usuario.query.filter_by(email=email).first():
            erro = "Já existe uma conta com este e-mail."

        if erro:
            flash(erro, "error")
            return render_template("registro.html", nome=nome, email=email)

        usuario = Usuario(nome=nome, email=email)
        usuario.set_senha(senha)
        db.session.add(usuario)
        db.session.flush()  # garante usuario.id antes de criar categorias

        for nome_cat, tipo_cat in CATEGORIAS_PADRAO:
            db.session.add(Categoria(nome=nome_cat, tipo=tipo_cat, usuario_id=usuario.id))

        db.session.commit()

        login_user(usuario)
        flash("Conta criada com sucesso. Bem-vindo(a)!", "success")
        return redirect(url_for("dashboard.index"))

    return render_template("registro.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        senha = request.form.get("senha", "")

        usuario = Usuario.query.filter_by(email=email).first()
        if usuario and usuario.checar_senha(senha):
            login_user(usuario)
            proxima = request.args.get("next")
            return redirect(proxima or url_for("dashboard.index"))

        flash("E-mail ou senha inválidos.", "error")

    return render_template("login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Você saiu da sua conta.", "info")
    return redirect(url_for("auth.login"))
