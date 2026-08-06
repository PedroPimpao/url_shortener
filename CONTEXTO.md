# Contexto do projeto

## Visão geral

Este projeto é o backend de um encurtador de URLs. A aplicação expõe uma API HTTP para cadastro e autenticação de usuários, criação e gerenciamento de links curtos, contabilização de acessos e geração de QR Code.

A API é construída com FastAPI e persiste os dados em PostgreSQL por meio do SQLAlchemy. Cada URL pertence a um usuário. A autenticação usa tokens JWT enviados no cabeçalho `Authorization: Bearer <token>`.

Estado atual relevante:

- a API não possui frontend neste repositório;
- não há suíte de testes versionada;
- a rota de acesso ao link curto retorna a URL original em JSON; ela não executa redirecionamento HTTP;
- os campos de recuperação de senha e expiração de URL existem nos modelos, mas ainda não possuem fluxos implementados;
- `app/routes/user_routes.py` e `app/services/user_service.py` estão vazios e não são registrados na aplicação.

## Tecnologias

- Python;
- FastAPI, para a API web, roteamento, validação e documentação OpenAPI;
- Uvicorn, como servidor ASGI;
- Pydantic e `pydantic-settings`, para schemas e configuração por ambiente;
- SQLAlchemy 2, como ORM;
- PostgreSQL, indicado pelo uso de UUID nativo e dos drivers Psycopg;
- Alembic, para migrações do banco;
- Passlib com bcrypt, para hash e verificação de senhas;
- `python-jose`, para criação e validação de JWT;
- `qrcode` e Pillow, para gerar QR Codes em PNG;
- Taskipy, configurado como atalho para executar o servidor em desenvolvimento.

## Estrutura do projeto

```text
.
├── alembic/
│   ├── versions/              # Migrações versionadas
│   ├── env.py                 # Integra Alembic, configurações e metadata
│   └── script.py.mako         # Template de novas migrações
├── app/
│   ├── controllers/           # Traduz erros do domínio em respostas HTTP
│   ├── database/              # Base declarativa, mixins, engine e sessões
│   ├── models/                # Modelos ORM User e URL
│   ├── routes/                # Endpoints de autenticação e URLs
│   ├── services/              # Regras de autenticação e gerenciamento de URLs
│   ├── utils/                 # Geração criptograficamente segura do short code
│   ├── config.py              # Leitura das variáveis de ambiente
│   ├── dependencies.py        # Sessão de banco e validação do usuário autenticado
│   ├── main.py                # Criação e configuração da aplicação FastAPI
│   ├── schemas.py             # Modelos de entrada Pydantic
│   └── security.py            # Contexto bcrypt e esquema OAuth2
├── .env                       # Configuração local; não deve ser versionada
├── alembic.ini                # Configuração do Alembic
├── pyproject.toml             # Tarefas do projeto
└── requirements.txt           # Dependências Python fixadas
```

## Arquitetura

A aplicação segue uma arquitetura em camadas:

1. **Routes** definem os caminhos HTTP, recebem e validam entradas com Pydantic e injetam dependências.
2. **Controllers** chamam os serviços e convertem exceções específicas da aplicação em `HTTPException`.
3. **Services** concentram autenticação, regras de URL, consultas e transações do ORM.
4. **Models** representam e relacionam as tabelas do banco.
5. **Database** cria o engine e fornece uma `Session` por requisição.

Responsabilidades transversais:

- `app/config.py` centraliza configurações carregadas do `.env`;
- `app/dependencies.py` abre/fecha sessões e resolve o usuário do JWT;
- `app/security.py` configura bcrypt e OAuth2;
- `app/schemas.py` contém os contratos de entrada da API.

## Fluxo de uma requisição

Em uma requisição típica protegida:

