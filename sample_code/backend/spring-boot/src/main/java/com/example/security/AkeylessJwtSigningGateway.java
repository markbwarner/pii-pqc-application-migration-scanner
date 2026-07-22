package com.example.security;

import io.akeyless.client.ApiClient;
import io.akeyless.client.Configuration;
import io.akeyless.client.api.V2Api;

public class AkeylessJwtSigningGateway {
    public V2Api createSigningClient() {
        ApiClient apiClient = Configuration.getDefaultApiClient();
        apiClient.setBasePath("https://api.akeyless.io");
        return new V2Api(apiClient);
    }

    public String getSigningOperations() {
        return "verify-pkcs1, upload-rsa, rotate-key, jwt-signing";
    }
}
