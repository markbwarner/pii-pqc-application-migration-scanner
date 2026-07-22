package com.example.security;

import com.safenetinc.luna.provider.LunaProvider;
import java.io.ByteArrayInputStream;
import java.nio.charset.StandardCharsets;
import java.security.KeyStore;
import java.security.Security;

public class LunaKeystoreService {

    public KeyStore openPartitionKeystore(int slot, String password) throws Exception {
        Security.addProvider(new LunaProvider());
        KeyStore keyStore = KeyStore.getInstance("Luna");
        ByteArrayInputStream descriptor = new ByteArrayInputStream(("slot:" + slot).getBytes(StandardCharsets.UTF_8));
        keyStore.load(descriptor, password.toCharArray());
        return keyStore;
    }

    public boolean containsAlias(KeyStore keyStore, String alias) throws Exception {
        return keyStore.containsAlias(alias);
    }
}
