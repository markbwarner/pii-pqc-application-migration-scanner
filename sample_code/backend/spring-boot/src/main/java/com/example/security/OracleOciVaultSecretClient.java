package com.example.security;

import com.oracle.bmc.vault.VaultsClient;
import com.oracle.bmc.vault.model.CreateSecretDetails;
import com.oracle.bmc.vault.requests.CreateSecretRequest;
import com.oracle.bmc.vault.requests.GetSecretRequest;

public class OracleOciVaultSecretClient {

    public void manageSecret(VaultsClient client, CreateSecretDetails secretDetails, String secretId) {
        client.createSecret(CreateSecretRequest.builder().createSecretDetails(secretDetails).build());
        client.getSecret(GetSecretRequest.builder().secretId(secretId).build());
    }
}
