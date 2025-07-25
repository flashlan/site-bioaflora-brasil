from flask import Flask, render_template, request, flash, redirect, url_for, Response, jsonify
import os
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import re
import json
import hashlib
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Disponibilizar get_env_value para templates
@app.context_processor
def inject_env_function():
    return dict(get_env_value=get_env_value)

# Configurações Admin
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'bioaflora2024')

# Sistema de gerenciamento do arquivo .env
ENV_FILE = '.env'

def load_env_config():
    """Carregar configurações do arquivo .env"""
    config = {}
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    config[key.strip()] = value.strip().strip('"\'')
    return config

def save_env_config(config):
    """Salvar configurações no arquivo .env"""
    try:
        with open(ENV_FILE, 'w', encoding='utf-8') as f:
            f.write('# Configurações do Bio Aflora Brasil - Agronanobio\n')
            f.write('# Gerado automaticamente pelo Dashboard Admin\n\n')
            
            f.write('# Email Configuration\n')
            f.write(f'EMAIL_PASSWORD={config.get("EMAIL_PASSWORD", "")}\n')
            f.write(f'EMAIL_REMETENTE={config.get("EMAIL_REMETENTE", "contato@bioaflora.com.br")}\n')
            f.write(f'EMAIL_DESTINO={config.get("EMAIL_DESTINO", "contato@bioaflora.com.br")}\n')
            f.write(f'SMTP_SERVER={config.get("SMTP_SERVER", "smtp.gmail.com")}\n')
            f.write(f'SMTP_PORT={config.get("SMTP_PORT", "587")}\n\n')
            
            f.write('# Analytics Configuration\n')
            f.write(f'GA4_MEASUREMENT_ID={config.get("GA4_MEASUREMENT_ID", "GA4-BIOAFLORA")}\n')
            f.write(f'GTM_CONTAINER_ID={config.get("GTM_CONTAINER_ID", "GTM-BIOAFLORA")}\n\n')
            
            f.write('# Admin Configuration\n')
            f.write(f'ADMIN_USERNAME={config.get("ADMIN_USERNAME", "admin")}\n')
            f.write(f'ADMIN_PASSWORD={config.get("ADMIN_PASSWORD", "bioaflora2024")}\n\n')
            
            f.write('# Site Configuration\n')
            f.write(f'SECRET_KEY={config.get("SECRET_KEY", "your-secret-key-here")}\n')
            f.write(f'SITE_URL={config.get("SITE_URL", "https://bioaflora.com.br")}\n')
        return True
    except Exception as e:
        print(f"Erro ao salvar .env: {e}")
        return False

def get_env_value(key, default=''):
    """Obter valor do ambiente ou .env"""
    # Primeiro tenta do sistema
    value = os.environ.get(key)
    if value:
        return value
    
    # Depois tenta do arquivo .env
    config = load_env_config()
    return config.get(key, default)

# Autenticação Admin
def require_admin_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in request.form and 'admin_logged_in' not in request.args:
            # Verificar se já está logado na sessão
            if 'admin_authenticated' in request.cookies:
                return f(*args, **kwargs)
                
            # Verificar credenciais básicas
            auth = request.authorization
            if not auth or auth.username != get_env_value('ADMIN_USERNAME', ADMIN_USERNAME) or auth.password != get_env_value('ADMIN_PASSWORD', ADMIN_PASSWORD):
                return Response('Acesso restrito ao dashboard admin', 401, {'WWW-Authenticate': 'Basic realm="Admin Dashboard"'})
        return f(*args, **kwargs)
    return decorated_function

# Configurações de Email (agora usando .env)
def get_email_config():
    return {
        'SMTP_SERVER': get_env_value('SMTP_SERVER', 'smtp.gmail.com'),
        'SMTP_PORT': int(get_env_value('SMTP_PORT', '587')),
        'EMAIL_REMETENTE': get_env_value('EMAIL_REMETENTE', 'contato@bioaflora.com.br'),
        'SENHA_EMAIL': get_env_value('EMAIL_PASSWORD', ''),
        'EMAIL_DESTINO': get_env_value('EMAIL_DESTINO', 'contato@bioaflora.com.br')
    }

EMAIL_CONFIG = get_email_config()

