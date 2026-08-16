# Contrato da API

Este documento descreve o comportamento atual da API do encurtador de URLs. Os exemplos usam `http://127.0.0.1:8000` como URL base.

## Convenções gerais

- Requisições JSON devem usar `Content-Type: application/json`.
- Rotas protegidas exigem `Authorization: Bearer <token>`.
- O token é obtido em `POST /auth/login` ou `POST /auth/login-form`.
- Respostas de erro explícitas seguem o formato `{"detail": "mensagem"}`.
- Entradas ausentes ou inválidas normalmente retornam `422 Unprocessable Entity`, com o formato de validação padrão do FastAPI.
- IDs de usuários são UUIDs.
- Datas e senhas nunca são retornadas pelos endpoints atuais.

### Erro de autenticação

Rotas protegidas retornam `401 Unauthorized` quando o token está ausente, inválido, expirado ou pertence a um usuário inexistente.

```json
{
  "detail": "Access Denied"
}
```

Quando o cabeçalho Bearer não é enviado, o detalhe pode ser gerado automaticamente pelo esquema OAuth2 do FastAPI.

## Resumo dos endpoints

| Método | Endpoint | Autenticação | Descrição |
|---|---|---|---|
| `GET` | `/` | Não | Verifica se a API está funcionando |
| `GET` | `/auth/` | Não | Verifica o módulo de autenticação |
| `POST` | `/auth/create-account` | Não | Cria uma conta |
| `POST` | `/auth/login` | Não | Autentica com JSON e emite tokens |
| `POST` | `/auth/login-form` | Não | Autentica com formulário OAuth2 |
| `GET` | `/auth/refresh-token` | Bearer | Emite um novo access token |
| `GET` | `/auth/me` | Bearer | Retorna o usuário autenticado |
| `POST` | `/auth/password-reset/request` | Não | Gera um OTP de recuperação |
| `POST` | `/auth/password-reset/verify` | Não | Valida o OTP e emite um reset token |
| `POST` | `/auth/password-reset/complete` | Não | Redefine a senha |
| `PATCH` | `/user/update-name` | Bearer | Atualiza o nome |
| `PATCH` | `/user/update-email` | Bearer | Atualiza o e-mail |
| `PATCH` | `/user/update-password` | Bearer | Atualiza a senha autenticada |
| `GET` | `/url/` | Bearer | Verifica o módulo de URLs |
| `POST` | `/url/create-short-url` | Bearer | Cria uma URL curta |
| `GET` | `/url/access-url/{short_code}` | Bearer | Consulta a URL original e registra um clique |
| `GET` | `/url/list_urls` | Bearer | Lista as URLs do usuário |
| `GET` | `/url/get-stats` | Bearer | Retorna estatísticas das URLs do usuário |
| `PATCH` | `/url/update-title/{short_code}` | Bearer | Atualiza o título de uma URL |
| `GET` | `/url/generate-qrcode/{short_code}` | Bearer | Gera um QR Code em Base64 |
| `DELETE` | `/url/delete-url/{short_code}` | Bearer | Exclui uma URL |

## Aplicação

### `GET /`

Verifica se a aplicação está funcionando.

**Resposta — `200 OK`**

```json
{
  "message": "API Funcionando"
}
```

## Autenticação

### `GET /auth/`

Verifica se o módulo de autenticação está acessível.

**Resposta — `200 OK`**

```json
{
  "message": "Home Auth Route"
}
```

### `POST /auth/create-account`

Cria uma conta de usuário.

**Corpo JSON**

| Campo | Tipo | Obrigatório | Regras atuais |
|---|---|---|---|
| `name` | string | Sim | Não possui limite específico neste schema |
| `email` | string | Sim | Deve ser único; não é normalizado por este endpoint |
| `password` | string | Sim | É armazenada como hash bcrypt |

```json
{
  "name": "Maria Silva",
  "email": "maria@example.com",
  "password": "senha-segura"
}
```

**Resposta — `200 OK`**

```json
{
  "message": "Conta criada com sucesso",
  "email": "maria@example.com"
}
```

**Erros conhecidos**

- `400 Bad Request`: `{"detail": "Email já cadastrado"}`.
- `422 Unprocessable Entity`: corpo ausente ou campo com tipo incompatível.

### `POST /auth/login`

Autentica por JSON. Retorna um access token e um refresh token.

**Corpo JSON**

```json
{
  "email": "maria@example.com",
  "password": "senha-segura"
}
```

**Resposta — `200 OK`**

```json
{
  "access_token": "jwt-access-token",
  "refresh_token": "jwt-refresh-token",
  "token_type": "Bearer"
}
```

