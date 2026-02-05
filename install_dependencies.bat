@echo off
REM Script para instalar dependências no Windows
REM Este arquivo instala automaticamente todos os pacotes Python necessários

echo.
echo ========================================
echo Instalando dependencias...
echo ========================================
echo.

REM Atualizar pip
python -m pip install --upgrade pip

REM Instalar pacotes
python -m pip install requests psutil ttkbootstrap

echo.
echo ========================================
echo Instalacao concluida!
echo ========================================
echo.
echo Proximos passos:
echo 1. Descarrega o xmrig de:
echo    https://github.com/xmrig/xmrig/releases
echo 2. Extrai na mesma pasta deste script
echo 3. Executa o script Python: python acho.py
echo.
pause
