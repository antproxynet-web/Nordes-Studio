# Contratos de API - Backend Unificado

## 📋 Visão Geral

Documentação completa de todos os endpoints da API do Nordes Studio.

**Base URL**: `http://localhost:5000`

**Autenticação**: JWT (Bearer Token)

---

## 🔐 Autenticação

### POST `/api/signup`

Criar nova conta de usuário.

**Autenticação**: ❌ Não requerida

**Body**:
```json
{
  "email": "user@example.com",
  "password": "senha123",
  "firstname": "João",
  "lastname": "Silva",
  "phone": "11999999999",
  "username": "joaosilva"  // Opcional
}
```

**Resposta (201)**:
```json
{
  "message": "Conta criada com sucesso",
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "name": "João Silva",
    "username": "joaosilva",
    "phone": "11999999999",
    "bio": null,
    "picture": null,
    "role": "user",
    "is_online": false,
    "last_seen": null,
    "is_verified": false,
    "verified_at": null
  }
}
```

**Erros**:
- `400`: Email já cadastrado
- `400`: Username já em uso
- `400`: Email e senha são obrigatórios

---

### POST `/api/login`

Login com email e senha.

**Autenticação**: ❌ Não requerida

**Body**:
```json
{
  "email": "user@example.com",
  "password": "senha123"
}
```

**Resposta (200)**:
```json
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "name": "João Silva",
    "username": "joaosilva",
    "is_verified": true,
    "verified_at": "2026-02-01T20:30:00.000Z",
    ...
  }
}
```

**Erros**:
- `401`: Usuário não encontrado
- `401`: Senha incorreta
- `400`: Email e senha são obrigatórios

---

### GET `/login/google`

Iniciar autenticação com Google OAuth.

**Autenticação**: ❌ Não requerida

**Resposta**: Redirect para Google OAuth

**Fluxo**:
1. Frontend redireciona para `/login/google`
2. Google autentica o usuário
3. Google redireciona para `/authorize/google`
4. Backend cria/atualiza usuário e gera JWT
5. Backend redireciona para `/pages/home.html?token=...&user=...`

---

### GET `/authorize/google`

Callback do Google OAuth (não chamar diretamente).

**Autenticação**: ❌ Não requerida

**Resposta**: Redirect para `/pages/home.html` com token JWT

---

### GET `/api/logout`

Logout do usuário.

**Autenticação**: ❌ Não requerida

**Resposta (200)**:
```json
{
  "success": true
}
```

---

## 👤 Usuário

### GET `/api/user/profile`

Obter perfil do usuário autenticado.

**Autenticação**: ✅ Requerida (JWT)

**Headers**:
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

**Resposta (200)**:
```json
{
  "id": 1,
  "email": "user@example.com",
  "name": "João Silva",
  "username": "joaosilva",
  "phone": "11999999999",
  "bio": "Desenvolvedor Full Stack",
  "picture": "/uploads/profile_1_20260201_125559.jpg",
  "role": "user",
  "is_online": true,
  "last_seen": "2026-02-01T20:30:00.000Z",
  "is_verified": true,
  "verified_at": "2026-02-01T15:00:00.000Z"
}
```

**Erros**:
- `401`: Token ausente ou inválido

---

### PUT `/api/user/profile`

Atualizar perfil do usuário.

**Autenticação**: ✅ Requerida (JWT)

**Body** (todos os campos são opcionais):
```json
{
  "name": "João Pedro Silva",
  "username": "jpsilva",
  "bio": "Desenvolvedor Full Stack | Python | React"
}
```

**Resposta (200)**:
```json
{
  "message": "Perfil atualizado com sucesso",
  "user": {
    "id": 1,
    "name": "João Pedro Silva",
    "username": "jpsilva",
    "bio": "Desenvolvedor Full Stack | Python | React",
    ...
  }
}
```

**Erros**:
- `400`: Username já em uso
- `401`: Token ausente ou inválido

**Observações**:
- ⚠️ **Email NÃO pode ser alterado** via este endpoint
- Apenas campos `name`, `username` e `bio` são permitidos

---

### GET `/api/user/check-username`

Verificar disponibilidade de username.

**Autenticação**: ✅ Requerida (JWT)

**Query Params**:
- `username`: Username a ser verificado

**Exemplo**:
```
GET /api/user/check-username?username=joaosilva
```

**Resposta (200) - Disponível**:
```json
{
  "available": true
}
```

**Resposta (200) - Indisponível**:
```json
{
  "available": false,
  "message": "Este nome de usuário já está em uso"
}
```

**Validações**:
- Mínimo 3 caracteres
- Máximo 30 caracteres
- Apenas letras, números, `.` e `_`
- Não pode começar ou terminar com `.` ou `_`

---

### POST `/api/user/profile-picture`

Upload de foto de perfil.

**Autenticação**: ✅ Requerida (JWT)

**Body** (multipart/form-data):
```
profile_picture: <arquivo>
```

**Resposta (200)**:
```json
{
  "message": "Foto de perfil atualizada com sucesso",
  "picture": "/uploads/profile_1_20260201_125559.jpg"
}
```

