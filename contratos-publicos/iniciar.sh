#!/bin/bash
# Lançador para Linux/Mac
# Execute: bash iniciar.sh ou ./iniciar.sh

cd "$(dirname "$0")"

echo "============================================================"
echo "  Monitor de Contratos Públicos - Iniciar"
echo "============================================================"
echo

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "ERRO: Python 3 não encontrado!"
    echo
    echo "Instale Python 3.10 ou superior:"
    echo "  Ubuntu/Debian: sudo apt-get install python3 python3-tk"
    echo "  Fedora/RedHat: sudo dnf install python3 python3-tkinter"
    echo "  macOS: brew install python-tk"
    echo
    read -p "Pressione ENTER para fechar..."
    exit 1
fi

echo "Python encontrado: $(python3 --version)"
echo

# Executar launcher
python3 launcher.pyw

if [ $? -ne 0 ]; then
    echo
    echo "Houve um erro ao iniciar a aplicação."
    echo "Veja logs/app.log para detalhes."
    echo
    read -p "Pressione ENTER para fechar..."
fi
