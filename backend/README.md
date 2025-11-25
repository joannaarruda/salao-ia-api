# Salão IA API

Este projeto é uma API para um sistema de gerenciamento de salão, desenvolvido com FastAPI. A API permite o registro de usuários, agendamentos de serviços e sugestões de estilos de cabelo utilizando inteligência artificial.

## Estrutura do Projeto

```
salao-ia-api
├── backend
│   ├── app
│   │   ├── __init__.py          # Inicializa o pacote da aplicação
│   │   ├── main.py              # Ponto de entrada da aplicação FastAPI
│   │   ├── models.py            # Define os modelos de dados com Pydantic
│   │   ├── auth.py              # Lógica de autenticação
│   │   ├── database.py          # Operações de banco de dados JSON
│   │   ├── controllers           # Controladores para operações específicas
│   │   │   ├── __init__.py
│   │   │   ├── users.py         # Operações relacionadas a usuários
│   │   │   ├── appointments.py   # Operações relacionadas a agendamentos
│   │   │   └── professionals.py   # Operações relacionadas a profissionais
│   │   ├── routes                # Rotas da API
│   │   │   ├── __init__.py
│   │   │   ├── auth.py          # Rotas de autenticação
│   │   │   ├── appointments.py   # Rotas de agendamentos
│   │   │   └── professionals.py   # Rotas de profissionais
│   │   └── utils                 # Utilitários e integrações
│   │       ├── __init__.py
│   │       ├── ai_integration.py # Integração com serviços de IA
│   │       └── validators.py     # Funções de validação
│   ├── data                      # Dados armazenados em JSON
│   │   ├── users.json
│   │   ├── appointments.json
│   │   └── professionals.json
│   ├── uploads                   # Diretório para arquivos enviados
│   ├── .env                      # Variáveis de ambiente
│   ├── requirements.txt          # Dependências do projeto
│   └── README.md                 # Documentação do backend
├── frontend                      # Frontend da aplicação
│   ├── index.html                # HTML principal
│   ├── css
│   │   └── style.css             # Estilos do frontend
│   ├── js
│   │   ├── app.js                # Lógica principal do JavaScript
│   │   ├── api.js                # Funções para chamadas de API
│   │   └── auth.js               # Funções de autenticação
│   └── assets                    # Recursos adicionais
└── .gitignore                    # Arquivos a serem ignorados pelo Git
```

## Como Executar

1. **Clone o repositório**:
   ```
   git clone <URL_DO_REPOSITORIO>
   cd salao-ia-api
   ```

2. **Instale as dependências**:
   ```
   cd backend
   pip install -r requirements.txt
   ```

3. **Configure as variáveis de ambiente** no arquivo `.env`.

4. **Inicie a aplicação**:
   ```
   uvicorn app.main:app --reload
   ```

5. **Acesse a documentação da API** em `http://localhost:8000/docs`.

## Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para abrir um pull request ou relatar problemas.

## Licença

Este projeto está licenciado sob a MIT License.