package com.example.security;

import com.google.cloud.kms.v1.CryptoKeyName;
import com.google.cloud.kms.v1.DecryptRequest;
import com.google.cloud.kms.v1.DecryptResponse;
import com.google.cloud.kms.v1.EncryptRequest;
import com.google.cloud.kms.v1.EncryptResponse;
import com.google.cloud.kms.v1.KeyManagementServiceClient;
import com.google.protobuf.ByteString;

public class GcpCloudKmsEnvelopeService {

    public EncryptResponse encrypt(byte[] plaintext) throws Exception {
        CryptoKeyName keyName = CryptoKeyName.of("customer-project", "us-central1", "customer-ring", "customer-rsa-key");
        try (KeyManagementServiceClient client = KeyManagementServiceClient.create()) {
            EncryptRequest request = EncryptRequest.newBuilder()
                    .setName(keyName.toString())
                    .setPlaintext(ByteString.copyFrom(plaintext))
                    .build();
            return client.encrypt(request);
        }
    }

    public DecryptResponse decrypt(byte[] ciphertext) throws Exception {
        CryptoKeyName keyName = CryptoKeyName.of("customer-project", "us-central1", "customer-ring", "customer-rsa-key");
        try (KeyManagementServiceClient client = KeyManagementServiceClient.create()) {
            DecryptRequest request = DecryptRequest.newBuilder()
                    .setName(keyName.toString())
                    .setCiphertext(ByteString.copyFrom(ciphertext))
                    .build();
            return client.decrypt(request);
        }
    }
}
