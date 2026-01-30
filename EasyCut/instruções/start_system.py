#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EasyCut - Script de Inicialização
Inicia todos os serviços necessários para o sistema
"""

import subprocess
import sys
import os
import time
import webbrowser
from pathlib import Path

def check_dependencies():
    """Verifica se as dependências estão instaladas"""
    print("🔍 Verificando dependências...")
    
    try:
        import flask
        import flask_cors
        import requests
        import phonenumbers
        import email_validator
        print("✅ Todas as dependências estão instaladas")
        return True
    except ImportError as e:
        print(f"❌ Dependência não encontrada: {e}")
        print("📦 Instalando dependências...")
        
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print("✅ Dependências instaladas com sucesso")
            return True
        except subprocess.CalledProcessError:
            print("❌ Erro ao instalar dependências")
            return False

def start_backend_api():
    """Inicia a API de barbearias"""
    print("🚀 Iniciando API de Barbearias...")
    
    try:
        # Mudar para o diretório backend
        backend_dir = Path(__file__).parent / "backend"
        os.chdir(backend_dir)
        
        # Iniciar o servidor
        process = subprocess.Popen([
            sys.executable, "barbearias_api.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Aguardar um pouco para o servidor inicializar
        time.sleep(3)
        
        # Verificar se o processo ainda está rodando
        if process.poll() is None:
            print("✅ API de Barbearias rodando em http://localhost:5001")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Erro ao iniciar API: {stderr.decode()}")
            return None
            
    except Exception as e:
        print(f"❌ Erro ao iniciar API: {e}")
        return None

def start_validation_api():
    """Inicia a API de validação"""
    print("🚀 Iniciando API de Validação...")
    
    try:
        # Mudar para o diretório backend
        backend_dir = Path(__file__).parent / "backend"
        os.chdir(backend_dir)
        
        # Iniciar o servidor
        process = subprocess.Popen([
            sys.executable, "api_validator.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Aguardar um pouco para o servidor inicializar
        time.sleep(3)
        
        # Verificar se o processo ainda está rodando
        if process.poll() is None:
            print("✅ API de Validação rodando em http://localhost:5000")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Erro ao iniciar API: {stderr.decode()}")
            return None
            
    except Exception as e:
        print(f"❌ Erro ao iniciar API: {e}")
        return None

def open_frontend():
    """Abre o frontend no navegador"""
    print("🌐 Abrindo frontend...")
    
    try:
        frontend_path = Path(__file__).parent / "frontend" / "TelaInicial.html"
        webbrowser.open(f"file://{frontend_path.absolute()}")
        print("✅ Frontend aberto no navegador")
    except Exception as e:
        print(f"❌ Erro ao abrir frontend: {e}")

def main():
    """Função principal"""
    print("=" * 60)
    print("EASYCUT - SISTEMA DE BARBEARIAS")
    print("=" * 60)
    
    # Verificar dependências
    if not check_dependencies():
        print("❌ Não foi possível instalar as dependências")
        return
    
    print("\n" + "=" * 60)
    print("INICIANDO SERVIÇOS")
    print("=" * 60)
    
    # Iniciar APIs
    validation_process = start_validation_api()
    barbearias_process = start_backend_api()
    
    if not validation_process or not barbearias_process:
        print("❌ Erro ao iniciar os serviços")
        return
    
    print("\n" + "=" * 60)
    print("SERVIÇOS INICIADOS COM SUCESSO!")
    print("=" * 60)
    print("📊 APIs disponíveis:")
    print("  • Validação: http://localhost:5000")
    print("  • Barbearias: http://localhost:5001")
    print("\n🌐 Frontend:")
    print("  • Tela Inicial: frontend/TelaInicial.html")
    print("  • Visualizar Barbearias: frontend/VisualizarBarbearias.html")
    print("  • Detalhes da Barbearia: frontend/BarbeariaDetalhes.html")
    
    # Abrir frontend
    time.sleep(2)
    open_frontend()
    
    print("\n" + "=" * 60)
    print("SISTEMA PRONTO PARA USO!")
    print("=" * 60)
    print("💡 Dicas:")
    print("  • Use Ctrl+C para parar os serviços")
    print("  • As APIs ficam rodando em background")
    print("  • Para testar APIs, use: curl http://localhost:5001/api/health")
    
    try:
        # Manter o script rodando
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Parando serviços...")
        if validation_process:
            validation_process.terminate()
        if barbearias_process:
            barbearias_process.terminate()
        print("✅ Serviços parados")

if __name__ == "__main__":
    main()


