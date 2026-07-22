package com.example.security;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;

public class ThalesCrdpDirectRestService {

    private static final String PROTECT_PATH = "/v2/protect";
    private static final String REVEAL_PATH = "/v2/reveal";
    private static final String PROTECT_BULK_PATH = "/v2/protectbulk";
    private static final String REVEAL_BULK_PATH = "/v2/revealbulk";

    private final HttpClient httpClient = HttpClient.newHttpClient();

    public String protect(String plaintext) throws Exception {
        String payload = "{\"data\":\"" + plaintext + "\"}";
        HttpRequest request = HttpRequest.newBuilder()
            .uri(URI.create("https://ciphertrust.example.internal" + PROTECT_PATH))
            .header("Content-Type", "application/json")
            .POST(HttpRequest.BodyPublishers.ofString(payload))
            .build();
        return httpClient.send(request, HttpResponse.BodyHandlers.ofString()).body();
    }

    public String reveal(String ciphertext) throws Exception {
        String payload = "{\"data\":\"" + ciphertext + "\"}";
        HttpRequest request = HttpRequest.newBuilder()
            .uri(URI.create("https://ciphertrust.example.internal" + REVEAL_PATH))
            .header("Content-Type", "application/json")
            .POST(HttpRequest.BodyPublishers.ofString(payload))
            .build();
        return httpClient.send(request, HttpResponse.BodyHandlers.ofString()).body();
    }

    public String protectBulk(String jsonArrayPayload) throws Exception {
        HttpRequest request = HttpRequest.newBuilder()
            .uri(URI.create("https://ciphertrust.example.internal" + PROTECT_BULK_PATH))
            .header("Content-Type", "application/json")
            .POST(HttpRequest.BodyPublishers.ofString(jsonArrayPayload))
            .build();
        return httpClient.send(request, HttpResponse.BodyHandlers.ofString()).body();
    }

    public String revealBulk(String jsonArrayPayload) throws Exception {
        HttpRequest request = HttpRequest.newBuilder()
            .uri(URI.create("https://ciphertrust.example.internal" + REVEAL_BULK_PATH))
            .header("Content-Type", "application/json")
            .POST(HttpRequest.BodyPublishers.ofString(jsonArrayPayload))
            .build();
        return httpClient.send(request, HttpResponse.BodyHandlers.ofString()).body();
    }
}