O access token usa a validade definida em `ACCESS_TOKEN_EXPIRE_MINUTES`. O refresh token é emitido com validade de sete dias.

**Erros conhecidos**

- `401 Unauthorized`: `{"detail": "Credenciais inválidas"}` para e-mail inexistente ou senha incorreta.
- `422 Unprocessable Entity`: corpo inválido.

### `POST /auth/login-form`

Alternativa de login compatível com OAuth2 e com o botão **Authorize** do Swagger.

**Content-Type**

```text
application/x-www-form-urlencoded
```

**Campos do formulário**

| Campo | Uso |
|---|---|
| `username` | Deve receber o e-mail do usuário |
| `password` | Senha do usuário |

Exemplo:

```text
username=maria%40example.com&password=senha-segura
```

**Resposta — `200 OK`**

```json
{
  "access_token": "jwt-access-token",
  "token_type": "Bearer"
}
```

Essa rota não retorna refresh token.

**Erros conhecidos**

- `401 Unauthorized`: `{"detail": "Credenciais inválidas"}`.
- `422 Unprocessable Entity`: formulário ausente ou inválido.

### `GET /auth/refresh-token`

Emite um novo access token para o usuário identificado pelo token Bearer enviado.

**Cabeçalho**

```http
Authorization: Bearer <token>
```

**Resposta — `200 OK`**

```json
{
  "access_token": "novo-jwt-access-token",
  "token_type": "Bearer"
}
```

Atualmente, a rota aceita qualquer JWT válido emitido pela aplicação; não diferencia access token de refresh token.

**Erros conhecidos**

- `401 Unauthorized`: token inválido, expirado ou associado a usuário inexistente.

### `GET /auth/me`

Retorna os dados públicos do usuário autenticado.

**Cabeçalho**

```http
Authorization: Bearer <access_token>
```

