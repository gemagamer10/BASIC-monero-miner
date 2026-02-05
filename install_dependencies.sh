#!/bin/bash

# Script para instalar dependências no Linux/Mac
# Este arquivo instala automaticamente todos os pacotes Python necessários

echo ""
echo "========================================"
echo "Instalando dependências..."
echo "========================================"
echo ""

# Atualizar pip
python3 -m pip install --upgrade pip

# Instalar pacotes
python3 -m pip install requests psutil ttkbootstrap

echo ""
echo "========================================"
echo "Instalação concluída!"
echo "========================================"
echo ""
echo "Próximos passos:"
echo "1. Descarrega o xmrig de:"
echo "   https://github.com/xmrig/xmrig/releases"
echo "2. Extrai na mesma pasta deste script"
echo "3. Executa o script Python: python3 acho.py"
echo ""
