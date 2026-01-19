from flask import Flask, render_template, request, jsonify
import logging

# Configuração básica do logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/')
def index():
    logger.info("Acessando a página inicial.")
    return render_template('index.html')

@app.route('/api/fazer_requisicao', methods=['POST'])
def fazer_requisicao():
    try:
        data = request.get_json()
        acao = data.get('acao', 'desconhecida')
        
        if acao == 'sucesso':
            logger.info("Requisição de sucesso processada.")
            response = {"status": "sucesso", "mensagem": "Ação executada com sucesso!"}
            status_code = 200
        elif acao == 'erro':
            logger.error("Requisição com erro simulado.")
            response = {"status": "erro", "mensagem": "Erro simulado durante a execução da ação."}
            status_code = 500
        else:
            logger.warning(f"Ação desconhecida recebida: {acao}")
            response = {"status": "aviso", "mensagem": f"Ação '{acao}' não reconhecida."}
            status_code = 400

        return jsonify(response), status_code

    except Exception as e:
        logger.exception("Exceção não tratada durante a requisição.")
        return jsonify({"status": "erro", "mensagem": f"Erro interno do servidor: {str(e)}"}), 500

# Removido o bloco if __name__ == '__main__': para usar Gunicorn/wsgi.py
