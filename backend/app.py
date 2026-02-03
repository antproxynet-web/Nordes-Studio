"""
Entrypoint da Aplicação Flask - Nordes Studio
Backend unificado com Application Factory, Blueprints e SocketIO
"""
from create_app import create_app, socketio

# Criar aplicação
app = create_app('development')

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Servidor Nordes Studio iniciado")
    print("=" * 60)
    print("📍 URL: http://localhost:5000")
    print("🔐 JWT: Autenticação habilitada")
    print("💬 SocketIO: Chat em tempo real ativo")
    print("🔑 OAuth: Google Login configurado")
    print("=" * 60)
    print()
    print("✅ Funcionalidades ativas:")
    print("   - Login tradicional (email/senha)")
    print("   - Google OAuth")
    print("   - Chat em tempo real")
    print("   - Validação de username")
    print("   - Sistema de verificação")
    print("   - Upload de fotos de perfil")
    print("=" * 60)
    
    socketio.run(app, debug=True, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
