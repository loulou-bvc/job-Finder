#!/usr/bin/env python3
"""
Script de lancement pour l'application de gestion d'offres de stage
Vérifie les dépendances et lance l'application
"""

import sys
import subprocess
import os

def check_python_version():
    """Vérifier la version de Python"""
    if sys.version_info < (3, 7):
        print("❌ Python 3.7+ requis")
        print(f"Version actuelle: {sys.version}")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} détecté")
    return True

def install_requirements():
    """Installer les dépendances"""
    requirements_file = os.path.join(os.path.dirname(__file__), "requirements.txt")
    
    if not os.path.exists(requirements_file):
        print("⚠️ Fichier requirements.txt non trouvé")
        return False
    
    try:
        print("📦 Installation des dépendances...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", requirements_file])
        print("✅ Dépendances installées")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur installation: {e}")
        return False

def check_dependencies():
    """Vérifier les dépendances critiques"""
    critical_modules = ['tkinter', 'sqlite3', 'requests', 'beautifulsoup4']
    missing = []
    
    for module in critical_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            print(f"❌ {module} manquant")
            missing.append(module)
    
    return len(missing) == 0

def create_data_directory():
    """Créer le dossier data s'il n'existe pas"""
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print("📁 Dossier data créé")
    else:
        print("✅ Dossier data existe")

def main():
    """Fonction principale"""
    print("🚀 Lancement de l'application de gestion d'offres de stage")
    print("=" * 60)
    
    # Vérifications
    if not check_python_version():
        return
    
    create_data_directory()
    
    if not check_dependencies():
        print("\n📦 Installation des dépendances manquantes...")
        if not install_requirements():
            print("❌ Impossible d'installer les dépendances")
            return
    
    print("\n🎯 Lancement de l'application...")
    
    try:
        # Essayer d'abord l'application complète
        try:
            from main_app_complete import main as app_main
            print("🚀 Lancement de l'application complète...")
            app_main()
        except ImportError:
            # Fallback vers l'application simplifiée
            print("⚠️ Application complète non disponible, lancement de la version simplifiée...")
            from main_app_simple import main as app_main
            app_main()
    except ImportError as e:
        print(f"❌ Erreur d'import: {e}")
        print("Vérifiez que les fichiers d'application existent")
    except Exception as e:
        print(f"❌ Erreur lors du lancement: {e}")

if __name__ == "__main__":
    main()