def validar_email(email):
    """Validar formato do email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validar_campos_contato(nome, email, mensagem):
    """Validar campos do formulário de contato"""
    errors = []
    
    if not nome or len(nome.strip()) < 2:
        errors.append('Nome deve ter pelo menos 2 caracteres')
    
    if not email or not validar_email(email):
        errors.append('Email inválido')
    
    if not mensagem or len(mensagem.strip()) < 10:
        errors.append('Mensagem deve ter pelo menos 10 caracteres')
    
    return errors

def enviar_email_contato(nome, email, assunto, mensagem):
    """Enviar email de contato"""
    try:
        # Obter configuração atual
        email_config = get_email_config()
        
        # Criar mensagem
        msg = MIMEMultipart()
        msg['From'] = email_config['EMAIL_REMETENTE']
        msg['To'] = email_config['EMAIL_DESTINO']
        msg['Subject'] = f'[Agronanobio] Contato: {assunto or "Sem assunto"} - {nome}'
        
        # Corpo do email em HTML
        corpo_html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; padding: 20px; border-radius: 10px 10px 0 0;">
                    <h2 style="margin: 0;">🌿 Nova mensagem do site Agronanobio</h2>
                    <p style="margin: 5px 0 0 0; opacity: 0.9;">Projeto Bio Aflora</p>
                </div>
                
                <div style="background: #f9fafb; padding: 20px; border: 1px solid #e5e7eb;">
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr>
                            <td style="padding: 10px; font-weight: bold; background: #e5e7eb; width: 120px;">👤 Nome:</td>
                            <td style="padding: 10px; background: white;">{nome}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; font-weight: bold; background: #e5e7eb;">📧 Email:</td>
                            <td style="padding: 10px; background: white;"><a href="mailto:{email}">{email}</a></td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; font-weight: bold; background: #e5e7eb;">📋 Assunto:</td>
                            <td style="padding: 10px; background: white;">{assunto or "Não informado"}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; font-weight: bold; background: #e5e7eb; vertical-align: top;">💬 Mensagem:</td>
                            <td style="padding: 10px; background: white;">{mensagem.replace(chr(10), '<br>')}</td>
                        </tr>
                    </table>
                </div>
                
                <div style="background: #10b981; color: white; padding: 15px; border-radius: 0 0 10px 10px; text-align: center;">
                    <p style="margin: 0; font-size: 14px;">
                        📍 Vicina 11, Linha Esperança, 1954 - Serra do Tigre, Mallet-PR<br>
                        📞 (42) 99957-5280 | 🌐 bioaflora.com.br
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(corpo_html, 'html'))
        
        # Enviar email (apenas se tiver senha configurada)
        if email_config['SENHA_EMAIL']:
            server = smtplib.SMTP(email_config['SMTP_SERVER'], email_config['SMTP_PORT'])
            server.starttls()
            server.login(email_config['EMAIL_REMETENTE'], email_config['SENHA_EMAIL'])
            server.send_message(msg)
            server.quit()
            return True, "Email enviado com sucesso!"
        else:
            # Modo de desenvolvimento - apenas simular
            print("=" * 50)
            print("EMAIL SIMULADO (Configure EMAIL_PASSWORD para envio real)")
            print("=" * 50)
            print(f"De: {email_config['EMAIL_REMETENTE']}")
            print(f"Para: {email_config['EMAIL_DESTINO']}")
            print(f"Assunto: {msg['Subject']}")
            print(f"Nome: {nome}")
            print(f"Email: {email}")
            print(f"Mensagem: {mensagem}")
            print("=" * 50)
            return True, "Mensagem recebida com sucesso! (Modo desenvolvimento)"
            
    except Exception as e:
        print(f"Erro ao enviar email: {e}")
        return False, f"Erro ao enviar mensagem: {str(e)}"

# Sistema de Newsletter
NEWSLETTER_FILE = 'newsletter_subscribers.json'

def carregar_newsletter():
    """Carregar lista de inscritos da newsletter"""
    try:
        if os.path.exists(NEWSLETTER_FILE):
            with open(NEWSLETTER_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    except Exception as e:
        print(f"Erro ao carregar newsletter: {e}")
        return []

def salvar_newsletter(subscribers):
    """Salvar lista de inscritos da newsletter"""
    try:
        with open(NEWSLETTER_FILE, 'w', encoding='utf-8') as f:
            json.dump(subscribers, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Erro ao salvar newsletter: {e}")
        return False

def gerar_token_unsubscribe(email):
    """Gerar token para descadastro"""
    return hashlib.md5(f"{email}_{app.secret_key}".encode()).hexdigest()

def email_ja_cadastrado(email):
    """Verificar se email já está cadastrado"""
    subscribers = carregar_newsletter()
    return any(sub['email'].lower() == email.lower() for sub in subscribers)

def cadastrar_newsletter(email):
    """Cadastrar email na newsletter"""
    if email_ja_cadastrado(email):
        return False, "Email já cadastrado na newsletter"
    
    subscribers = carregar_newsletter()
    novo_subscriber = {
        'email': email.lower(),
        'data_cadastro': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'ativo': True,
        'token_unsubscribe': gerar_token_unsubscribe(email)
    }
    
    subscribers.append(novo_subscriber)
    
    if salvar_newsletter(subscribers):
        return True, "Email cadastrado com sucesso!"
    else:
        return False, "Erro ao salvar cadastro"

def enviar_email_confirmacao_newsletter(email):
    """Enviar email de confirmação da newsletter"""
    try:
        # Obter configuração atual
        email_config = get_email_config()
        site_url = get_env_value('SITE_URL', 'https://bioaflora.com.br')
        
        token = gerar_token_unsubscribe(email)
        unsubscribe_url = f"{site_url}/newsletter/descadastrar?email={email}&token={token}"
        
        msg = MIMEMultipart()
        msg['From'] = email_config['EMAIL_REMETENTE']
        msg['To'] = email
        msg['Subject'] = '🌿 Bem-vindo à Newsletter da Agronanobio!'
        
        corpo_html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1 style="margin: 0; font-size: 28px;">🌿 Agronanobio</h1>
                <p style="margin: 10px 0 0 0; opacity: 0.9; font-size: 16px;">Projeto Bio Aflora</p>
            </div>
            
            <div style="background: #f9fafb; padding: 30px; border: 1px solid #e5e7eb;">
                <h2 style="color: #10b981; margin-top: 0;">Obrigado por se inscrever!</h2>
                
                <p style="font-size: 16px; margin: 20px 0;">
                    Seja bem-vindo à nossa newsletter! Você receberá conteúdos exclusivos sobre:
                </p>
                
                <ul style="color: #4b5563; font-size: 15px; padding-left: 20px;">
                    <li style="margin: 8px 0;">🌱 <strong>Sustentabilidade</strong> e práticas agroecológicas</li>
                    <li style="margin: 8px 0;">🧉 <strong>Erva-mate nativa</strong> e seus benefícios</li>
                    <li style="margin: 8px 0;">🔬 <strong>Inovações biotecnológicas</strong> na agricultura</li>
                    <li style="margin: 8px 0;">📍 <strong>Novidades da URT</strong> em Mallet-PR</li>
                    <li style="margin: 8px 0;">🤝 <strong>Oportunidades de parceria</strong> e colaboração</li>
                </ul>
                
                <div style="background: white; padding: 20px; margin: 25px 0; border-left: 4px solid #10b981; border-radius: 5px;">
                    <h3 style="color: #10b981; margin-top: 0;">🎯 Nossa Missão</h3>
                    <p style="margin: 0; color: #6b7280;">
                        Desenvolver sistemas agroflorestas com erva-mate nativa, criando a 
                        <strong>Unidade de Referência Tecnológica (URT)</strong> em Mallet-PR, 
                        focando na implantação de produção orgânica sustentável.
                    </p>
                </div>
                
                <p style="text-align: center; margin: 30px 0;">
                    <strong style="color: #10b981;">Frequência:</strong> Enviaremos conteúdos 1-2 vezes por mês<br>
                    <strong style="color: #10b981;">Qualidade:</strong> Apenas conteúdo relevante, sem spam
                </p>
            </div>
            
            <div style="background: #10b981; color: white; padding: 20px; border-radius: 0 0 10px 10px;">
                <div style="text-align: center; margin-bottom: 15px;">
                    <h3 style="margin: 0; font-size: 18px;">📞 Fale Conosco</h3>
                </div>
                <div style="display: flex; justify-content: space-around; flex-wrap: wrap; gap: 10px; font-size: 14px;">
                    <div>📧 contato@bioaflora.com.br</div>
                    <div>📞 (42) 99957-5280</div>
                    <div>🌐 bioaflora.com.br</div>
                </div>
                <div style="text-align: center; margin-top: 15px; font-size: 13px; opacity: 0.8;">
                    📍 Vicina 11, Linha Esperança, 1954 - Serra do Tigre, Mallet-PR
                </div>
                
                <hr style="border: none; border-top: 1px solid rgba(255,255,255,0.3); margin: 20px 0;">
                
                <div style="text-align: center; font-size: 12px; opacity: 0.7;">
                    <p style="margin: 5px 0;">Você está recebendo este email porque se inscreveu em nossa newsletter.</p>
                    <p style="margin: 5px 0;">
                        Para se descadastrar, <a href="{unsubscribe_url}" style="color: #fbbf24; text-decoration: underline;">clique aqui</a>
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(corpo_html, 'html'))
        
        # Enviar email (apenas se tiver senha configurada)
        if email_config['SENHA_EMAIL']:
            server = smtplib.SMTP(email_config['SMTP_SERVER'], email_config['SMTP_PORT'])
            server.starttls()
            server.login(email_config['EMAIL_REMETENTE'], email_config['SENHA_EMAIL'])
            server.send_message(msg)
            server.quit()
            return True, "Email de confirmação enviado!"
        else:
            # Modo desenvolvimento
            print("=" * 50)
            print("EMAIL DE CONFIRMAÇÃO NEWSLETTER (SIMULADO)")
            print("=" * 50)
            print(f"Para: {email}")
            print(f"Assunto: {msg['Subject']}")
            print(f"URL Descadastro: {unsubscribe_url}")
            print("=" * 50)
            return True, "Inscrição confirmada! (Modo desenvolvimento)"
            
    except Exception as e:
        print(f"Erro ao enviar email de confirmação: {e}")
        return False, f"Erro ao enviar confirmação: {str(e)}"

@app.route('/')
def inicio():
    return render_template('inicio.html')

@app.route('/saiba-mais')
def saiba_mais():
    return render_template('saiba_mais.html')

@app.route('/contato', methods=['GET', 'POST'])
def contato():
    if request.method == 'POST':
        # Obter dados do formulário
        nome = request.form.get('nome', '').strip()
        email = request.form.get('email', '').strip()
        assunto = request.form.get('assunto', '').strip()
        mensagem = request.form.get('mensagem', '').strip()
        
        # Validar campos obrigatórios
        errors = validar_campos_contato(nome, email, mensagem)
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('contato.html', 
                                 nome=nome, email=email, 
                                 assunto=assunto, mensagem=mensagem)
        
        # Tentar enviar email
        sucesso, mensagem_resultado = enviar_email_contato(nome, email, assunto, mensagem)
        
        if sucesso:
            flash(f'✅ {mensagem_resultado}', 'success')
            return redirect(url_for('contato'))
        else:
            flash(f'❌ {mensagem_resultado}', 'error')
            return render_template('contato.html', 
                                 nome=nome, email=email, 
                                 assunto=assunto, mensagem=mensagem)
    
    return render_template('contato.html')

@app.route('/sobre-nos')
def sobre_nos():
    return render_template('sobre_nos.html')

@app.route('/newsletter/cadastrar', methods=['POST'])
def newsletter_cadastrar():
    """Rota para cadastrar na newsletter"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        
        # Validar email
        if not email or not validar_email(email):
            return {'success': False, 'message': 'Email inválido'}, 400
        
        # Tentar cadastrar
        sucesso, mensagem = cadastrar_newsletter(email)
        
        if sucesso:
            # Enviar email de confirmação
            sucesso_email, mensagem_email = enviar_email_confirmacao_newsletter(email)
            
            if sucesso_email:
                return {'success': True, 'message': f'✅ {mensagem} Email de confirmação enviado!'}, 200
            else:
                return {'success': True, 'message': f'✅ {mensagem} {mensagem_email}'}, 200
        else:
            return {'success': False, 'message': f'❌ {mensagem}'}, 400

