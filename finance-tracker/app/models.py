from datetime import datetime, date

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))


class Usuario(UserMixin, db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    senha_hash = db.Column(db.String(255), nullable=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    categorias = db.relationship(
        "Categoria", backref="usuario", cascade="all, delete-orphan", lazy=True
    )
    transacoes = db.relationship(
        "Transacao", backref="usuario", cascade="all, delete-orphan", lazy=True
    )
    metas = db.relationship(
        "Meta", backref="usuario", cascade="all, delete-orphan", lazy=True
    )

    def set_senha(self, senha_plana):
        self.senha_hash = generate_password_hash(senha_plana)

    def checar_senha(self, senha_plana):
        return check_password_hash(self.senha_hash, senha_plana)


class Categoria(db.Model):
    __tablename__ = "categorias"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), nullable=False)
    tipo = db.Column(db.String(10), nullable=False)  # 'receita' ou 'despesa'
    cor = db.Column(db.String(7), default="#3F6C51")
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)

    transacoes = db.relationship("Transacao", backref="categoria", lazy=True)

    __table_args__ = (
        db.UniqueConstraint("nome", "tipo", "usuario_id", name="uq_categoria_usuario"),
    )


class Transacao(db.Model):
    __tablename__ = "transacoes"

    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(200), nullable=False)
    valor = db.Column(db.Numeric(10, 2), nullable=False)
    tipo = db.Column(db.String(10), nullable=False)  # 'receita' ou 'despesa'
    data = db.Column(db.Date, nullable=False, default=date.today)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    categoria_id = db.Column(db.Integer, db.ForeignKey("categorias.id"), nullable=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)


class Meta(db.Model):
    __tablename__ = "metas"

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(120), nullable=False)
    valor_alvo = db.Column(db.Numeric(10, 2), nullable=False)
    valor_atual = db.Column(db.Numeric(10, 2), default=0)
    prazo = db.Column(db.Date, nullable=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
