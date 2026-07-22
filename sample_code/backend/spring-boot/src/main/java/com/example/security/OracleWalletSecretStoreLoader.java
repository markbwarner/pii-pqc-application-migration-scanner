package com.example.security;

import oracle.security.pki.OracleSecretStore;
import oracle.security.pki.OracleWallet;

public class OracleWalletSecretStoreLoader {

    public String loadSecret(String walletPath, String alias) throws Exception {
        OracleWallet wallet = new OracleWallet();
        wallet.open(walletPath, null);

        OracleSecretStore secretStore = wallet.getSecretStore();
        char[] secretChars = secretStore.getSecret(alias);
        if (secretChars == null) {
            throw new IllegalStateException("Secret alias not found: " + alias);
        }
        String secret = new String(secretChars);
        java.util.Arrays.fill(secretChars, ' ');
        return secret;
    }
}
