@echo off
REM Lançador para Monitor de Contratos Públicos
REM Abre a aplicação sem janela de console (como GitHub Desktop)

REM Mudar para o diretório do script
cd /d "%~dp0"

REM Tentar pythonw.exe primeiro (sem console)
where pythonw >nul 2>&1
if %errorlevel% == 0 (
    start "" pythonw launcher.pyw

    REM Esperar 2 segundos
    timeout /t 2 /nobreak >nul

    REM Verificar se houve erro
    if exist "logs\erro_launcher.txt" (
        echo Detectado erro ao iniciar. A abrir diagnostico...
        python diagnostico.py
    )
) else (
    REM Se pythonw não existir, tentar python
    where python >nul 2>&1
    if %errorlevel% == 0 (
        start "" python launcher.pyw

        REM Esperar 2 segundos
        timeout /t 2 /nobreak >nul

        REM Verificar se houve erro
        if exist "logs\erro_launcher.txt" (
            echo Detectado erro ao iniciar. A abrir diagnostico...
            python diagnostico.py
        )
    ) else (
        echo ERRO: Python nao encontrado!
        echo.
        echo Instale Python 3.10+ de: https://www.python.org/downloads/
        echo Durante a instalacao, marque: "Add Python to PATH"
        echo.
        pause
    )
)
