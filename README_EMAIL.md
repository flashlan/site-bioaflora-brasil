# 📧 Configuração do Sistema de Email

## Como ativar o envio de emails

### 1. Configurar Email Gmail (Recomendado)

1. **Criar uma conta Gmail** (se não tiver):
   - `contato@bioaflora.com.br` ou usar conta existente

2. **Ativar verificação em duas etapas**:
   - Acesse: https://myaccount.google.com/security
   - Ative "Verificação em duas etapas"

3. **Gerar senha de app**:
   - Acesse: https://myaccount.google.com/apppasswords
   - Gere uma senha para "Mail"
   - **Copie a senha gerada** (16 caracteres)

### 2. Configurar Variável de Ambiente

**Windows:**
```bash
set EMAIL_PASSWORD=sua_senha_de_app_aqui
python app.py
```

**Linux/Mac:**
```bash
export EMAIL_PASSWORD=sua_senha_de_app_aqui
python app.py
```

**Ou criar arquivo `.env`:**
```env
EMAIL_PASSWORD=sua_senha_de_app_aqui
```

### 3. Configurar Email Personalizado

Se usar email próprio (ex: `contato@bioaflora.com.br`), edite em `app.py`:

```python
EMAIL_CONFIG = {
    'SMTP_SERVER': 'smtp.seuservidor.com.br',  # Servidor SMTP
    'SMTP_PORT': 587,                          # Porta (587 ou 465)
    'EMAIL_REMETENTE': 'contato@bioaflora.com.br',
    'SENHA_EMAIL': os.environ.get('EMAIL_PASSWORD', ''),
    'EMAIL_DESTINO': 'contato@bioaflora.com.br'
}
```

## 🧪 Modo de Desenvolvimento

Sem configurar `EMAIL_PASSWORD`, o sistema:
- ✅ Mostra emails no console
- ✅ Confirma recebimento ao usuário  
- ❌ Não envia email real

## 🚀 Modo de Produção

Com `EMAIL_PASSWORD` configurado:
- ✅ Envia emails reais via SMTP
- ✅ Emails HTML formatados
- ✅ Validações completas

## 📋 Funcionalidades Implementadas

### ✅ Validações
- Nome mínimo 2 caracteres
- Email válido
- Mensagem mínimo 10 caracteres
- Checkbox de privacidade obrigatório

### ✅ UX Melhorada
- Loading durante envio
- Contador de caracteres
- Auto-resize do textarea
- Manter dados em caso de erro
- Feedback visual de erros/sucesso

### ✅ Email HTML
- Design profissional
- Logo e cores da marca
- Informações completas do contato
- Dados da empresa no rodapé

## 🛡️ Segurança

- ✅ Validação server-side e client-side
- ✅ Escape de caracteres perigosos
- ✅ Rate limiting (implementar se necessário)
- ✅ Checkbox de consentimento LGPD

## 📞 Teste Rápido

1. Acesse: http://localhost:5000/contato
2. Preencha o formulário
3. Verifique o console se estiver em modo desenvolvimento
4. Ou verifique o email se estiver configurado

## 🔧 Troubleshooting

### Erro "Authentication failed"
- Verifique se ativou verificação em duas etapas
- Use senha de app, não senha da conta
- Teste com Gmail primeiro

### Erro "SMTP timeout"
- Verifique conexão com internet
- Teste porta 465 em vez de 587
- Verifique firewall

### Formulário não envia
- Abra console do navegador (F12)
- Verifique mensagens de erro
- Confirme JavaScript habilitado

## 📈 Próximas Melhorias

- [ ] Rate limiting anti-spam
- [ ] reCAPTCHA
- [ ] Banco de dados para logs
- [ ] Template de resposta automática
- [ ] Dashboard de mensagens