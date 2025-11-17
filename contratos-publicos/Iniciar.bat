@echo off
REM Lançador para Windows
REM Duplo clique neste ficheiro para iniciar a aplicação

cd /d "%~dp0"

echo ============================================================
echo   Monitor de Contratos Publicos - Iniciar
echo ============================================================
echo.

REM Tentar encontrar Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERRO: Python nao encontrado!
    echo.
    echo Instale Python 3.10 ou superior de python.org
    echo.
    pause
    exit /b 1
)

REM Executar launcher
python launcher.pyw

if %errorlevel% neq 0 (
    echo.
    echo Houve um erro ao iniciar a aplicacao.
    echo Veja logs/app.log para detalhes.
    echo.
    pause
)
