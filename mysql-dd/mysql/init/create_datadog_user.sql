-- =====================================================
-- Script de inicialização do MySQL para Datadog DBM
-- Este script é executado automaticamente quando o
-- container MySQL é criado pela primeira vez.
-- =====================================================

-- Cria database do Datadog (necessário para procedures)
CREATE DATABASE IF NOT EXISTS datadog;

-- =====================================================
-- Cria usuário de monitoramento
-- =====================================================

CREATE USER IF NOT EXISTS 'datadog'@'%' IDENTIFIED BY 'datadog';

-- =====================================================
-- Permissões necessárias para Database Monitoring
-- =====================================================

GRANT SELECT ON *.* TO 'datadog'@'%';
GRANT PROCESS ON *.* TO 'datadog'@'%';
GRANT REPLICATION CLIENT ON *.* TO 'datadog'@'%';
GRANT SELECT ON performance_schema.* TO 'datadog'@'%';

-- =====================================================
-- Procedure necessária para Explain Plans
-- =====================================================

DELIMITER $$

CREATE PROCEDURE datadog.explain_statement(IN stmt TEXT)
SQL SECURITY DEFINER
BEGIN
SET @explain_stmt = CONCAT('EXPLAIN FORMAT=JSON ', stmt);
PREPARE stmt_explain FROM @explain_stmt;
EXECUTE stmt_explain;
DEALLOCATE PREPARE stmt_explain;
END$$

DELIMITER ;

-- Permissão para executar a procedure
GRANT EXECUTE ON PROCEDURE datadog.explain_statement TO 'datadog'@'%';

-- =====================================================
-- Habilita coleta de wait events
-- =====================================================

UPDATE performance_schema.setup_consumers
SET ENABLED = 'YES'
WHERE NAME IN (
'events_waits_current',
'events_waits_history',
'events_waits_history_long'
);

-- =====================================================
-- Aplica alterações
-- =====================================================

FLUSH PRIVILEGES;
