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
    
    packages = [
        ('flask', 'flask'),
        ('flask_cors', 'flask-cors'),
        ('requests', 'requests'),
        ('phonenumbers', 'phonenumbers'),
        ('email_validator', 'email-validator'),
        ('mysql.connector', 'mysql-connector-python'),
        ('geopy', 'geopy')
    ]
    
    missing = []
    for import_name, package_name in packages:
        try:
            __import__(import_name)
        except ImportError:
            missing.append(package_name)
    
    if missing:
        print(f"📦 Instalando dependências ausentes: {', '.join(missing)}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing)
            print("✅ Dependências instaladas")
            return True
        except subprocess.CalledProcessError:
            print("❌ Erro ao instalar dependências")
            return False
            
    print("✅ Todas as dependências estão instaladas")
    return True

def start_backend_api():
    """Inicia a API de barbearias"""
    print("🚀 Iniciando API de Barbearias...")
    
    try:
        # Mudar para o diretório backend
        backend_dir = Path(__file__).parent.parent / "backend"
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
        backend_dir = Path(__file__).parent.parent / "backend"
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

def start_frontend_server():
    """Inicia um servidor HTTP simples para o frontend"""
    print("🚀 Iniciando Servidor Frontend...")
    
    try:
        # Mudar para o diretório frontend
        frontend_dir = Path(__file__).parent.parent / "frontend"
        os.chdir(frontend_dir)
        
        # Iniciar servidor Python simples na porta 8000
        # Redirecionamos stdout/stderr para DEVNULL para não poluir o terminal
        process = subprocess.Popen([
            sys.executable, "-m", "http.server", "8000"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        time.sleep(2)
        
        if process.poll() is None:
            print("✅ Frontend rodando em http://localhost:8000")
            return process
        else:
            print("❌ Erro ao iniciar servidor Frontend")
            return None
            
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor Frontend: {e}")
        return None

def open_frontend_url():
    """Abre o frontend no navegador"""
    print("🌐 Abrindo frontend...")
    try:
        webbrowser.open("http://localhost:8000/TelaInicial.html")
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
    frontend_process = start_frontend_server()
    
    if not validation_process or not barbearias_process or not frontend_process:
        print("❌ Erro ao iniciar os serviços")
        return
    
    print("\n" + "=" * 60)
    print("SERVIÇOS INICIADOS COM SUCESSO!")
    print("=" * 60)
    print("📊 APIs disponíveis:")
    print("  • Validação: http://localhost:5000")
    print("  • Barbearias: http://localhost:5001")
    print("\n🌐 Frontend (Acesse por aqui):")
    print("  • http://localhost:8000/TelaInicial.html")
    print("  • http://localhost:8000/CadastroCliente.html")
    print("  • http://localhost:8000/VisualizarBarbearias.html")
    
    # Abrir frontend
    time.sleep(2)
    open_frontend_url()
    
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
        if frontend_process:
            frontend_process.terminate()
        print("✅ Serviços parados")

if __name__ == "__main__":
    main()
