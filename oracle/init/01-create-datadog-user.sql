-- Script executado automaticamente na inicialização do Oracle XE
-- Cria o usuário usado pelo Datadog Database Monitoring

ALTER SESSION SET CONTAINER = XEPDB1;

-- cria usuário datadog
CREATE USER datadog IDENTIFIED BY datadog;

-- permissão básica de login
GRANT CREATE SESSION TO datadog;

-- acesso às views necessárias para métricas
GRANT SELECT ON V_$SESSION TO datadog;
GRANT SELECT ON V_$DATABASE TO datadog;
GRANT SELECT ON V_$INSTANCE TO datadog;
GRANT SELECT ON V_$PROCESS TO datadog;
GRANT SELECT ON V_$PARAMETER TO datadog;

-- acesso às queries (Database Monitoring)
GRANT SELECT ON V_$SQL TO datadog;
GRANT SELECT ON V_$SQLSTATS TO datadog;
GRANT SELECT ON V_$SQLAREA TO datadog;
GRANT SELECT ON V_$SQL_PLAN TO datadog;

-- necessário para session sampling
GRANT SELECT ON V_$ACTIVE_SESSION_HISTORY TO datadog;

-- eventos e waits
GRANT SELECT ON V_$SESSION_WAIT TO datadog;
GRANT SELECT ON V_$SYSTEM_EVENT TO datadog;

-- tablespaces
GRANT SELECT ON DBA_TABLESPACES TO datadog;
GRANT SELECT ON DBA_DATA_FILES TO datadog;
GRANT SELECT ON DBA_FREE_SPACE TO datadog;

-- permissão importante para DB Monitoring completo
GRANT SELECT ANY DICTIONARY TO datadog;

-- garante que o usuário pode acessar o PDB
ALTER USER datadog QUOTA UNLIMITED ON USERS;