1. o Uvicorn entrega a requisição ao FastAPI;
2. o router seleciona o endpoint e o Pydantic valida corpo e parâmetros;
3. `get_session()` cria uma sessão SQLAlchemy e garante seu fechamento ao final;
4. `verify_token()` lê o Bearer token, valida assinatura e expiração, extrai o `sub` e busca o usuário;
5. a rota chama o controller;
6. o controller delega a operação ao service;
7. o service consulta ou altera modelos ORM e, em operações de escrita, executa `commit()`;
8. o controller converte erros conhecidos em respostas HTTP;
9. o FastAPI serializa o resultado em JSON e a sessão é fechada.

Falhas de validação do corpo ou dos parâmetros são tratadas automaticamente pelo FastAPI, normalmente com status `422`.

## Modelos do banco

Todos os modelos usam UUID como chave primária e os campos `created_at` e `updated_at` com timezone. Os valores iniciais de timestamps são definidos pelo banco com `now()`.

### `users`

| Campo | Tipo | Regras |
|---|---|---|
| `id` | UUID | Chave primária, gerada automaticamente |
| `name` | varchar(120) | Obrigatório |
| `email` | varchar(255) | Obrigatório, único e indexado |
| `password` | varchar(255) | Obrigatório; armazena hash bcrypt |
| `password_reset_otp` | varchar(6) | Opcional; fluxo ainda não implementado |
| `password_reset_expires` | datetime com timezone | Opcional; fluxo ainda não implementado |
| `is_password_reset_authorized` | boolean | Obrigatório, padrão `false` |
| `created_at` | datetime com timezone | Criação automática |
| `updated_at` | datetime com timezone | Atualizado pelo ORM em alterações |

### `urls`

| Campo | Tipo | Regras |
|---|---|---|
| `id` | UUID | Chave primária, gerada automaticamente |
| `original_url` | varchar(2048) | Obrigatório |
| `short_code` | varchar(8) | Obrigatório, único e indexado |
| `title` | varchar | Obrigatório; inicia como string vazia |
| `expires_at` | datetime com timezone | Opcional; expiração ainda não é aplicada |
| `clicks` | integer | Obrigatório, padrão `0` |
| `user_id` | UUID | FK obrigatória para `users.id`, indexada |
| `created_at` | datetime com timezone | Criação automática |
| `updated_at` | datetime com timezone | Atualizado pelo ORM em alterações |

O relacionamento é `User 1:N URL`. A remoção de um usuário elimina suas URLs tanto pelo relacionamento ORM (`delete-orphan`) quanto pela FK com `ON DELETE CASCADE`.

## Regras de negócio

- o e-mail de cada usuário deve ser único;
- senhas nunca são persistidas em texto puro: são transformadas em hash bcrypt;
- o login exige combinação válida de e-mail e senha;
- o access token expira após o número de minutos configurado;
- o token chamado de refresh token expira em sete dias;
- um token válido só autentica se o usuário contido em `sub` ainda existir no banco;
- toda URL encurtada pertence ao usuário autenticado que a criou;
- o código curto possui oito caracteres Base62 (`0-9`, `A-Z`, `a-z`), gerados com `secrets`;
- antes da criação, o serviço compara o código gerado com os códigos já existentes; há também restrição única no banco;
- acessar uma URL curta incrementa `clicks` em uma unidade;
- listar URLs retorna apenas as URLs do usuário autenticado;
- atualizar título, gerar QR Code e excluir URL exigem que o código pertença ao usuário autenticado;
- o QR Code contém a URL original, não a URL curta;
- o fluxo atual não valida se `original_url` é uma URL bem-formada;
- `expires_at` não é consultado ao acessar um link;
- o endpoint de refresh aceita qualquer JWT válido emitido pela aplicação; não diferencia access token de refresh token.

## Rotas de API

O FastAPI também disponibiliza, por padrão, a interface Swagger em `/docs`, ReDoc em `/redoc` e o schema em `/openapi.json`.

