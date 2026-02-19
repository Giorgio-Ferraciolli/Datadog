package com.example.app.controller;

import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.time.LocalDateTime;
import java.util.Map;

@Slf4j
@RestController
@RequestMapping("/api")
public class InfoController {

    @Value("${app.version:1.0.0}")
    private String appVersion;

    @Value("${app.environment:local}")
    private String environment;

    @GetMapping("/info")
    public ResponseEntity<Map<String, Object>> info() {
        log.info("Requisição de info recebida");
        return ResponseEntity.ok(Map.of(
            "app", "java-datadog-app",
            "version", appVersion,
            "environment", environment,
            "timestamp", LocalDateTime.now().toString(),
            "status", "UP"
        ));
    }
}
