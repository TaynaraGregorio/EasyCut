import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import json
import sys
import os

# Adiciona o diretório atual ao path para permitir importação correta do app
sys.path.append(os.path.dirname(__file__))
# Adiciona o diretório 'backend' (pai da pasta 'tests') ao sys.path
# para que o 'from barbearias_api import app' funcione corretamente.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importa a aplicação Flask do seu projeto
from barbearias_api import app

@pytest.fixture
def client():
    """Fixture que cria um cliente de teste do Flask"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@patch('barbearias_api.get_db_connection')
def test_agendamento_valido(mock_get_db, client):
    """
    RF06 - Teste de Agendamento Válido (Caminho Feliz)
    Verifica se o sistema aceita um agendamento com todos os dados corretos.
    """
    print("\n\n🔵 [TESTE] Iniciando: Agendamento Válido (Caminho Feliz)")

    # --- 1. ARRANGE (PREPARAÇÃO) ---
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_db.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    
    # Simular o ID gerado pelo banco após o insert
    mock_cursor.lastrowid = 101
    
    # Preparar dados do agendamento (Data Futura)
    future_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    payload = {
        'cliente_id': 1,
        'barbearia_id': 1,
        'servico_id': 1,
        'data_agendamento': future_date,
        'horario_inicio': '14:00',
        'valor_total': 50.00,
        'observacoes': 'Teste unitário'
    }
    print(f"   📝 Payload preparado: {payload}")
    
    # --- 2. ACT (EXECUÇÃO) ---
    response = client.post('/api/agendamentos', json=payload)
    data = response.get_json()
    print(f"   📡 Resposta recebida: Status {response.status_code} | Body: {data}")
    
    # --- 3. ASSERT (VERIFICAÇÃO) ---
    assert response.status_code == 200, f"❌ Esperado status 200, mas recebeu {response.status_code}"
    print("   ✅ Status Code 200 OK")

    assert data['success'] is True, "❌ O campo 'success' deveria ser True"
    print("   ✅ Flag 'success' verdadeira")

    assert 'Agendamento realizado com sucesso' in data['message'], "❌ Mensagem de sucesso incorreta"
    print("   ✅ Mensagem de sucesso validada")

    assert data['id'] == 101, f"❌ ID retornado incorreto. Esperado 101, recebeu {data.get('id')}"
    print("   ✅ ID do agendamento retornado corretamente")
    
    # Verificar se o SQL de INSERT foi chamado
    mock_cursor.execute.assert_called_once()
    query_arg = mock_cursor.execute.call_args[0][0]
    assert 'INSERT INTO agendamentos' in query_arg, "❌ A query SQL de INSERT não foi chamada corretamente"
    print("   ✅ Query SQL verificada com sucesso")

def test_agendamento_dados_invalidos_campos_vazios(client):
    """
    RF06 - Teste de Dados Inválidos
    Verifica se o sistema rejeita agendamento faltando campos obrigatórios.
    """
    print("\n\n🟠 [TESTE] Iniciando: Validação de Campos Vazios")

    # --- ARRANGE ---
    # Payload incompleto (sem data, horário e valor)
    payload = {
        'cliente_id': 1,
        'barbearia_id': 1,
        'servico_id': 1
    }
    print(f"   📝 Payload incompleto enviado: {payload}")
    
    # --- ACT ---
    response = client.post('/api/agendamentos', json=payload)
    data = response.get_json()
    print(f"   📡 Resposta recebida: Status {response.status_code}")
    
    # --- ASSERT ---
    assert response.status_code == 400, f"❌ Esperado erro 400, mas recebeu {response.status_code}"
    print("   ✅ Status Code 400 (Bad Request) confirmado")

    assert data['success'] is False, "❌ O campo 'success' deveria ser False para erro"
    
    expected_msg = 'Preencha cliente, barbearia, serviço, data e horário'
    assert expected_msg in data['message'], f"❌ Mensagem de erro esperada: '{expected_msg}'"
    print("   ✅ Mensagem de validação correta")

@patch('barbearias_api.get_db_connection')
def test_agendamento_horario_ocupado(mock_get_db, client):
    """
    RF06 - Teste de Horário Já Ocupado
    Simula o cenário onde o banco de dados rejeita o agendamento por conflito de horário.
    """
    print("\n\n🔴 [TESTE] Iniciando: Simulação de Horário Ocupado (Erro de BD)")

    # --- ARRANGE ---
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_db.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    
    # Simular que o banco lance uma exceção ao tentar inserir (conflito)
    error_msg = "Horário indisponível"
    mock_cursor.execute.side_effect = Exception(error_msg)
    print(f"   🔧 Mock configurado para lançar exceção: '{error_msg}'")
    
    payload = {
        'cliente_id': 1,
        'barbearia_id': 1,
        'servico_id': 1,
        'data_agendamento': '2025-12-25',
        'horario_inicio': '10:00',
        'valor_total': 50.00
    }
    
    # --- ACT ---
    response = client.post('/api/agendamentos', json=payload)
    data = response.get_json()
    print(f"   📡 Resposta recebida: Status {response.status_code}")
    
    # --- ASSERT ---
    assert response.status_code == 500, f"❌ Esperado erro 500, mas recebeu {response.status_code}"
    print("   ✅ Status Code 500 (Erro Interno) confirmado")

    assert data['success'] is False, "❌ O campo 'success' deveria ser False"
    
    assert 'Horário indisponível' in data['message'], "❌ A mensagem de erro da exceção não foi repassada corretamente"
    print("   ✅ O sistema capturou e retornou a exceção do banco corretamente")
    
    # Garante que tentou conectar ao banco antes de falhar
    mock_cursor.execute.assert_called()