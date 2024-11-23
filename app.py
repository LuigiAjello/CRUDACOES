from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import locale

locale.setlocale(locale.LC_NUMERIC, "pt_BR.UTF-8")

app = Flask(__name__)
app.secret_key = "secret_key"  # Necessário para flash messages
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///carteiras.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modelos
class Carteira(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    acoes = db.relationship('Acao', backref='carteira', cascade="all, delete-orphan")

class Acao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    carteira_id = db.Column(db.Integer, db.ForeignKey('carteira.id'), nullable=False)
    ticker = db.Column(db.String(10), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    preco_medio = db.Column(db.Float, nullable=False)

# Rotas
@app.route('/')
def index():
    carteiras = Carteira.query.all()
    return render_template('index.html', carteiras=carteiras)

@app.route('/carteira/<int:carteira_id>')
def detalhes_carteira(carteira_id):
    carteira = Carteira.query.get_or_404(carteira_id)
    return render_template('detalhes_carteira.html', carteira=carteira)

@app.route('/carteira/nova', methods=['GET', 'POST'])
def nova_carteira():
    if request.method == 'POST':
        nome = request.form['nome']
        if nome:
            nova_carteira = Carteira(nome=nome)
            db.session.add(nova_carteira)
            db.session.commit()
            flash('Carteira criada com sucesso!')
            return redirect(url_for('index'))
    return render_template('form_carteira.html')

@app.route('/acao/nova/<int:carteira_id>', methods=['GET', 'POST'])
def nova_acao(carteira_id):
    carteira = Carteira.query.get_or_404(carteira_id)
    if request.method == 'POST':
        ticker = request.form['ticker']
        quantidade = request.form['quantidade']
        preco_medio = request.form['preco_medio'].replace(',', '.')
        if ticker and quantidade and preco_medio:
            nova_acao = Acao(
                ticker=ticker.upper(),
                quantidade=int(quantidade),
                preco_medio=float(preco_medio),
                carteira_id=carteira.id
            )
            db.session.add(nova_acao)
            db.session.commit()
            flash('Ação adicionada com sucesso!')
            return redirect(url_for('detalhes_carteira', carteira_id=carteira.id))
    return render_template('form_acao.html', carteira=carteira)

@app.route('/acao/editar/<int:acao_id>', methods=['GET', 'POST'])
def editar_acao(acao_id):
    acao = Acao.query.get_or_404(acao_id)
    if request.method == 'POST':
        acao.ticker = request.form['ticker'].upper()
        acao.quantidade = int(request.form['quantidade'])
        acao.preco_medio = float(request.form['preco_medio'].replace(',', '.'))
        db.session.commit()
        flash('Ação atualizada com sucesso!')
        return redirect(url_for('detalhes_carteira', carteira_id=acao.carteira_id))
    return render_template('editar_acao.html', acao=acao)

@app.route('/carteira/excluir/<int:carteira_id>')
def excluir_carteira(carteira_id):
    carteira = Carteira.query.get_or_404(carteira_id)
    db.session.delete(carteira)
    db.session.commit()
    flash('Carteira excluída com sucesso!')
    return redirect(url_for('index'))

@app.route('/acao/excluir/<int:acao_id>')
def excluir_acao(acao_id):
    acao = Acao.query.get_or_404(acao_id)
    carteira_id = acao.carteira_id
    db.session.delete(acao)
    db.session.commit()
    flash('Ação excluída com sucesso!')
    return redirect(url_for('detalhes_carteira', carteira_id=carteira_id))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Garante que o banco de dados será criado
    app.run(debug=True)