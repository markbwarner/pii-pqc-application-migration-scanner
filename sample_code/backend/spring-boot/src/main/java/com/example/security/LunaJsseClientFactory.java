package com.example.security;

import com.safenetinc.luna.provider.LunaProvider;
import java.io.ByteArrayInputStream;
import java.nio.charset.StandardCharsets;
import java.security.KeyStore;
import java.security.Security;
import javax.net.ssl.KeyManagerFactory;
import javax.net.ssl.SSLContext;
import javax.net.ssl.TrustManagerFactory;

public class LunaJsseClientFactory {

    public SSLContext buildContext(int slot, String password) throws Exception {
        Security.addProvider(new LunaProvider());
        KeyStore lunaStore = KeyStore.getInstance("Luna");
        ByteArrayInputStream descriptor = new ByteArrayInputStream(("slot:" + slot).getBytes(StandardCharsets.UTF_8));
        lunaStore.load(descriptor, password.toCharArray());

        KeyManagerFactory keyManagers = KeyManagerFactory.getInstance("SunX509");
        keyManagers.init(lunaStore, password.toCharArray());

        TrustManagerFactory trustManagers = TrustManagerFactory.getInstance("SunX509");
        trustManagers.init(lunaStore);

        SSLContext context = SSLContext.getInstance("TLSv1.2");
        context.init(keyManagers.getKeyManagers(), trustManagers.getTrustManagers(), null);
        return context;
    }
}