@app.route('/newsletter/descadastrar')
def newsletter_descadastrar():
    """Rota para descadastrar da newsletter"""
    email = request.args.get('email', '')
    token = request.args.get('token', '')
    
    if not email or not token:
        flash('Link de descadastro inválido', 'error')
        return redirect(url_for('inicio'))
    
    # Verificar token
    token_esperado = gerar_token_unsubscribe(email)
    if token != token_esperado:
        flash('Link de descadastro inválido', 'error')
        return redirect(url_for('inicio'))
    
    # Remover da lista
    subscribers = carregar_newsletter()
    subscribers_atualizados = [s for s in subscribers if s['email'].lower() != email.lower()]
    
    if len(subscribers_atualizados) < len(subscribers):
        if salvar_newsletter(subscribers_atualizados):
            flash(f'✅ Email {email} removido da newsletter com sucesso!', 'success')
        else:
            flash('❌ Erro ao processar descadastro', 'error')
    else:
        flash('Email não encontrado na lista', 'info')
    
    return redirect(url_for('inicio'))

@app.route('/newsletter/stats')
def newsletter_stats():
    """Visualizar estatísticas da newsletter (admin)"""
    subscribers = carregar_newsletter()
    ativos = [s for s in subscribers if s.get('ativo', True)]
    
    stats = {
        'total': len(subscribers),
        'ativos': len(ativos),
        'recentes': len([s for s in ativos if 
                        datetime.strptime(s['data_cadastro'], '%Y-%m-%d %H:%M:%S') > 
                        datetime.now().replace(day=1)]),
        'subscribers': ativos[-10:]  # Últimos 10
    }
    
    return f"""
    <h2>📊 Estatísticas da Newsletter</h2>
    <p><strong>Total de inscritos:</strong> {stats['total']}</p>
    <p><strong>Inscritos ativos:</strong> {stats['ativos']}</p>
    <p><strong>Novos este mês:</strong> {stats['recentes']}</p>
    
    <h3>Últimos 10 inscritos:</h3>
    <ul>
    {''.join([f"<li>{s['email']} - {s['data_cadastro']}</li>" for s in stats['subscribers']])}
    </ul>
    
    <p><a href="/">← Voltar ao site</a></p>
    """

