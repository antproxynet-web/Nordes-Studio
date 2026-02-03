# Backend Unificado - Nordes Studio

## 🎯 Visão Geral

Backend Flask profissional e escalável para o Nordes Studio, consolidando as melhores práticas de arquitetura de software.

### ✨ Características Principais

- ✅ **Application Factory Pattern**: Criação modular e testável da aplicação
- ✅ **Blueprints**: Separação clara de responsabilidades por domínio
- ✅ **JWT Authentication**: Autenticação stateless e segura
- ✅ **Google OAuth**: Login social integrado
- ✅ **SocketIO**: Chat em tempo real
- ✅ **Sistema de Verificação**: Badge de verificação para usuários
- ✅ **Senhas com Hash**: Segurança com `werkzeug.security`
- ✅ **CORS Configurado**: Suporte a requisições cross-origin
- ✅ **Error Handlers**: Páginas de erro personalizadas

---

## 📁 Estrutura do Projeto

```
backend/
├── app_unified.py              # ✅ Entrypoint único
├── create_app.py               # ✅ Application Factory
├── config.py                   # ✅ Configurações centralizadas
├── extensions.py               # ✅ Extensões compartilhadas
├── socketio_events.py          # ✅ Eventos SocketIO
│
├── models/                     # 📦 Modelos de dados
│   ├── user.py                # User (com is_verified)
│   ├── book.py                # Book
│   ├── chat.py                # Message, UserStatus
│   └── config.py              # Config (chave-valor)
│
├── routes/                     # 🛣️ Blueprints de rotas
│   ├── auth.py                # Login, signup, OAuth
│   ├── user.py                # Perfil, username, foto
│   ├── books.py               # CRUD de livros
│   ├── chat.py                # API de chat
│   ├── admin_tools.py         # Ferramentas de admin
│   └── static_routes.py       # Servir frontend
│
├── services/                   # 🔧 Lógica de negócio
│   ├── auth_service.py        # Autenticação, JWT
│   ├── user_service.py        # Gerenciamento de usuários
│   └── book_service.py        # Gerenciamento de livros
│
├── utils/                      # 🛠️ Utilitários
│   ├── decorators.py          # token_required, admin_required
│   └── helpers.py             # Funções auxiliares
│
├── migrations/                 # 🗄️ Migrações
│   └── migrate_to_unified.py  # Script de migração
│
└── docs/                       # 📚 Documentação
    ├── ANALISE_PROBLEMAS_ARQUITETURAIS.md
    ├── ARQUITETURA_UNIFICADA.md
    ├── GUIA_MIGRACAO.md
    └── API_CONTRACTS.md
```

---

## 🚀 Como Executar

### 1. Pré-requisitos

- Python 3.8+
- pip
- virtualenv (recomendado)

### 2. Instalação

```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Instalar dependências
pip install -r requirements.txt
```

### 3. Configuração

Criar arquivo `.env` na raiz do projeto:

```env
FLASK_SECRET_KEY=nordes_studio_secret_key_123
GOOGLE_CLIENT_ID=38064533636-ji95u6d97vhsf8rqslu2es271fa15i66.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=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
FLASK_ENV=development
```

### 4. Migração (Primeira Vez)

```bash
# Executar migração do banco de dados
python migrate_to_unified.py
```

### 5. Executar Servidor

```bash
# Executar backend unificado
python app_unified.py
```

**Saída esperada:**
```
============================================================
🚀 Servidor Nordes Studio iniciado
============================================================
📍 URL: http://localhost:5000
🔐 JWT: Autenticação habilitada
💬 SocketIO: Chat em tempo real ativo
🔑 OAuth: Google Login configurado
============================================================

✅ Funcionalidades ativas:
   - Login tradicional (email/senha)
   - Google OAuth
   - Chat em tempo real
   - Validação de username
   - Sistema de verificação
   - Upload de fotos de perfil
============================================================
```

---

## 🔧 Funcionalidades

### 1. Autenticação

#### Login Tradicional
```bash
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "senha123"}'
```

#### Google OAuth
```
http://localhost:5000/login/google
```

### 2. Perfil de Usuário

#### Obter Perfil
```bash
curl -X GET http://localhost:5000/api/user/profile \
  -H "Authorization: Bearer <token>"
```

#### Atualizar Perfil
```bash
curl -X PUT http://localhost:5000/api/user/profile \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "João Silva", "bio": "Desenvolvedor"}'
```

### 3. Chat em Tempo Real

#### Conectar ao SocketIO
```javascript
const socket = io('http://localhost:5000', {
    query: { token: localStorage.getItem('token') }
});

socket.on('connect', () => {
    console.log('Conectado ao chat!');
});
```

#### Enviar Mensagem
```javascript
socket.emit('send_message', {
    receiver_id: 2,
    content: 'Oi, tudo bem?'
});
```

### 4. Sistema de Verificação (Admin)

#### Verificar Usuário
```bash
curl -X POST http://localhost:5000/api/admin/verify-user/2 \
  -H "Authorization: Bearer <token_admin>"
```

---

## 📚 Documentação

### Documentos Principais

1. **[ANALISE_PROBLEMAS_ARQUITETURAIS.md](ANALISE_PROBLEMAS_ARQUITETURAIS.md)**
   - Problemas identificados nos backends antigos
   - Erros arquiteturais a evitar

2. **[ARQUITETURA_UNIFICADA.md](ARQUITETURA_UNIFICADA.md)**
   - Arquitetura detalhada do backend unificado
   - Componentes e responsabilidades

