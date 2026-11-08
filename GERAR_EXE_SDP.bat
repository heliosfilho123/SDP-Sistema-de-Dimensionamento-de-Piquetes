@echo off
chcp 65001 > nul
title Gerar executavel do SDP

echo ==========================================
echo       SDP - GERADOR DE EXECUTAVEL
echo ==========================================
echo.

if not exist "SDP.py" (
    echo ERRO: O arquivo SDP.py nao foi encontrado.
    echo Coloque este arquivo .bat na mesma pasta do SDP.py.
    echo.
    pause
    exit /b 1
)

echo [1/3] Verificando Python...
py --version
if errorlevel 1 (
    echo.
    echo ERRO: Python nao encontrado.
    echo Instale o Python para Windows e marque "Add Python to PATH".
    pause
    exit /b 1
)

echo.
echo [2/3] Instalando/atualizando PyInstaller...
py -m pip install --upgrade pyinstaller
if errorlevel 1 (
    echo.
    echo ERRO ao instalar o PyInstaller.
    pause
    exit /b 1
)

echo.
echo [3/3] Gerando SDP.exe...
py -m PyInstaller --noconfirm --clean --onefile --console --name SDP "SDP.py"
if errorlevel 1 (
    echo.
    echo ERRO ao gerar o executavel.
    pause
    exit /b 1
)

echo.
echo ==========================================
echo EXECUTAVEL GERADO COM SUCESSO!
echo Local: pasta dist\SDP.exe
echo ==========================================
echo.
pause
