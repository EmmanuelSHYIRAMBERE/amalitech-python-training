package com.amalitech.ecslab.controller;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
public class VersionController {

    @GetMapping("/api/version")
    public Map<String, String> version() {
        return Map.of(
                "app", "ecs-lab",
                "version", "1.0.0",
                "student", "Emmanuel Shyirambere"
        );
    }
}
