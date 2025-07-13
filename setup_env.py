import subprocess
import sys
import os

# Crear entorno virtual si no existe
def create_virtualenv():
    if not os.path.exists('.venv'):
        print("Creando entorno virtual...")
        subprocess.run([sys.executable, '-m', 'venv', '.venv'])

# Activar entorno virtual y instalar dependencias
def install_dependencies():
    print("Instalando dependencias...")
    venv_python = os.path.join('.venv', 'Scripts', 'python.exe')
    
    # Instalar pip si es necesario
    subprocess.run([venv_python, '-m', 'ensurepip', '--upgrade'])
    
    # Instalar dependencias desde requirements.txt
    subprocess.run([venv_python, '-m', 'pip', 'install', '-r', 'requirements.txt'])

if __name__ == "__main__":
    create_virtualenv()
    install_dependencies()
    print("\nEntorno configurado correctamente. Puedes ejecutar la aplicación con:")
    print(".venv\\Scripts\\python.exe main.py")