**Erros**:
- `400`: Nenhum arquivo enviado
- `400`: Formato de arquivo não permitido (apenas png, jpg, jpeg, gif)
- `400`: Arquivo muito grande (máximo 5MB)
- `401`: Token ausente ou inválido

---

## 💬 Chat

### GET `/api/chat/users`

Listar usuários para chat.

**Autenticação**: ✅ Requerida (JWT)

**Query Params**:
- `search`: Buscar por username ou nome (opcional)

**Exemplo**:
```
GET /api/chat/users?search=joao
```

**Resposta (200)**:
```json
[
  {
    "id": 2,
    "username": "joaosilva",
    "name": "João Silva",
    "picture": "/uploads/profile_2.jpg",
    "is_online": true,
    "last_seen": "2026-02-01T20:30:00.000Z",
    "is_verified": true,
    "last_message": "Oi, tudo bem?",
    "last_message_time": "2026-02-01T20:25:00.000Z",
    "unread_count": 2
  },
  ...
]
```

**Observações**:
- Retorna no máximo 20 usuários
- Ordenado por última mensagem

---

### GET `/api/chat/messages/<user_id>`

Obter mensagens com um usuário específico.

**Autenticação**: ✅ Requerida (JWT)

**Exemplo**:
```
GET /api/chat/messages/2
```

**Resposta (200)**:
```json
[
  {
    "id": 1,
    "sender_id": 1,
    "receiver_id": 2,
    "content": "Oi, tudo bem?",
    "timestamp": "2026-02-01T20:20:00.000Z",
    "is_read": true
  },
  {
    "id": 2,
    "sender_id": 2,
    "receiver_id": 1,
    "content": "Tudo ótimo! E você?",
    "timestamp": "2026-02-01T20:21:00.000Z",
    "is_read": true
  },
  ...
]
```

**Efeito Colateral**:
- Marca automaticamente as mensagens recebidas como lidas

---

### POST `/api/chat/send`

Enviar mensagem (REST - alternativa ao SocketIO).

**Autenticação**: ✅ Requerida (JWT)

**Body**:
```json
{
  "receiver_id": 2,
  "content": "Oi, tudo bem?"
}
```

**Resposta (201)**:
```json
{
  "id": 1,
  "sender_id": 1,
  "receiver_id": 2,
  "content": "Oi, tudo bem?",
  "timestamp": "2026-02-01T20:20:00.000Z",
  "is_read": false
}
```

**Erros**:
- `400`: Dados incompletos
- `401`: Token ausente ou inválido

---

### GET `/api/chat/user/<user_id>`

Obter informações de um usuário.

**Autenticação**: ✅ Requerida (JWT)

**Exemplo**:
```
GET /api/chat/user/2
```

**Resposta (200)**:
```json
{
  "id": 2,
  "username": "joaosilva",
  "name": "João Silva",
  "bio": "Desenvolvedor Full Stack",
  "picture": "/uploads/profile_2.jpg",
  "is_online": true,
  "last_seen": "2026-02-01T20:30:00.000Z",
  "is_verified": true
}
```

**Erros**:
- `404`: Usuário não encontrado

---

## 📚 Livros

### GET `/api/books`

Listar todos os livros.

**Autenticação**: ❌ Não requerida

**Resposta (200)**:
```json
[
  {
    "id": 1,
    "title": "O Senhor dos Anéis",
    "author": "J.R.R. Tolkien",
    "price": 49.90,
    "description": "Uma jornada épica...",
    "image": "livro-1.jpg",
    "release_date": "1954",
    "stock": 10,
    "category": "Fantasia"
  },
  ...
]
```

---

### POST `/api/books`

Adicionar novo livro (apenas admin).

**Autenticação**: ✅ Requerida (JWT + Admin)

**Body** (multipart/form-data):
```
title: O Senhor dos Anéis
author: J.R.R. Tolkien
price: 49.90
description: Uma jornada épica...
stock: 10
category: Fantasia
image: <arquivo>
```

**Resposta (201)**:
```json
{
  "message": "Sucesso",
  "book": {
    "id": 1,
    "title": "O Senhor dos Anéis",
    ...
  }
}
```

**Erros**:
- `401`: Token ausente ou inválido
- `403`: Acesso restrito ao administrador

---

### PUT `/api/books/<id>`

Atualizar livro (apenas admin).

**Autenticação**: ✅ Requerida (JWT + Admin)

**Body** (multipart/form-data - todos os campos opcionais):
```
title: O Senhor dos Anéis - Edição Especial
price: 59.90
stock: 15
```

**Resposta (200)**:
```json
{
  "message": "Atualizado com sucesso",
  "book": {
    "id": 1,
    "title": "O Senhor dos Anéis - Edição Especial",
    "price": 59.90,
    ...
  }
}
```

**Erros**:
- `404`: Livro não encontrado
- `401`: Token ausente ou inválido
- `403`: Acesso restrito ao administrador

---

### DELETE `/api/books/<id>`

Deletar livro (apenas admin).

**Autenticação**: ✅ Requerida (JWT + Admin)