# Blog posts data
BLOG_POSTS = {
    'preservacao-mata-atlantica': {
        'title': 'A Importância da Preservação da Mata Atlântica para a Erva-Mate',
        'date': '20 de Janeiro, 2024',
        'category': 'Sustentabilidade',
        'author': 'Bio Aflora Brasil',
        'excerpt': 'Descubra como a preservação da Mata Atlântica é fundamental para manter a qualidade e sustentabilidade da erva-mate.',
        'featured': True
    },
    'cultivo-organico': {
        'title': 'Cultivo Orgânico: O Futuro da Erva-Mate',
        'date': '15 de Janeiro, 2024',
        'category': 'Sustentabilidade',
        'author': 'Bio Aflora Brasil',
        'excerpt': 'Técnicas sustentáveis que utilizamos para minimizar o impacto no meio ambiente durante o cultivo.'
    },
    'beneficios-nutricionais': {
        'title': 'Os Benefícios Nutricionais da Erva-Mate',
        'date': '16 de Janeiro, 2024',
        'category': 'Erva-Mate',
        'author': 'Bio Aflora Brasil',
        'excerpt': 'Descubra as propriedades nutritivas e benefícios para a saúde da Ilex paraguariensis.'
    },
    'reflorestamento': {
        'title': 'Reflorestamento: Nossa Contribuição',
        'date': '14 de Janeiro, 2024',
        'category': 'Meio Ambiente',
        'author': 'Bio Aflora Brasil',
        'excerpt': 'Conheça nossos projetos de reflorestamento e recuperação de áreas degradadas.'
    },
    'inovacoes-processamento': {
        'title': 'Inovações no Processamento Sustentável',
        'date': '12 de Janeiro, 2024',
        'category': 'Pesquisa',
        'author': 'Bio Aflora Brasil',
        'excerpt': 'Novas tecnologias que aplicamos para processar erva-mate de forma mais sustentável.'
    },
    'apoio-familias': {
        'title': 'Apoio às Famílias Produtoras',
        'date': '10 de Janeiro, 2024',
        'category': 'Comunidade',
        'author': 'Bio Aflora Brasil',
        'excerpt': 'Como trabalhamos em parceria com famílias locais para fortalecer a comunidade.'
    },
    'relatorio-sustentabilidade': {
        'title': 'Relatório de Sustentabilidade 2023',
        'date': '08 de Janeiro, 2024',
        'category': 'Sustentabilidade',
        'author': 'Bio Aflora Brasil',
        'excerpt': 'Confira nossos resultados e metas alcançadas em sustentabilidade durante 2023.'
    }
}

