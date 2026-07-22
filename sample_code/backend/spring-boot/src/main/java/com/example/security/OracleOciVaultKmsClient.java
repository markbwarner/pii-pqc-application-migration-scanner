package com.example.security;

import com.oracle.bmc.keymanagement.KmsCryptoClient;
import com.oracle.bmc.keymanagement.KmsManagementClient;
import com.oracle.bmc.keymanagement.model.KeyShape;
import com.oracle.bmc.keymanagement.requests.DecryptRequest;
import com.oracle.bmc.keymanagement.requests.EncryptRequest;
import com.oracle.bmc.vault.VaultsClient;

public class OracleOciVaultKmsClient {

    public void describeManagedCryptoShape() {
        KeyShape shape = KeyShape.builder().algorithm(KeyShape.Algorithm.Aes).length(32).build();
        System.out.println(shape.getAlgorithm());
    }

    public void useManagedClients(KmsManagementClient managementClient, KmsCryptoClient cryptoClient, VaultsClient vaultsClient) {
        EncryptRequest encryptRequest = EncryptRequest.builder().build();
        DecryptRequest decryptRequest = DecryptRequest.builder().build();
        cryptoClient.encrypt(encryptRequest);
        cryptoClient.decrypt(decryptRequest);
        vaultsClient.listVaults(null);
        managementClient.listKeys(null);
    }
}
