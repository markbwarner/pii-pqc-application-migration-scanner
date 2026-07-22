package com.example.security;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;

public class ThalesCtvlTokenizationService {

    private static final String TOKENIZE_PATH = "/vts/rest/v2.0/tokenize";
    private static final String DETOKENIZE_PATH = "/vts/rest/v2.0/detokenize";

    private final HttpClient httpClient = HttpClient.newHttpClient();

    public String tokenizeAccountNumber(String plaintext) throws Exception {
        String payload = "{\"tokengroup\":\"FF1_Tok_Group\",\"data\":\"" + plaintext + "\",\"tokentemplate\":\"FF1_Tok_Template\"}";
        HttpRequest request = HttpRequest.newBuilder()
            .uri(URI.create("https://VTS_IP_Address" + TOKENIZE_PATH))
            .header("Content-Type", "application/json")
            .POST(HttpRequest.BodyPublishers.ofString(payload))
            .build();
        return httpClient.send(request, HttpResponse.BodyHandlers.ofString()).body();
    }

    public String detokenizeAccountNumber(String token) throws Exception {
        String payload = "{\"tokengroup\":\"FF1_Tok_Group\",\"token\":\"" + token + "\",\"tokentemplate\":\"FF1_Tok_Template\"}";
        HttpRequest request = HttpRequest.newBuilder()
            .uri(URI.create("https://VTS_IP_Address" + DETOKENIZE_PATH))
            .header("Content-Type", "application/json")
            .POST(HttpRequest.BodyPublishers.ofString(payload))
            .build();
        return httpClient.send(request, HttpResponse.BodyHandlers.ofString()).body();
    }
}
