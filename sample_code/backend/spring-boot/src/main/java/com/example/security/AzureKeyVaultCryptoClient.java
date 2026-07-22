package com.example.security;

import com.microsoft.azure.keyvault.KeyVaultClient;
import com.microsoft.azure.keyvault.KeyVaultClientService;
import com.microsoft.azure.keyvault.KeyVaultConfiguration;
import com.microsoft.azure.keyvault.authentication.KeyVaultCredentials;
import com.microsoft.azure.keyvault.models.KeyOperationResult;
import com.microsoft.azure.keyvault.webkey.JsonWebKeyEncryptionAlgorithm;
import com.microsoft.windowsazure.Configuration;

public class AzureKeyVaultCryptoClient {

    public KeyVaultClient createClient(KeyVaultCredentials credentials) {
        Configuration configuration = KeyVaultConfiguration.configure(null, credentials);
        return KeyVaultClientService.create(configuration);
    }

    public KeyOperationResult encrypt(KeyVaultClient client, String keyIdentifier, byte[] plaintext) throws Exception {
        return client.encryptAsync(keyIdentifier, JsonWebKeyEncryptionAlgorithm.RSAOAEP, plaintext).get();
    }

    public KeyOperationResult decrypt(KeyVaultClient client, String keyIdentifier, byte[] ciphertext) throws Exception {
        return client.decryptAsync(keyIdentifier, "RSA-OAEP", ciphertext).get();
    }
}
