# Bio Aflora Brasil - Website

Website institucional da Bio Aflora Brasil, empresa especializada em produtos de erva-mate sustentáveis.

## Sobre o Projeto

Site desenvolvido em Python Flask com foco em sustentabilidade e produtos de erva-mate (Ilex paraguariensis):
- Chá-mate premium
- Erva para chimarrão
- Ervas com sabores naturais

## Funcionalidades

- **Início**: Apresentação da empresa e produtos principais
- **Saiba Mais**: Informações detalhadas sobre erva-mate e sustentabilidade
- **Contato**: Formulário de contato e informações de localização
- **Sobre Nós**: História, missão, visão e valores da empresa

## Tecnologias Utilizadas

- **Backend**: Python Flask 2.3.3
- **Frontend**: HTML5, CSS3, Bootstrap 5.1.3
- **Responsivo**: Design adaptável para desktop e mobile

## Como Executar

1. Instalar dependências:
```bash
pip install -r requirements.txt
```

2. Executar o servidor:
```bash
python app.py
```

3. Acessar no navegador:
```
http://localhost:5000
```

## Estrutura do Projeto

```
site_bioaflora/
├── app.py                 # Aplicação Flask principal
├── requirements.txt       # Dependências Python
├── templates/            # Templates HTML
│   ├── base.html         # Template base
│   ├── inicio.html       # Página inicial
│   ├── saiba_mais.html   # Informações sobre erva-mate
│   ├── contato.html      # Formulário de contato
│   └── sobre_nos.html    # Sobre a empresa
└── static/              # Arquivos estáticos
    └── css/
        └── style.css    # Estilos customizados
```

## Recursos Implementados

- Design responsivo com Bootstrap
- Formulário de contato funcional
- Animações CSS suaves
- Gradientes e efeitos visuais
- Ícones temáticos relacionados à erva-mate
- Sistema de mensagens flash
- Navegação intuitiva

## Próximas Implementações

O site foi desenvolvido em Python Flask para facilitar futuras integrações:
- Sistema de gerenciamento de produtos
- E-commerce integrado
- Blog sobre sustentabilidade
- Sistema de newsletter
- Integração com APIs de pagamento
- Dashboard administrativo