| Método | Rota | Autenticação | Entrada | Resultado principal |
|---|---|---|---|---|
| GET | `/` | Não | — | Confirma que a API está funcionando |
| GET | `/auth/` | Não | — | Mensagem da área de autenticação |
| POST | `/auth/create-account` | Não | JSON: `name`, `email`, `password` | Cria conta e retorna mensagem e e-mail |
| POST | `/auth/login` | Não | JSON: `email`, `password` | Retorna access token, refresh token e tipo |
| POST | `/auth/login-form` | Não | Form OAuth2: `username`, `password` | Retorna access token e tipo; usado pelo Swagger |
| GET | `/auth/refresh-token` | Bearer | — | Emite novo access token |
| GET | `/auth/me` | Bearer | — | Retorna `id`, `name` e `email` do usuário |
| GET | `/url/` | Bearer | — | Mensagem da área de URLs |
| POST | `/url/create-short-url` | Bearer | JSON: `original_url` | Cria link e retorna código e URL curta montada |
| GET | `/url/access-url/{short_code}` | Bearer | Parâmetro de caminho | Retorna URL original e total de cliques atualizado |
| GET | `/url/list_urls` | Bearer | — | Lista URLs do usuário |
| PATCH | `/url/update-title/{short_code}` | Bearer | JSON: `title` | Atualiza o título de uma URL do usuário |
| GET | `/url/generate-qrcode/{short_code}` | Bearer | Parâmetro de caminho | Retorna PNG codificado em Base64 |
| DELETE | `/url/delete-url/{short_code}` | Bearer | Parâmetro de caminho | Exclui uma URL do usuário |

Observação: `dependencies=[Depends(verify_token)]` foi aplicado ao router inteiro de URLs. Portanto, inclusive `/url/access-url/{short_code}` exige autenticação, apesar de o endpoint não receber o usuário explicitamente.

## Variáveis de ambiente

Crie um arquivo `.env` na raiz. Ele não deve ser versionado nem ter seus valores expostos em documentação.

| Variável | Finalidade |
|---|---|
| `DATABASE_URL` | String de conexão SQLAlchemy com o banco PostgreSQL. Também é usada pelo Alembic. |
| `SECRET_KEY` | Segredo usado para assinar e validar os tokens JWT. Deve ser forte e privado. |
| `ALGORITHM` | Algoritmo criptográfico usado pelo `python-jose` para JWT, como um algoritmo HMAC compatível. |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Duração, em minutos, do access token. Deve ser um número inteiro. |
| `API_URL` | URL base pública usada para montar o campo `short-url` após a criação de um link. |

Todas são obrigatórias na inicialização. Variáveis adicionais são ignoradas pela configuração atual.

## Dependências do projeto

As dependências diretas e transitivas estão fixadas em `requirements.txt`. As principais por função são:

- **API/servidor:** `fastapi`, `starlette`, `uvicorn`, `anyio`, `h11`, `click`;
- **validação/configuração:** `pydantic`, `pydantic-core`, `pydantic-settings`, `python-dotenv`, `annotated-types`, `typing-extensions`;
- **banco/migrações:** `SQLAlchemy`, `SQLAlchemy-Utils`, `alembic`, `greenlet`, `Mako`, `MarkupSafe`;
- **drivers PostgreSQL:** `psycopg`, `psycopg-binary` e `psycopg2-binary`;
- **autenticação/criptografia:** `passlib`, `bcrypt`, `python-jose`, `cryptography`, `ecdsa`, `rsa`, `pyasn1`, `cffi`;
- **formulários:** `python-multipart`, necessário ao login OAuth2 por formulário;
- **QR Code:** `qrcode` e `pillow`.

O `pyproject.toml` configura o comando Taskipy `dev`, embora `taskipy` não esteja listado em `requirements.txt`; para usar esse atalho, ele precisa estar disponível no ambiente. Como alternativa, execute o Uvicorn diretamente.

## Convenções

