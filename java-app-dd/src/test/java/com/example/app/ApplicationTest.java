package com.example.app;

import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.TestPropertySource;

@SpringBootTest
@TestPropertySource(properties = {
    "management.metrics.export.statsd.enabled=false"
})
class ApplicationTest {

    @Test
    void contextLoads() {
        // Valida que o contexto Spring sobe sem erros
    }
}