@app.route('/blog')
def blog():
    return render_template('blog.html', posts=BLOG_POSTS)

@app.route('/blog/<slug>')
def blog_post(slug):
    if slug not in BLOG_POSTS:
        return render_template('404.html'), 404
    
    post = BLOG_POSTS[slug]
    post['slug'] = slug
    
    # Get next and previous posts
    post_keys = list(BLOG_POSTS.keys())
    current_index = post_keys.index(slug)
    
    next_post = None
    prev_post = None
    
    if current_index < len(post_keys) - 1:
        next_key = post_keys[current_index + 1]
        next_post = {
            'slug': next_key,
            'title': BLOG_POSTS[next_key]['title']
        }
    
    if current_index > 0:
        prev_key = post_keys[current_index - 1]
        prev_post = {
            'slug': prev_key,
            'title': BLOG_POSTS[prev_key]['title']
        }
    
    return render_template('blog_post.html', post=post, next_post=next_post, prev_post=prev_post)

@app.route('/sitemap.xml')
def sitemap():
    """Generate XML sitemap for SEO"""
    base_url = 'https://bioaflora.com.br'
    urls = [
        {'loc': f'{base_url}{url_for("inicio")}', 'priority': '1.0', 'changefreq': 'weekly'},
        {'loc': f'{base_url}{url_for("saiba_mais")}', 'priority': '0.8', 'changefreq': 'monthly'},
        {'loc': f'{base_url}{url_for("contato")}', 'priority': '0.7', 'changefreq': 'monthly'},
        {'loc': f'{base_url}{url_for("sobre_nos")}', 'priority': '0.6', 'changefreq': 'monthly'},
        {'loc': f'{base_url}{url_for("blog")}', 'priority': '0.9', 'changefreq': 'weekly'},
    ]
    
    # Add blog posts to sitemap
    for slug in BLOG_POSTS.keys():
        urls.append({
            'loc': f'{base_url}{url_for("blog_post", slug=slug)}',
            'priority': '0.8',
            'changefreq': 'monthly'
        })
    
    sitemap_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
