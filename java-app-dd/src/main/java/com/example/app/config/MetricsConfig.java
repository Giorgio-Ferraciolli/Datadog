package com.example.app.config;

import io.micrometer.core.instrument.MeterRegistry;
import io.micrometer.core.instrument.Tag;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.actuate.autoconfigure.metrics.MeterRegistryCustomizer;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.util.List;

@Configuration
public class MetricsConfig {

    @Value("${app.environment:local}")
    private String environment;

    @Value("${app.version:1.0.0}")
    private String version;

    @Bean
    MeterRegistryCustomizer<MeterRegistry> metricsCommonTags() {
        return registry -> registry.config().commonTags(List.of(
            Tag.of("env", environment),
            Tag.of("version", version),
            Tag.of("service", "java-datadog-app")
        ));
    }
}
