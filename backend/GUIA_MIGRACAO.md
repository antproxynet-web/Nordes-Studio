# Guia de Migração para Backend Unificado

## 🎯 Objetivo

Migrar do backend fragmentado (app.py, app_new.py, app_refactored.py) para o **backend unificado** com Application Factory, Blueprints e todas as funcionalidades integradas.

---

## 📋 Pré-requisitos

Antes de iniciar a migração, certifique-se de:

1. ✅ Fazer backup do banco de dados atual
2. ✅ Ter todas as dependências instaladas (`pip install -r requirements.txt`)
3. ✅ Ter as variáveis de ambiente configuradas (`.env`)

---

## 🔄 Passo a Passo

### 1. Backup do Banco de Dados

```bash
# Fazer backup do banco de dados atual
cp instance/nordes_studio.db instance/nordes_studio.db.backup
```

### 2. Executar Script de Migração

```bash
# Executar migração automática
python migrate_to_unified.py
```

**O que o script faz:**
- ✅ Adiciona campos `is_verified` e `verified_at` ao modelo User
- ✅ Converte senhas em texto plano para hash (segurança)
- ✅ Gera usernames para usuários que não têm
- ✅ Exibe estatísticas do banco de dados

**Saída esperada:**
```
============================================================
🔄 Iniciando migração do banco de dados
============================================================

📝 Etapa 1: Verificando campos de verificação...
✅ Campos de verificação adicionados/verificados

📝 Etapa 2: Migrando senhas para hash...
   Migrando senha de user@example.com...
✅ 5 senha(s) migrada(s) para hash

📝 Etapa 3: Verificando usernames...
✅ Todos os usuários já têm username

============================================================
📊 Estatísticas do banco de dados:
============================================================
👥 Total de usuários: 10
✅ Usuários verificados: 0
🔑 Usuários OAuth (sem senha): 2
👑 Administradores: 1

============================================================
✅ Migração concluída com sucesso!
============================================================
```

### 3. Testar o Backend Unificado

```bash
# Executar o backend unificado
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

### 4. Testar Funcionalidades

#### 4.1. Login Tradicional

```bash
# Testar login via API
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "senha123"}'
```

**Resposta esperada:**
```json
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "name": "João Silva",
    "username": "joaosilva",
    "is_verified": false,
    ...
  }
}
```

#### 4.2. Google OAuth

1. Abrir navegador: `http://localhost:5000/login/google`
2. Fazer login com conta Google
3. Verificar redirecionamento para `/pages/home.html?token=...`

#### 4.3. Chat em Tempo Real

1. Conectar ao SocketIO com token JWT
2. Enviar mensagem via evento `send_message`
3. Verificar recebimento via evento `new_message`

#### 4.4. Validação de Username

```bash
# Testar validação de username
curl -X GET "http://localhost:5000/api/user/check-username?username=joaosilva" \
  -H "Authorization: Bearer <seu_token>"
```

**Resposta esperada:**
```json
{
  "available": false,
  "message": "Este nome de usuário já está em uso"
}
```

#### 4.5. Sistema de Verificação (Admin)

```bash
# Verificar usuário (apenas admin)
curl -X POST http://localhost:5000/api/admin/verify-user/1 \
  -H "Authorization: Bearer <token_admin>"
```

**Resposta esperada:**
```json
{
  "message": "Usuário joaosilva verificado com sucesso!",
  "user": {
    "id": 1,
    "username": "joaosilva",
    "is_verified": true,
    "verified_at": "2026-02-01T20:30:00.000Z"
  }
}
```

---

## 🗂️ Arquivos Criados/Modificados

### Novos Arquivos

| Arquivo                  | Descrição                                    |
|--------------------------|----------------------------------------------|
| `create_app.py`          | Application Factory (core da aplicação)     |
| `socketio_events.py`     | Eventos SocketIO (chat em tempo real)        |
| `app_unified.py`         | Entrypoint único (substitui app.py)          |
| `migrate_to_unified.py`  | Script de migração de banco de dados         |

### Arquivos Modificados

| Arquivo                  | Mudanças                                     |
|--------------------------|----------------------------------------------|
| `models/user.py`         | Adicionados campos `is_verified`, `verified_at` |
| `routes/auth.py`         | Separados blueprints `auth_bp` e `oauth_bp`  |
| `routes/admin_tools.py`  | Adicionados endpoints de verificação         |

### Arquivos a Deletar (Após Testes)

