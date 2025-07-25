# Configuração de Email - Exemplo para implementação futura

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def enviar_email(nome, email, mensagem):
    """
    Função para enviar email real - implementação futura
    """
    # Configurações do servidor SMTP (exemplo Gmail)
    SMTP_SERVER = 'smtp.gmail.com'
    SMTP_PORT = 587
    EMAIL_REMETENTE = 'contato@bioaflora.com.br'
    SENHA_EMAIL = 'sua-senha-app'  # Use App Password do Gmail
    
    # Criar mensagem
    msg = MIMEMultipart()
    msg['From'] = EMAIL_REMETENTE
    msg['To'] = EMAIL_REMETENTE  # Recebe no próprio email da empresa
    msg['Subject'] = f'Contato do Site - {nome}'
    
    # Corpo do email
    corpo = f"""
    Nova mensagem do site Agronanobio - Projeto Bio Aflora:
    
    Nome: {nome}
    Email: {email}
    
    Mensagem:
    {mensagem}
    """
    
    msg.attach(MIMEText(corpo, 'plain'))
    
    try:
        # Conectar ao servidor
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_REMETENTE, SENHA_EMAIL)
        
        # Enviar email
        server.send_message(msg)
        server.quit()
        
        return True
    except Exception as e:
        print(f"Erro ao enviar email: {e}")
        return False

# Para integrar no app.py, substitua a linha 23 por:
# if enviar_email(nome, email, mensagem):
#     flash('Mensagem enviada com sucesso! Entraremos em contato em breve.', 'success')
# else:
#     flash('Erro ao enviar mensagem. Tente novamente.', 'error')