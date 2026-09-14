@echo off
title Remote Control Panel
color 0a

echo.
echo  ================================
echo   Remote Control Panel
echo  ================================
echo.

:: Verifica se Python ta instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  [ERRO] Python nao encontrado!
    echo  Baixe em: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo  [OK] Python encontrado
echo  [..] Iniciando servidor...
echo.

:: Inicia o servidor Python em background
start "" /b python "%~dp0backend\server.py"

:: Espera 2 segundos pro servidor subir
timeout /t 2 /nobreak >nul

echo  [OK] Servidor rodando
echo  [..] Abrindo navegador em http://localhost:8081
echo.

:: Abre o navegador no servidor (nao no arquivo)
start "" "http://localhost:8081"

echo  ================================
echo   Nao feche essa janela!
echo   CTRL+C para parar o servidor.
echo  ================================
echo.

:: Agora mostra o servidor no foreground
python "%~dp0backend\server.py"

pause
