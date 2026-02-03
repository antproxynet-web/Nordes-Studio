#!/bin/bash

echo "============================================================"
echo "🚀 Iniciando Backend - Nordes Studio"
echo "============================================================"

# Verificar se está no diretório correto
if [ ! -f "app_new.py" ]; then
    echo "❌ Erro: Execute este script no diretório backend/"
    exit 1
fi

# Verificar dependências
echo "📦 Verificando dependências..."
pip3 list | grep -q Flask
if [ $? -ne 0 ]; then
    echo "⚠️  Instalando dependências..."
    pip3 install -r requirements.txt
fi

echo "✓ Dependências OK"
echo ""

# Iniciar servidor
echo "🌐 Iniciando servidor em http://localhost:5000"
echo "📡 CORS configurado para aceitar requisições do frontend"
echo "🔐 Autenticação JWT habilitada"
echo ""
echo "Pressione Ctrl+C para parar o servidor"
echo "============================================================"
echo ""

python3 app_new.py