**Resposta (200)**:
```json
{
  "message": "Excluído com sucesso"
}
```

**Erros**:
- `404`: Livro não encontrado
- `401`: Token ausente ou inválido
- `403`: Acesso restrito ao administrador

---

## 👑 Admin

### POST `/api/admin/verify-user/<user_id>`

Marcar usuário como verificado.

**Autenticação**: ✅ Requerida (JWT + Admin)

**Exemplo**:
```
POST /api/admin/verify-user/2
```

**Resposta (200)**:
```json
{
  "message": "Usuário joaosilva verificado com sucesso!",
  "user": {
    "id": 2,
    "username": "joaosilva",
    "is_verified": true,
    "verified_at": "2026-02-01T20:30:00.000Z",
    ...
  }
}
```

**Erros**:
- `404`: Usuário não encontrado
- `400`: Usuário já está verificado
- `401`: Token ausente ou inválido
- `403`: Acesso restrito ao administrador

---

### POST `/api/admin/unverify-user/<user_id>`

Remover verificação de usuário.

**Autenticação**: ✅ Requerida (JWT + Admin)

**Resposta (200)**:
```json
{
  "message": "Verificação removida de joaosilva",
  "user": {
    "id": 2,
    "username": "joaosilva",
    "is_verified": false,
    "verified_at": null,
    ...
  }
}
```

**Erros**:
- `404`: Usuário não encontrado
- `400`: Usuário não está verificado
- `401`: Token ausente ou inválido
- `403`: Acesso restrito ao administrador

---

### GET `/api/admin/verified-users`

Listar usuários verificados.

**Autenticação**: ✅ Requerida (JWT + Admin)

**Resposta (200)**:
```json
[
  {
    "id": 2,
    "username": "joaosilva",
    "is_verified": true,
    "verified_at": "2026-02-01T20:30:00.000Z",
    ...
  },
  ...
]
```

---

### GET `/api/admin/users`

Listar todos os usuários (com filtros).

**Autenticação**: ✅ Requerida (JWT + Admin)

**Query Params**:
- `search`: Buscar por nome, email ou username
- `role`: Filtrar por role (user, professional, admin)
- `verified`: Filtrar por verificação (true/false)

**Exemplo**:
```
GET /api/admin/users?search=joao&verified=true
```

**Resposta (200)**:
```json
[
  {
    "id": 2,
    "username": "joaosilva",
    "email": "joao@example.com",
    "role": "user",
    "is_verified": true,
    ...
  },
  ...
]
```

---

## 🔌 SocketIO Events

### Conexão

**Evento**: `connect`

**Parâmetros**:
```javascript
const socket = io('http://localhost:5000', {
    query: {
        token: 'eyJ0eXAiOiJKV1QiLCJhbGc...'
    }
});
```

**Resposta**:
- Evento `user_status` broadcast para todos: `{user_id: 1, status: 'online'}`

---

### Desconexão

**Evento**: `disconnect`

**Resposta**:
- Evento `user_status` broadcast para todos: `{user_id: 1, status: 'offline'}`

---

### Enviar Mensagem

**Evento**: `send_message`

**Payload**:
```javascript
socket.emit('send_message', {
    receiver_id: 2,
    content: 'Oi, tudo bem?'
});
```

**Resposta**:
- Evento `message_sent` para o remetente
- Evento `new_message` para o destinatário (se online)

---

### Marcar como Lida

**Evento**: `mark_read`

**Payload**:
```javascript
socket.emit('mark_read', {
    message_id: 123
});
```

**Resposta**:
- Evento `message_read` para o remetente original

---

### Digitando (Opcional)

**Evento**: `typing`

**Payload**:
```javascript
socket.emit('typing', {
    receiver_id: 2,
    is_typing: true
});
```

**Resposta**:
- Evento `user_typing` para o destinatário

---

## 🔒 Autenticação JWT

### Como Usar

1. **Obter Token**: Fazer login via `/api/login` ou `/login/google`
2. **Armazenar Token**: Salvar no `localStorage`
3. **Enviar Token**: Incluir em todas as requisições autenticadas

**Exemplo (JavaScript)**:
```javascript
// Armazenar token
localStorage.setItem('token', token);

// Enviar em requisições
fetch('/api/user/profile', {
    headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
    }
});
```

### Expiração

- **Duração**: 24 horas
- **Renovação**: Fazer login novamente

---

## 📊 Códigos de Status HTTP

| Código | Significado                  | Quando Ocorre                          |
|--------|------------------------------|----------------------------------------|
| 200    | OK                           | Requisição bem-sucedida                |
| 201    | Created                      | Recurso criado com sucesso             |
| 400    | Bad Request                  | Dados inválidos ou ausentes            |
| 401    | Unauthorized                 | Token ausente, inválido ou expirado    |
| 403    | Forbidden                    | Sem permissão (não é admin)            |
| 404    | Not Found                    | Recurso não encontrado                 |
| 500    | Internal Server Error        | Erro inesperado no servidor            |

---

**Gerado em**: 01/02/2026  
**Versão**: 1.0  
**Status**: Documentação completa
