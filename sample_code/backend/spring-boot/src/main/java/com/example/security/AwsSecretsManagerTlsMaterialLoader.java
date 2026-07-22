package com.example.security;

import com.amazonaws.services.secretsmanager.AWSSecretsManager;
import com.amazonaws.services.secretsmanager.AWSSecretsManagerClientBuilder;
import com.amazonaws.services.secretsmanager.model.GetSecretValueRequest;

public class AwsSecretsManagerTlsMaterialLoader {

    public String loadClientCertificatePem(String secretId) {
        AWSSecretsManager client = AWSSecretsManagerClientBuilder.standard()
                .withRegion("us-east-1")
                .build();
        return client.getSecretValue(new GetSecretValueRequest().withSecretId(secretId)).getSecretString();
    }
}
