#!/usr/bin/env python3
"""
Script para criar executável standalone da aplicação
Usa PyInstaller para gerar .exe (Windows), .app (Mac) ou binário (Linux)
"""

import os
import sys
import platform
import subprocess
from pathlib import Path

# Configurações
APP_NAME = "ContratosPublicos"
VERSION = "1.0.0"
AUTHOR = "Monitor Contratos"
DESCRIPTION = "Monitor de Contratos Públicos Portugueses"

# Ícone (será criado se não existir)
ICON_PATH = "assets/icon.ico" if platform.system() == "Windows" else "assets/icon.icns"


def check_pyinstaller():
    """Verifica se PyInstaller está instalado"""
    try:
        import PyInstaller
        return True
    except ImportError:
        print("PyInstaller não encontrado!")
        print("\nPara instalar:")
        print("  pip install pyinstaller")
        return False


def create_icon():
    """Cria ícone básico da aplicação se não existir"""
    assets_dir = Path("assets")
    assets_dir.mkdir(exist_ok=True)

    # Se já existe, não fazer nada
    if Path(ICON_PATH).exists():
        print(f"✓ Ícone encontrado: {ICON_PATH}")
        return ICON_PATH

    print("Criando ícone padrão...")

    try:
        from PIL import Image, ImageDraw, ImageFont

        # Criar imagem 256x256
        size = 256
        img = Image.new('RGB', (size, size), color='#2c3e50')
        draw = ImageDraw.Draw(img)

        # Desenhar círculo azul
        margin = 30
        draw.ellipse([margin, margin, size-margin, size-margin],
                    fill='#3498db', outline='#ecf0f1', width=5)

        # Adicionar texto (iniciais)
        try:
            # Tentar carregar fonte
            font = ImageFont.truetype("arial.ttf", 80)
        except:
            font = ImageFont.load_default()

        text = "CP"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        position = ((size - text_width) // 2, (size - text_height) // 2 - 10)
        draw.text(position, text, fill='white', font=font)

        # Guardar como PNG primeiro
        png_path = assets_dir / "icon.png"
        img.save(png_path, 'PNG')
        print(f"✓ Ícone PNG criado: {png_path}")

        # Converter para formato apropriado
        if platform.system() == "Windows":
            # Converter para ICO
            img.save(assets_dir / "icon.ico", format='ICO', sizes=[(256, 256)])
            print(f"✓ Ícone ICO criado: {assets_dir / 'icon.ico'}")
            return str(assets_dir / "icon.ico")
        elif platform.system() == "Darwin":  # macOS
            # Para Mac, usar PNG (PyInstaller converte)
            return str(png_path)
        else:  # Linux
            return str(png_path)

    except ImportError:
        print("⚠ Pillow não instalado - ícone não será criado")
        print("  Para adicionar ícone: pip install Pillow")
        return None


def get_hidden_imports():
    """Retorna lista de imports que PyInstaller pode não detectar"""
    return [
        'sqlite3',
        'tkinter',
        'tkinter.ttk',
        'tkinter.scrolledtext',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'pandas',
        'openpyxl',
        'requests',
        'bs4',
        'tqdm',
        'datetime',
        'json',
        'csv',
        'pathlib',
    ]


def get_data_files():
    """Retorna lista de ficheiros de dados a incluir"""
    return [
        ('data/exemplo_contratos.csv', 'data'),
        ('README.md', '.'),
        ('QUICK_START.md', '.'),
    ]


def build_spec_file():
    """Cria ficheiro .spec personalizado"""
    icon_path = create_icon()

    hidden_imports = get_hidden_imports()
    datas = get_data_files()

    spec_content = f"""# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Imports ocultos
hiddenimports = {hidden_imports}

# Ficheiros de dados
datas = {datas}

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='{APP_NAME}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # Comprimir executável
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Sem janela de console
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon={repr(icon_path) if icon_path else 'None'},
)

# Para macOS - criar .app bundle
"""

    if platform.system() == "Darwin":
        spec_content += f"""
app = BUNDLE(
    exe,
    name='{APP_NAME}.app',
    icon={repr(icon_path) if icon_path else 'None'},
    bundle_identifier='pt.contratos.monitor',
    info_plist={{
        'NSPrincipalClass': 'NSApplication',
        'NSHighResolutionCapable': 'True',
        'CFBundleName': '{APP_NAME}',
        'CFBundleDisplayName': '{DESCRIPTION}',
        'CFBundleVersion': '{VERSION}',
    }},
)
"""

    spec_path = Path(f"{APP_NAME}.spec")
    spec_path.write_text(spec_content, encoding='utf-8')
    print(f"✓ Ficheiro .spec criado: {spec_path}")
    return spec_path


def build_executable():
    """Constrói o executável"""
    print("""
╔════════════════════════════════════════════════════════════════╗
║     BUILD DE EXECUTÁVEL - CONTRATOS PÚBLICOS                   ║
╚════════════════════════════════════════════════════════════════╝
    """)

    # 1. Verificar PyInstaller
    if not check_pyinstaller():
        return False

    # 2. Criar spec file
    print("\n[1/3] Criando ficheiro de especificação...")
    spec_file = build_spec_file()

    # 3. Executar PyInstaller
    print("\n[2/3] Construindo executável...")
    print("Isto pode demorar alguns minutos...\n")

    try:
        cmd = [
            sys.executable, '-m', 'PyInstaller',
            '--clean',  # Limpar cache anterior
            '--noconfirm',  # Sobrescrever sem perguntar
            str(spec_file)
        ]

        result = subprocess.run(cmd, check=True)

        if result.returncode == 0:
            print("\n✓ Build concluído com sucesso!")

            # 4. Informar localização
            print("\n[3/3] Localização do executável:")

            dist_dir = Path("dist")
            if platform.system() == "Windows":
                exe_path = dist_dir / f"{APP_NAME}.exe"
                print(f"\n  📁 {exe_path.absolute()}")
                print(f"\n  Tamanho: {exe_path.stat().st_size / 1024 / 1024:.1f} MB")
            elif platform.system() == "Darwin":
                app_path = dist_dir / f"{APP_NAME}.app"
                print(f"\n  📁 {app_path.absolute()}")
            else:
                exe_path = dist_dir / APP_NAME
                print(f"\n  📁 {exe_path.absolute()}")
                print(f"\n  Tamanho: {exe_path.stat().st_size / 1024 / 1024:.1f} MB")

            print("\n" + "=" * 64)
            print("INSTRUÇÕES DE USO:")
            print("=" * 64)
            print("\n1. Executável criado na pasta 'dist/'")
            print("2. Pode copiar/mover para qualquer local")
            print("3. Duplo clique para executar")
            print("\n⚠ IMPORTANTE:")
            print("  - A primeira execução pode ser mais lenta")
            print("  - Antivírus pode alertar (é falso positivo)")
            print("  - Base de dados será criada na pasta 'data/'")
            print("\n" + "=" * 64)

            return True

    except subprocess.CalledProcessError as e:
        print(f"\n✗ Erro no build: {e}")
        return False
    except Exception as e:
        print(f"\n✗ Erro inesperado: {e}")
        return False


def create_installer_script():
    """Cria script de instalação (opcional)"""
    if platform.system() == "Windows":
        # Criar script InnoSetup (se disponível)
        iss_content = f"""
; Script gerado automaticamente para Inno Setup
[Setup]
AppName={APP_NAME}
AppVersion={VERSION}
DefaultDirName={{pf}}\\{APP_NAME}
DefaultGroupName={APP_NAME}
OutputDir=installer
OutputBaseFilename={APP_NAME}_Setup
Compression=lzma
SolidCompression=yes

[Files]
Source: "dist\\{APP_NAME}.exe"; DestDir: "{{app}}"; Flags: ignoreversion

[Icons]
Name: "{{group}}\\{APP_NAME}"; Filename: "{{app}}\\{APP_NAME}.exe"
Name: "{{commondesktop}}\\{APP_NAME}"; Filename: "{{app}}\\{APP_NAME}.exe"
        """

        Path("installer_setup.iss").write_text(iss_content, encoding='utf-8')
        print("\n✓ Script de instalador criado: installer_setup.iss")
        print("  Use Inno Setup para criar instalador Windows")


# ==================== ESTIMATIVA DE TAMANHO ====================

def print_size_estimates():
    """Imprime estimativas de tamanho"""
    print("""
╔════════════════════════════════════════════════════════════════╗
║     ESTIMATIVAS DE TAMANHO                                     ║
╚════════════════════════════════════════════════════════════════╝

EXECUTÁVEL:
  • Windows (.exe): ~80-120 MB
  • macOS (.app): ~85-130 MB
  • Linux (binário): ~75-110 MB

  ℹ Inclui Python + todas as bibliotecas + aplicação

BASE DE DADOS (SQLite otimizada):
  • 10.000 contratos: ~5-7 MB
  • 100.000 contratos: ~55-70 MB
  • 500.000 contratos: ~275-350 MB
  • 1.000.000 contratos: ~550-700 MB

  ℹ Com otimização (VACUUM): redução de ~30%

TOTAL ESTIMADO (com 100k contratos):
  • Aplicação: ~100 MB
  • Base de dados: ~60 MB
  • Logs e cache: ~10 MB
  • TOTAL: ~170 MB

💡 DICAS DE OTIMIZAÇÃO:
  • Execute VACUUM regularmente (Menu → Ferramentas)
  • Exporte dados antigos e remova da BD
  • Desative logs verbose em produção
    """)


if __name__ == "__main__":
    print_size_estimates()

    resposta = input("\nDeseja continuar com o build? (s/n): ")

    if resposta.lower() in ['s', 'sim', 'y', 'yes']:
        sucesso = build_executable()

        if sucesso:
            criar_installer = input("\nCriar script de instalador? (s/n): ")
            if criar_installer.lower() in ['s', 'sim']:
                create_installer_script()

        sys.exit(0 if sucesso else 1)
    else:
        print("Build cancelado.")
        sys.exit(0)
