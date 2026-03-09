'''O ficheiro logging_config.py é um módulo em Python que configura o sistema de logging para uma aplicação, com um foco especial em logs estruturados em formato JSON, que são ideais para sistemas de observabilidade como o Datadog.'''

import logging
import sys
from pythonjsonlogger import jsonlogger

def setup_logging():
    # Remove o manipulador de log padrão para evitar logs duplicados.
    # Isso é importante porque, sem essa remoção, os logs podem aparecer tanto no formato padrão
    # quanto no formato JSON, poluindo a saída e dificultando a análise.
    if logging.root.handlers:
        for handler in logging.root.handlers:
            logging.root.removeHandler(handler)

    # Configura o logger para capturar todos os logs a partir do nível INFO.
    # O nível INFO é um bom ponto de partida para a maioria das aplicações, pois captura
    # eventos importantes sem gerar um volume excessivo de logs.
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Cria um manipulador de log que envia os logs para a saída padrão (stdout).
    # Em ambientes de contêiner, os logs são normalmente enviados para stdout/stderr,
    # de onde são coletados por ferramentas de agregação de logs.
    log_handler = logging.StreamHandler(sys.stdout)

    # Define o formato do log em JSON, incluindo campos estruturados.
    # O uso de um formato JSON facilita a análise e a consulta dos logs em plataformas
    # de observabilidade, pois cada campo (como timestamp, level, message) pode ser
    # indexado e pesquisado de forma independente.
    formatter = jsonlogger.JsonFormatter(
        '''%(asctime)s %(name)s %(levelname)s %(message)s %(pathname)s %(lineno)d''',
        rename_fields={
            "asctime": "timestamp",
            "levelname": "level",
            "message": "message",
            "name": "logger_name",
            "pathname": "file_path",
            "lineno": "line_number",
        }
    )

    # Associa o formatador JSON ao manipulador de log.
    log_handler.setFormatter(formatter)

    # Adiciona o manipulador configurado ao logger raiz.
    # Isso garante que todos os logs gerados pela aplicação (que não tenham um manipulador
    # específico) sejam processados por este manipulador e formatados como JSON.
    logger.addHandler(log_handler)
