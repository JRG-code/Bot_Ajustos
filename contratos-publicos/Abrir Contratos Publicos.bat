@echo off
REM Lançador para Monitor de Contratos Públicos
REM Abre a aplicação sem janela de console (como GitHub Desktop)

REM Mudar para o diretório do script
cd /d "%~dp0"

REM Tentar pythonw.exe primeiro (sem console)
where pythonw >nul 2>&1
if %errorlevel% == 0 (
    start "" pythonw launcher.pyw
) else (
    REM Se pythonw não existir, tentar python
    where python >nul 2>&1
    if %errorlevel% == 0 (
        start "" python launcher.pyw
    ) else (
        echo ERRO: Python nao encontrado!
        echo.
        echo Instale Python 3.10+ de: https://www.python.org/downloads/
        echo.
        pause
    )
)