| Arquivo                  | Motivo                                       |
|--------------------------|----------------------------------------------|
| `app.py`                 | Substituído por `app_unified.py`             |
| `app_new.py`             | Funcionalidades integradas em `create_app.py`|
| `app_refactored.py`      | Base usada para criar `create_app.py`        |
| `config_app.py`          | Substituído por `config.py`                  |

---

## 🔧 Ajustes no Frontend

### 1. URLs de OAuth

**Antes:**
```javascript
// Login com Google redirecionava para /api/login/google
window.location.href = '/api/login/google';
```

**Depois:**
```javascript
// Agora redireciona para /login/google (SEM /api)
window.location.href = '/login/google';
```

### 2. Exibir Badge de Verificação

```javascript
// Verificar se o usuário é verificado
if (user.is_verified) {
    // Exibir badge de verificação (✓)
    const badge = '<span class="verified-badge">✓</span>';
    usernameElement.innerHTML = user.username + badge;
}
```

### 3. Validação de Username em Tempo Real

```javascript
// Validar username enquanto o usuário digita
const usernameInput = document.getElementById('username');

usernameInput.addEventListener('input', async (e) => {
    const username = e.target.value;
    
    if (username.length < 3) return;
    
    const response = await fetch(`/api/user/check-username?username=${username}`, {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    });
    
    const data = await response.json();
    
    if (data.available) {
        // Username disponível
        usernameInput.classList.add('valid');
        usernameInput.classList.remove('invalid');
    } else {
        // Username indisponível
        usernameInput.classList.add('invalid');
        usernameInput.classList.remove('valid');
        showError(data.message);
    }
});
```

---

## 🚨 Problemas Comuns e Soluções

### 1. Erro: "Token inválido ou expirado"

**Causa**: Senhas foram migradas para hash, mas o token foi gerado com senha em texto plano.

**Solução**:
```bash
# Fazer logout e login novamente
# O novo login gerará um token válido
```

### 2. Erro: "OAuth não configurado"

**Causa**: Variáveis de ambiente `GOOGLE_CLIENT_ID` ou `GOOGLE_CLIENT_SECRET` não estão definidas.

**Solução**:
```bash
# Verificar arquivo .env
cat .env | grep GOOGLE

# Se não existir, adicionar:
echo "GOOGLE_CLIENT_ID=38064533636-ji95u6d97vhsf8rqslu2es271fa15i66.apps.googleusercontent.com" >> .env
echo "GOOGLE_CLIENT_SECRET=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" >> .env
```

### 3. Erro: "SocketIO connection failed"

**Causa**: Token JWT não está sendo enviado na conexão WebSocket.

**Solução**:
```javascript
// Frontend: Conectar ao SocketIO com token
const socket = io('http://localhost:5000', {
    query: {
        token: localStorage.getItem('token')
    }
});
```

### 4. Erro: "User não encontrado" após OAuth

**Causa**: Usuário foi criado mas não tem username.

**Solução**:
```bash
# Executar migração novamente
python migrate_to_unified.py
```

---

## 📊 Checklist de Migração

- [ ] Backup do banco de dados criado
- [ ] Script de migração executado com sucesso
- [ ] Backend unificado iniciado sem erros
- [ ] Login tradicional testado e funcionando
- [ ] Google OAuth testado e funcionando
- [ ] Chat em tempo real testado e funcionando
- [ ] Validação de username testada e funcionando
- [ ] Sistema de verificação testado (admin)
- [ ] Frontend ajustado para novas URLs OAuth
- [ ] Arquivos antigos deletados (app.py, app_new.py, app_refactored.py)

---

## 🎉 Próximos Passos

Após a migração bem-sucedida:

1. **Documentar contratos de API** (ver `ARQUITETURA_UNIFICADA.md`)
2. **Configurar ambiente de produção** (usar `ProductionConfig`)
3. **Implementar testes automatizados** (pytest)
4. **Configurar CI/CD** (GitHub Actions, GitLab CI)
5. **Implementar sistema de pagamento Pix** (próxima feature)

---

## 📞 Suporte

Se encontrar problemas durante a migração:

1. Verificar logs do servidor (`python app_unified.py`)
2. Consultar `ANALISE_PROBLEMAS_ARQUITETURAIS.md`
3. Consultar `ARQUITETURA_UNIFICADA.md`
4. Restaurar backup do banco de dados se necessário

---

**Gerado em**: 01/02/2026  
**Versão**: 1.0  
**Status**: Pronto para uso
