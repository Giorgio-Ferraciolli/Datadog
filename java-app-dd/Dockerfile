# ── Stage 1: Build ────────────────────────────────────────────────────────────
FROM maven:3.9.6-eclipse-temurin-17 AS build

WORKDIR /app
COPY pom.xml .
RUN mvn dependency:go-offline -q
COPY src ./src
RUN mvn clean package -DskipTests -q

# ── Stage 2: Runtime ──────────────────────────────────────────────────────────
FROM eclipse-temurin:17-jre-alpine

WORKDIR /app

ADD https://dtdg.co/latest-java-tracer /app/dd-java-agent.jar

COPY --from=build /app/target/java-datadog-app-1.0.0.jar app.jar

ENV DD_SERVICE=java-datadog-app \
    DD_ENV=production \
    DD_VERSION=1.0.0 \
    DD_LOGS_INJECTION=true \
    DD_TRACE_SAMPLE_RATE=1 \
    DD_AGENT_HOST=datadog-agent \
    DD_TRACE_AGENT_PORT=8126 \
    # Força uso de TCP em vez de socket Unix
    DD_TRACE_AGENT_URL=http://datadog-agent:8126 \
    DD_JMXFETCH_ENABLED=false

EXPOSE 8080

ENTRYPOINT ["java", \
  "-javaagent:/app/dd-java-agent.jar", \
  "-Ddd.service=java-datadog-app", \
  "-Ddd.env=production", \
  "-Ddd.version=1.0.0", \
  "-Ddd.logs.injection=true", \
  "-Ddd.trace.agent.url=http://datadog-agent:8126", \
  "-Ddd.writer.type=DDAgentWriter", \
  "-jar", "app.jar"]