**Resposta — `200 OK`**

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Maria Silva",
  "email": "maria@example.com"
}
```

**Erros conhecidos**

- `401 Unauthorized`: token inválido, expirado ou associado a usuário inexistente.

## Recuperação de senha

O fluxo possui três etapas: solicitar OTP, validar OTP e redefinir a senha. O OTP é retornado diretamente pela API porque este projeto tem finalidade de estudo.

### `POST /auth/password-reset/request`

Gera um OTP numérico de seis dígitos. Para uma conta existente, somente o hash do código é persistido, com prazo de expiração e contador de tentativas.

**Corpo JSON**

```json
{
  "email": "maria@example.com"
}
```

O e-mail é normalizado para minúsculas e validado.

**Resposta — `202 Accepted`**

```json
{
  "message": "Código de recuperação gerado com sucesso",
  "otp": "123456"
}
```

Para um e-mail inexistente, a resposta mantém o mesmo formato e contém um OTP aleatório, mas esse código não é persistido e não será aceito na próxima etapa.

**Erros conhecidos**

- `422 Unprocessable Entity`: e-mail ausente ou inválido.
- `429 Too Many Requests`: mais de cinco solicitações pelo mesmo IP em 15 minutos.

```json
{
  "detail": "Muitas tentativas. Tente novamente mais tarde"
}
```

### `POST /auth/password-reset/verify`

Valida o OTP e o troca por um token temporário de redefinição. O OTP deixa de ser válido após uma verificação bem-sucedida.

**Corpo JSON**

| Campo | Tipo | Regras |
|---|---|---|
| `email` | string | E-mail válido e normalizado |
| `otp` | string | Exatamente seis dígitos |

```json
{
  "email": "maria@example.com",
  "otp": "123456"
}
```

**Resposta — `200 OK`**

```json
{
  "reset_token": "token-temporario-de-redefinicao"
}
```

**Erros conhecidos**

- `400 Bad Request`: `{"detail": "Código inválido ou expirado"}`.
- `422 Unprocessable Entity`: e-mail inválido ou OTP fora do formato de seis dígitos.
- `429 Too Many Requests`: mais de dez verificações pelo mesmo IP em 15 minutos.

Cada OTP permite no máximo o número de tentativas definido em `PASSWORD_RESET_MAX_ATTEMPTS`, cujo padrão é cinco.

### `POST /auth/password-reset/complete`

Redefine a senha usando o reset token recebido na etapa anterior. O token é temporário e consumido após o sucesso.

**Corpo JSON**

| Campo | Tipo | Regras |
|---|---|---|
| `reset_token` | string | Entre 32 e 255 caracteres |
| `new_password` | string | Entre 8 e 72 caracteres e no máximo 72 bytes |
| `new_password_confirmation` | string | Deve ser igual a `new_password` |

```json
{
  "reset_token": "token-temporario-de-redefinicao",
  "new_password": "nova-senha-segura",
  "new_password_confirmation": "nova-senha-segura"
}
```

**Resposta — `200 OK`**

```json
{
  "message": "Senha redefinida com sucesso"
}
```

**Erros conhecidos**

- `400 Bad Request`: `{"detail": "Autorização inválida ou expirada"}`.
- `400 Bad Request`: `{"detail": "A nova senha deve ser diferente da senha atual"}`.
- `422 Unprocessable Entity`: senha inválida ou confirmação divergente.
- `429 Too Many Requests`: mais de dez tentativas pelo mesmo IP em 15 minutos.

## Manutenção do usuário

Todas as rotas desta seção exigem Bearer token. A conta alterada é sempre a conta indicada pelo token.

### `PATCH /user/update-name`

Atualiza o nome do usuário autenticado.

**Corpo JSON**

```json
{
  "new_name": "Maria Souza"
}
```

O nome deve possuir entre 2 e 120 caracteres. Espaços repetidos são normalizados.

**Resposta — `200 OK`**

```json
{
  "message": "Nome atualizado com sucesso",
  "name": "Maria Souza"
}
```

**Erros conhecidos**

- `400 Bad Request`: `{"detail": "O novo nome deve ser diferente do nome atual"}`.
- `401 Unauthorized`: falha de autenticação.
- `422 Unprocessable Entity`: nome fora dos limites ou inválido.

### `PATCH /user/update-email`

Reautentica o usuário e atualiza seu e-mail.

**Corpo JSON**

| Campo | Tipo | Regras |
|---|---|---|
| `current_email` | string | Deve corresponder ao e-mail atual |
| `new_email` | string | Deve ser válido, diferente e único |
| `password` | string | Senha atual; pelo menos um caractere |

```json
{
  "current_email": "maria@example.com",
  "new_email": "maria.souza@example.com",
  "password": "senha-segura"
}
```

Os e-mails são normalizados para minúsculas.

**Resposta — `200 OK`**

```json
{
  "message": "Email atualizado com sucesso",
  "email": "maria.souza@example.com"
}
```

**Erros conhecidos**

- `400 Bad Request`: `{"detail": "Email já cadastrado"}`.
- `401 Unauthorized`: `{"detail": "Credenciais atuais inválidas"}` ou falha no Bearer token.
- `422 Unprocessable Entity`: e-mail inválido, e-mails iguais ou senha vazia.

### `PATCH /user/update-password`

Reautentica o usuário e altera sua senha sem usar o fluxo de recuperação.

**Corpo JSON**

| Campo | Tipo | Regras |
|---|---|---|
| `email` | string | Deve corresponder ao usuário autenticado |
| `current_password` | string | Senha atual; pelo menos um caractere |
| `new_password` | string | Entre 8 e 72 caracteres e no máximo 72 bytes |
| `new_password_confirmation` | string | Deve ser igual à nova senha |

```json
{
  "email": "maria.souza@example.com",
  "current_password": "senha-segura",
  "new_password": "outra-senha-segura",
  "new_password_confirmation": "outra-senha-segura"
}
```

**Resposta — `200 OK`**

```json
{
  "message": "Senha atualizada com sucesso"
}
```

**Erros conhecidos**

- `400 Bad Request`: `{"detail": "A nova senha deve ser diferente da senha atual"}`.
- `401 Unauthorized`: `{"detail": "Credenciais atuais inválidas"}` ou falha no Bearer token.
- `422 Unprocessable Entity`: senha fora dos limites, confirmação divergente ou nova senha igual à atual no próprio corpo.

## URLs encurtadas

Todas as rotas `/url`, inclusive `access-url`, exigem Bearer token por configuração do router.

### `GET /url/`

Verifica se o módulo de URLs está acessível para o usuário autenticado.

**Resposta — `200 OK`**

```json
{
  "message": "Home URL Route"
}
```

### `POST /url/create-short-url`

Cria uma URL curta vinculada ao usuário autenticado.

**Corpo JSON**

```json
{
  "original_url": "https://example.com/conteudo"
}
```

Atualmente, `original_url` é uma string sem validação específica de formato ou tamanho no schema de entrada.

**Resposta — `200 OK`**

```json
{
  "message": "URL Curto",
  "short-code": "aB12Cd34",
  "short-url": "http://127.0.0.1:8000/aB12Cd34"
}
```

`short-url` é montada usando `API_URL` e o código gerado. A aplicação não possui atualmente uma rota pública `/{short_code}`; o endpoint de consulta implementado é `/url/access-url/{short_code}`.

**Erros conhecidos**

- `401 Unauthorized`: falha de autenticação.
- `422 Unprocessable Entity`: corpo ausente ou inválido.
- `500 Internal Server Error`: `{"detail": "Erro ao buscar URLs"}`.

### `GET /url/access-url/{short_code}`

Localiza o código, incrementa `clicks` e retorna a URL original. Não executa redirecionamento HTTP.

**Parâmetro de caminho**

| Parâmetro | Tipo | Descrição |
|---|---|---|
| `short_code` | string | Código curto da URL |

Exemplo:

```http
GET /url/access-url/aB12Cd34
Authorization: Bearer <access_token>
```

**Resposta — `200 OK`**

```json
{
  "message": "URL Original",
  "original-url": "https://example.com/conteudo",
  "clicks": 1
}
```

**Erros conhecidos**

- `401 Unauthorized`: falha de autenticação.
- `404 Not Found`: `{"detail": "URL não encontrada"}` ou `{"detail": "Erro ao buscar URL"}`.

### `GET /url/list_urls`

Lista apenas as URLs pertencentes ao usuário autenticado.

**Resposta — `200 OK`**

```json
{
  "message": "URLs do Usuário",
  "urls": [
    {
      "url_title": "Conteúdo de exemplo",
      "original-url": "https://example.com/conteudo",
      "short-code": "aB12Cd34",
      "clicks": 3
    }
  ]
}
```

**Erros conhecidos**

- `401 Unauthorized`: falha de autenticação.
- `404 Not Found`: `{"detail": "Nenhuma URL encontrada para o usuário"}`.
- `404 Not Found`: `{"detail": "Erro ao buscar URLs"}` em falha de consulta.

### `GET /url/get-stats`

Retorna estatísticas calculadas apenas a partir das URLs pertencentes ao usuário autenticado.

**Resposta — `200 OK`**

```json
{
  "total_urls": 3,
  "total_clicks": 12,
  "url_most_clicks": "aB12Cd34",
  "most_clicks": 7
}
```

`url_most_clicks` contém o código curto da URL com mais acessos, enquanto `most_clicks` informa sua quantidade de cliques. Em caso de empate, é retornada a primeira URL encontrada com a maior quantidade.

**Erros conhecidos**

- `401 Unauthorized`: falha de autenticação.
- `404 Not Found`: `{"detail": "URLs não encontradas"}` quando o usuário não possui URLs.
- `404 Not Found`: `{"detail": "Erro ao buscar URLs"}` em falha de consulta ou cálculo.

### `PATCH /url/update-title/{short_code}`

Atualiza o título de uma URL pertencente ao usuário autenticado.

**Corpo JSON**

```json
{
  "title": "Documentação importante"
}
```

Atualmente, o título não possui limite ou validação específica no schema.

**Resposta — `200 OK`**

```json
{
  "message": "Título atualizado com sucesso",
  "new-title": "Documentação importante"
}
```

**Erros conhecidos**

- `401 Unauthorized`: falha de autenticação.
- `404 Not Found`: `{"detail": "URL não encontrada"}` ou `{"detail": "Erro ao buscar URL"}`.
- `422 Unprocessable Entity`: corpo ausente ou inválido.

### `GET /url/generate-qrcode/{short_code}`

Gera um QR Code PNG contendo a URL original. A imagem é retornada como texto Base64 dentro de JSON.

**Resposta — `200 OK`**

```json
{
  "message": "QR Code gerado com sucesso",
  "qrcode": "iVBORw0KGgoAAAANSUhEUgAA..."
}
```

Para reconstruir o arquivo, o cliente deve decodificar `qrcode` de Base64 para bytes e salvá-los como PNG.

**Erros conhecidos**

- `401 Unauthorized`: falha de autenticação.
- `404 Not Found`: `{"detail": "Erro ao buscar URL"}` quando a URL não existe, não pertence ao usuário ou ocorre uma falha de consulta.

### `DELETE /url/delete-url/{short_code}`

Exclui uma URL pertencente ao usuário autenticado.

**Resposta — `200 OK`**

```json
{
  "message": "URL excluída com sucesso",
  "short-code": "aB12Cd34"
}
```

**Erros conhecidos**

- `401 Unauthorized`: falha de autenticação.
- `404 Not Found`: `{"detail": "Erro ao buscar URL"}` quando a URL não existe, não pertence ao usuário ou ocorre uma falha de consulta.

## Documentação automática

Com a aplicação em execução, o FastAPI também disponibiliza:

- Swagger UI: `GET /docs`;
- ReDoc: `GET /redoc`;
- Especificação OpenAPI: `GET /openapi.json`.

Essas rotas são geradas automaticamente e não exigem Bearer token para abrir a documentação. As chamadas feitas pela interface continuam sujeitas à autenticação de cada endpoint.
