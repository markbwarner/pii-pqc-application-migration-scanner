package com.example.security;

import com.google.cloud.kms.v1.CreateCryptoKeyRequest;
import com.google.cloud.kms.v1.CryptoKey;
import com.google.cloud.kms.v1.CryptoKeyVersionTemplate;
import com.google.cloud.kms.v1.KeyManagementServiceClient;
import com.google.cloud.kms.v1.KeyRingName;
import com.google.cloud.kms.v1.ProtectionLevel;

public class GcpCloudHsmKeyTemplateService {

    public CryptoKey createHsmSigningKey() throws Exception {
        KeyRingName parent = KeyRingName.of("customer-project", "us-central1", "signing-ring");
        CryptoKeyVersionTemplate versionTemplate = CryptoKeyVersionTemplate.newBuilder()
                .setProtectionLevel(ProtectionLevel.HSM)
                .build();

        CryptoKey key = CryptoKey.newBuilder()
                .setPurpose(CryptoKey.CryptoKeyPurpose.ASYMMETRIC_SIGN)
                .setVersionTemplate(versionTemplate)
                .build();

        CreateCryptoKeyRequest request = CreateCryptoKeyRequest.newBuilder()
                .setParent(parent.toString())
                .setCryptoKeyId("customer-pqc-transition-key")
                .setCryptoKey(key)
                .build();

        try (KeyManagementServiceClient client = KeyManagementServiceClient.create()) {
            return client.createCryptoKey(request);
        }
    }
}