- módulos, funções e variáveis seguem `snake_case`; classes usam `PascalCase`;
- modelos ORM são anotados com `Mapped[...]` e `mapped_column`;
- IDs são UUIDs gerados pela aplicação;
- schemas de entrada ficam centralizados em `app/schemas.py`;
- regras de aplicação ficam em métodos estáticos de services;
- controllers convertem exceções dos services em erros HTTP;
- dependências FastAPI fornecem sessão e usuário autenticado;
- endpoints protegidos usam Bearer token;
- migrações seguem a cadeia de revisões do Alembic;
- respostas usam JSON, mas atualmente misturam nomes em `snake_case` (`access_token`) e kebab-case (`short-code`, `original-url`); ao estender a API, convém preservar o contrato existente ou padronizá-lo de forma versionada.

## Padrões de erro

Erros HTTP explícitos seguem o formato padrão do FastAPI:

```json
{
  "detail": "Mensagem do erro"
}
```

| Status | Situação atual |
|---|---|
| `400 Bad Request` | Tentativa de cadastrar e-mail já existente |
| `401 Unauthorized` | Credenciais inválidas, JWT inválido/expirado ou usuário do token inexistente |
| `404 Not Found` | URL não encontrada, URL fora da propriedade do usuário ou lista vazia |
| `422 Unprocessable Entity` | Entrada ausente ou incompatível com os schemas, tratado pelo FastAPI |
| `500 Internal Server Error` | Falha capturada ao buscar URLs durante a criação do link, ou erro não tratado |

Os services lançam `EmailAlreadyExistsError`, `InvalidCredentialsError`, `UniqueURLNotFoundError` e `MultipleURLsNotFoundError`; os controllers fazem o mapeamento para HTTP. As operações atuais não executam `rollback()` explicitamente após falhas de banco, e várias consultas capturam exceções de forma genérica.

## Fluxos principais

### Cadastro e login

1. o cliente cria uma conta em `/auth/create-account`;
2. o serviço impede e-mail duplicado e salva a senha com bcrypt;
3. o cliente envia as credenciais a `/auth/login`;
4. após a validação, recebe access token e refresh token;
5. envia o access token como Bearer nas rotas protegidas;
6. pode consultar sua identidade em `/auth/me` e emitir um novo access token em `/auth/refresh-token`.

### Criação e acesso de URL curta

1. o usuário autenticado envia `original_url` para `/url/create-short-url`;
2. o serviço gera um código Base62 de oito caracteres e evita colisões conhecidas;
3. a URL é salva vinculada ao usuário, com título vazio e zero cliques;
4. a resposta monta a URL curta com `API_URL` e o código;
5. ao chamar `/url/access-url/{short_code}`, a API localiza o registro, incrementa os cliques e retorna a URL original em JSON.

### Gerenciamento das URLs

1. `/url/list_urls` lista links do usuário autenticado;
2. `/url/update-title/{short_code}` altera o título quando o link pertence ao usuário;
3. `/url/generate-qrcode/{short_code}` gera um PNG da URL original e o devolve em Base64;
4. `/url/delete-url/{short_code}` remove definitivamente o link pertencente ao usuário.

## Como executar o projeto

Pré-requisitos: Python compatível com as versões de `requirements.txt` e uma instância PostgreSQL acessível.

No PowerShell, a partir da raiz do projeto:

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Crie o `.env` com todas as variáveis descritas acima e aplique as migrações:

```powershell
alembic upgrade head
```

Inicie o servidor em desenvolvimento:

```powershell
uvicorn app.main:app --reload
```

Se o Taskipy estiver instalado no ambiente, o atalho equivalente é:

```powershell
task dev
```

Por padrão, o Uvicorn atende em `http://127.0.0.1:8000`. Use `http://127.0.0.1:8000/docs` para explorar e testar a API pelo Swagger. Para autorizar no Swagger, crie uma conta e use `/auth/login-form`; nesse formulário, o campo `username` deve receber o e-mail.

Para criar uma nova migração após alterar modelos e depois aplicá-la:

```powershell
alembic revision --autogenerate -m "descricao da alteracao"
alembic upgrade head
```