3. **[GUIA_MIGRACAO.md](GUIA_MIGRACAO.md)**
   - Passo a passo para migrar do backend antigo
   - Troubleshooting

4. **[API_CONTRACTS.md](API_CONTRACTS.md)**
   - Documentação completa de todos os endpoints
   - Exemplos de requisições e respostas

---

## 🔐 Segurança

### Boas Práticas Implementadas

- ✅ **Senhas com Hash**: `werkzeug.security.generate_password_hash()`
- ✅ **JWT Stateless**: Autenticação sem sessões no servidor
- ✅ **CORS Configurado**: Apenas origens permitidas
- ✅ **Validação de Entrada**: Whitelist de campos permitidos
- ✅ **Admin Restrito**: Apenas email específico pode ser admin
- ✅ **Upload Seguro**: Validação de tipo e tamanho de arquivo

### Configuração de Admin

Apenas o email `ant.proxy.net@gmail.com` pode ter role `admin`.

Para criar um admin:
```bash
python create_admin.py
```

---

## 🧪 Testes

### Testar Endpoints

```bash
# Instalar pytest
pip install pytest pytest-flask

# Executar testes
pytest tests/
```

### Testar SocketIO

```bash
# Instalar python-socketio[client]
pip install python-socketio[client]

# Executar teste de chat
python test_chat_flow.py
```

---

## 🗄️ Banco de Dados

### SQLite (Desenvolvimento)

- **Localização**: `instance/nordes_studio.db`
- **Backup**: `cp instance/nordes_studio.db instance/nordes_studio.db.backup`

### Migração

```bash
# Adicionar campos is_verified e verified_at
# Migrar senhas para hash
python migrate_to_unified.py
```

### Modelos

- **User**: Usuários do sistema
- **Book**: Livros disponíveis
- **Message**: Mensagens de chat
- **UserStatus**: Status online/offline
- **Config**: Configurações chave-valor
- **Notification**: Notificações
- **HomeLayout**: Layout da home

---

## 🌐 Deploy (Produção)

### 1. Configurar Variáveis de Ambiente

```env
FLASK_ENV=production
FLASK_SECRET_KEY=<chave_secreta_forte>
GOOGLE_CLIENT_ID=<seu_client_id>
GOOGLE_CLIENT_SECRET=<seu_client_secret>
DATABASE_URL=<url_do_banco_producao>
```

### 2. Usar Gunicorn

```bash
# Instalar gunicorn
pip install gunicorn

# Executar com workers
gunicorn -w 4 -b 0.0.0.0:5000 "create_app:create_app('production')"
```

### 3. Usar Nginx (Proxy Reverso)

```nginx
server {
    listen 80;
    server_name nordesstudio.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /socket.io {
        proxy_pass http://127.0.0.1:5000/socket.io;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

---

## 🐛 Troubleshooting

### Problema: Token inválido após migração

**Solução**: Fazer logout e login novamente.

### Problema: OAuth retorna 404

**Solução**: Verificar se as rotas OAuth estão sem prefixo `/api`:
```python
# Correto
@oauth_bp.route('/login/google')

# Errado
@auth_bp.route('/login/google')  # Teria prefixo /api
```

### Problema: SocketIO não conecta

**Solução**: Verificar se o token está sendo enviado:
```javascript
const socket = io('http://localhost:5000', {
    query: { token: localStorage.getItem('token') }
});
```

### Problema: Senhas não funcionam

**Solução**: Executar migração de senhas:
```bash
python migrate_to_unified.py
```

---

## 📊 Estatísticas

### Linhas de Código

| Componente       | Linhas |
|------------------|--------|
| create_app.py    | ~150   |
| socketio_events  | ~150   |
| routes/          | ~800   |
| models/          | ~300   |
| services/        | ~400   |
| **Total**        | ~1800  |

### Endpoints

- **Autenticação**: 5 endpoints
- **Usuário**: 4 endpoints
- **Chat**: 4 endpoints
- **Livros**: 4 endpoints
- **Admin**: 6 endpoints
- **Total**: 23 endpoints

---

## 🎯 Próximos Passos

### Features Planejadas

1. ✅ Sistema de verificação (concluído)
2. ⏭️ Sistema de pagamento Pix
3. ⏭️ Notificações push
4. ⏭️ Sistema de avaliações
5. ⏭️ Recomendações personalizadas
6. ⏭️ API GraphQL (opcional)

### Melhorias Técnicas

1. ⏭️ Testes automatizados (pytest)
2. ⏭️ CI/CD (GitHub Actions)
3. ⏭️ Documentação OpenAPI/Swagger
4. ⏭️ Rate limiting
5. ⏭️ Logging estruturado
6. ⏭️ Monitoramento (Sentry)

---

## 📞 Suporte

Para dúvidas ou problemas:

1. Consultar documentação em `docs/`
2. Verificar logs do servidor
3. Abrir issue no repositório

---

## 📝 Changelog

### v1.0.0 (01/02/2026)

- ✅ Backend unificado criado
- ✅ Application Factory implementada
- ✅ Blueprints organizados
- ✅ JWT authentication
- ✅ Google OAuth funcional
- ✅ SocketIO chat em tempo real
- ✅ Sistema de verificação
- ✅ Migração de senhas para hash
- ✅ Documentação completa

---

## 📄 Licença

Propriedade de Nordes Studio. Todos os direitos reservados.

---

**Desenvolvido com ❤️ pela equipe Nordes Studio**

**Versão**: 1.0.0  
**Data**: 01/02/2026  
**Status**: Produção Ready ✅
