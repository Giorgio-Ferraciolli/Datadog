# === Arquivo: api_monitor.py ===
#!/usr/bin/env python3
"""
Script para consultar API periodicamente e armazenar resultados
"""
import requests
import json
import sqlite3
from datetime import datetime
import logging
import sys
import time

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/api_monitor.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Lista de endpoints para consultar
API_ENDPOINTS = [
    "https://jsonplaceholder.typicode.com/posts",
    "https://jsonplaceholder.typicode.com/users",
    "https://jsonplaceholder.typicode.com/comments"
]

# Caminho do banco de dados
DB_PATH = "/app/data/api_data.db"

def criar_tabela():
    """Cria a tabela no banco de dados se não existir"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS api_responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            endpoint TEXT,
            status_code INTEGER,
            response_data TEXT,
            records_count INTEGER,
            success BOOLEAN
        )
    ''')
    
    conn.commit()
    conn.close()
    logging.info("Tabela verificada/criada com sucesso")

def consultar_api(url):
    """Consulta a API e retorna a resposta"""
    try:
        logging.info(f"Consultando API: {url}")
        response = requests.get(url, timeout=30)
        
        data = response.json() if response.ok else response.text
        records_count = len(data) if isinstance(data, list) else 1
        
        return {
            'endpoint': url,
            'status_code': response.status_code,
            'data': data,
            'records_count': records_count,
            'success': response.ok
        }
    
    except requests.exceptions.RequestException as e:
        logging.error(f"Erro ao consultar API {url}: {str(e)}")
        return {
            'endpoint': url,
            'status_code': 0,
            'data': {'error': str(e)},
            'records_count': 0,
            'success': False
        }

def salvar_resultado(resultado):
    """Salva o resultado no banco de dados"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO api_responses (endpoint, status_code, response_data, records_count, success)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            resultado['endpoint'],
            resultado['status_code'],
            json.dumps(resultado['data'], ensure_ascii=False)[:5000],  # Limita tamanho
            resultado['records_count'],
            resultado['success']
        ))
        
        conn.commit()
        conn.close()
        logging.info(f"Resultado salvo - {resultado['records_count']} registros")
        
    except Exception as e:
        logging.error(f"Erro ao salvar no banco: {str(e)}")

def main():
    """Função principal"""
    logging.info("=== Script iniciado - Loop a cada 30 segundos ===")
    
    # Cria a tabela se não existir
    criar_tabela()
    
    # Loop infinito executando a cada 30 segundos
    while True:
        try:
            logging.info("--- Nova consulta iniciada ---")
            
            # Consulta todos os endpoints
            for endpoint in API_ENDPOINTS:
                resultado = consultar_api(endpoint)
                salvar_resultado(resultado)
                
                if resultado['success']:
                    logging.info(f"✓ {endpoint} - Status: {resultado['status_code']} - Registros: {resultado['records_count']}")
                else:
                    logging.warning(f"✗ {endpoint} - Falhou - Status: {resultado['status_code']}")
                
                time.sleep(1)  # Pequeno delay entre requisições
            
            logging.info("--- Consulta finalizada - Aguardando 30 segundos ---\n")
            time.sleep(30)  # Aguarda 30 segundos antes da próxima execução
            
        except KeyboardInterrupt:
            logging.info("Script interrompido pelo usuário")
            break
        except Exception as e:
            logging.error(f"Erro no loop principal: {str(e)}")
            time.sleep(30)  # Aguarda mesmo em caso de erro

if __name__ == "__main__":
    main()