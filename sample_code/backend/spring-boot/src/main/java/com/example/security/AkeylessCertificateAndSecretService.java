package com.example.security;

import io.akeyless.client.ApiClient;
import io.akeyless.client.Configuration;
import io.akeyless.client.api.V2Api;

public class AkeylessCertificateAndSecretService {
    public V2Api buildClient(String gatewayUrl) {
        ApiClient apiClient = Configuration.getDefaultApiClient();
        apiClient.setBasePath(gatewayUrl + "/api.akeyless.io");
        return new V2Api(apiClient);
    }

    public String describeOperations() {
        return "provision-certificate, create-dynamic-secret, rotate-key, verify-pkcs1";
    }
}
