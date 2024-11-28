from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
import random
import string
from sqlalchemy import text  # Importando o método text

# Inicializando o app
app = Flask(__name__)

# Configuração do Banco de Dados
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///credentials.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modelo para armazenar as credenciais no banco de dados
class Credenciais(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    primeiro_nome = db.Column(db.String(50), nullable=False)
    ultimo_nome = db.Column(db.String(50), nullable=False)
    email_gerado = db.Column(db.String(100), nullable=False)
    senha_gerada = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f'<Credenciais {self.email_gerado}>'

# Função para gerar a senha aleatória
def gerar_senha(tamanho=12):
    caracteres = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(caracteres) for i in range(tamanho))

# Página principal (formulário)
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        primeiro_nome = request.form['primeiro_nome']
        ultimo_nome = request.form['ultimo_nome']

        # Garantir que a primeira letra de cada nome seja maiúscula
        primeiro_nome = primeiro_nome.strip().capitalize()  # Strip para remover espaços em excesso e capitalize para a primeira letra
        ultimo_nome = ultimo_nome.strip().capitalize()  # Faz o mesmo para o último nome

        # Gerando o email corporativo e senha
        email_gerado = f'{primeiro_nome.lower()}.{ultimo_nome.lower()}@jacintolela.io'
        senha_gerada = gerar_senha()

        # Hashing da senha antes de armazenar
        senha_hash = generate_password_hash(senha_gerada)

        # Salvando as credenciais no banco de dados
        nova_credencial = Credenciais(
            primeiro_nome=primeiro_nome,
            ultimo_nome=ultimo_nome,
            email_gerado=email_gerado,
            senha_gerada=senha_hash
        )
        db.session.add(nova_credencial)
        db.session.commit()

        # Exibindo uma mensagem de sucesso no frontend
        mensagem_sucesso = f"Seu email foi criado com sucesso: {email_gerado}. Verifique sua caixa de entrada para mais informações."
        return render_template('index.html', mensagem_sucesso=mensagem_sucesso)

    return render_template('index.html')

# Nova Rota para listar as credenciais com filtros
@app.route('/credenciais', methods=['GET'])
def listar_credenciais():
    order = request.args.get('order', 'asc')  # Pega o parâmetro 'order' da URL
    search = request.args.get('search', '').lower()  # Pega a letra para pesquisa (se houver)

    query = Credenciais.query

    # Ordenação por data
    if order == 'asc':
        query = query.order_by(Credenciais.id.asc())  # Antigo para Novo
    elif order == 'desc':
        query = query.order_by(Credenciais.id.desc())  # Novo para Antigo

    # Pesquisa por letra (primeiro nome ou último nome)
    if search:
        query = query.filter(
            (Credenciais.primeiro_nome.ilike(f'{search}%')) | 
            (Credenciais.ultimo_nome.ilike(f'{search}%'))
        )

    credenciais = query.all()  # Executa a query e pega os resultados

    return render_template('listar_credenciais.html', credenciais=credenciais)

# Executando a aplicação
if __name__ == '__main__':
    with app.app_context():
        # Remover a tabela antiga (caso ela exista)
        db.session.execute(text('DROP TABLE IF EXISTS credenciais'))  # Usando 'text' para SQL
        db.session.commit()  # Confirmar as alterações no banco de dados
        # Criar as novas tabelas
        db.create_all()

    app.run(debug=True)