'''
    
    for url in urls:
        sitemap_xml += f'''    <url>
        <loc>{url['loc']}</loc>
        <lastmod>{datetime.now().strftime('%Y-%m-%d')}</lastmod>
        <changefreq>{url['changefreq']}</changefreq>
        <priority>{url['priority']}</priority>
    </url>
'''
    
    sitemap_xml += '</urlset>'
    
    return Response(sitemap_xml, mimetype='application/xml')

@app.route('/robots.txt')
def robots():
    """Generate robots.txt for SEO"""
    robots_txt = '''User-agent: *
Allow: /
Disallow: /admin/
Disallow: /private/

Sitemap: https://bioaflora.com.br/sitemap.xml

# Google
User-agent: Googlebot
Allow: /

# Bing
User-agent: Bingbot
Allow: /

# Crawl-delay for all bots
Crawl-delay: 1
'''
    return Response(robots_txt, mimetype='text/plain')

# ===============================
# DASHBOARD ADMIN
# ===============================

@app.route('/admin')
@require_admin_auth
def admin_dashboard():
    """Dashboard administrativo principal"""
    # Estatísticas gerais
    newsletter_stats = carregar_newsletter()
    env_config = load_env_config()
    
    stats = {
        'newsletter_total': len(newsletter_stats),
        'newsletter_ativos': len([s for s in newsletter_stats if s.get('ativo', True)]),
        'env_configured': len(env_config) > 0,
        'email_configured': bool(get_env_value('EMAIL_PASSWORD')),
        'analytics_configured': get_env_value('GA4_MEASUREMENT_ID') != 'GA4-BIOAFLORA'
    }
    
    return render_template('admin/dashboard.html', stats=stats, config=env_config)

@app.route('/admin/settings', methods=['GET', 'POST'])
@require_admin_auth
def admin_settings():
    """Configurações do sistema"""
    if request.method == 'POST':
        # Obter configuração atual
        config = load_env_config()
        
        # Atualizar com novos valores
        config.update({
            'EMAIL_PASSWORD': request.form.get('email_password', ''),
            'EMAIL_REMETENTE': request.form.get('email_remetente', ''),
            'EMAIL_DESTINO': request.form.get('email_destino', ''),
            'SMTP_SERVER': request.form.get('smtp_server', ''),
            'SMTP_PORT': request.form.get('smtp_port', ''),
            'GA4_MEASUREMENT_ID': request.form.get('ga4_id', ''),
            'GTM_CONTAINER_ID': request.form.get('gtm_id', ''),
            'ADMIN_USERNAME': request.form.get('admin_username', ''),
            'ADMIN_PASSWORD': request.form.get('admin_password', ''),
            'SECRET_KEY': request.form.get('secret_key', ''),
            'SITE_URL': request.form.get('site_url', '')
        })
        
        # Salvar configurações
        if save_env_config(config):
            flash('✅ Configurações salvas com sucesso!', 'success')
            
            # Atualizar EMAIL_CONFIG na memória
            global EMAIL_CONFIG
            EMAIL_CONFIG = get_email_config()
        else:
            flash('❌ Erro ao salvar configurações', 'error')
        
        return redirect(url_for('admin_settings'))
    
    # GET - mostrar formulário
    config = load_env_config()
    return render_template('admin/settings.html', config=config)

@app.route('/admin/newsletter')
@require_admin_auth
def admin_newsletter():
    """Gerenciamento da newsletter"""
    subscribers = carregar_newsletter()
    
    # Estatísticas detalhadas
    stats = {
        'total': len(subscribers),
        'ativos': len([s for s in subscribers if s.get('ativo', True)]),
        'este_mes': len([s for s in subscribers if 
                        datetime.strptime(s['data_cadastro'], '%Y-%m-%d %H:%M:%S').month == datetime.now().month]),
        'dominios': {}
    }
    
    # Análise de domínios
    for sub in subscribers:
        if sub.get('ativo', True):
            domain = sub['email'].split('@')[1] if '@' in sub['email'] else 'unknown'
            stats['dominios'][domain] = stats['dominios'].get(domain, 0) + 1
    
    # Ordenar por data (mais recente primeiro)
    subscribers.sort(key=lambda x: x['data_cadastro'], reverse=True)
    
    return render_template('admin/newsletter.html', subscribers=subscribers, stats=stats)

@app.route('/admin/newsletter/export')
@require_admin_auth
def admin_newsletter_export():
    """Exportar lista de newsletter em CSV"""
    subscribers = carregar_newsletter()
    
    # Criar CSV
    csv_content = "Email,Data Cadastro,Ativo,Dominio\n"
    for sub in subscribers:
        domain = sub['email'].split('@')[1] if '@' in sub['email'] else 'unknown'
        csv_content += f"{sub['email']},{sub['data_cadastro']},{sub.get('ativo', True)},{domain}\n"
    
    response = Response(csv_content, mimetype='text/csv')
    response.headers['Content-Disposition'] = f'attachment; filename=newsletter_subscribers_{datetime.now().strftime("%Y%m%d")}.csv'
    return response

@app.route('/admin/test-email', methods=['POST'])
@require_admin_auth
def admin_test_email():
    """Testar configuração de email"""
    email_destino = request.form.get('email_teste', get_env_value('EMAIL_DESTINO'))
    
    try:
        # Tentar enviar email de teste
        sucesso, mensagem = enviar_email_contato(
            "Sistema Admin", 
            "admin@bioaflora.com.br",
            "Teste de Configuração", 
            "Este é um email de teste enviado pelo dashboard administrativo para verificar se as configurações de email estão funcionando corretamente."
        )
        
        if sucesso:
            return jsonify({'success': True, 'message': f'✅ {mensagem}'})
        else:
            return jsonify({'success': False, 'message': f'❌ {mensagem}'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'❌ Erro: {str(e)}'})

@app.route('/admin/system-info')
@require_admin_auth
def admin_system_info():
    """Informações do sistema"""
    import sys
    import platform
    
    info = {
        'python_version': sys.version,
        'platform': platform.platform(),
        'flask_env': os.environ.get('FLASK_ENV', 'production'),
        'env_file_exists': os.path.exists('.env'),
        'env_vars': len(load_env_config()),
        'newsletter_file_exists': os.path.exists(NEWSLETTER_FILE),
        'disk_space': 'N/A'  # Simplificado
    }
    
    return render_template('admin/system_info.html', info=info)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)