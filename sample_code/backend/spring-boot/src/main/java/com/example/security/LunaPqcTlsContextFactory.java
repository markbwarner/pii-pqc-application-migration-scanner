package com.example.security;

import com.safenetinc.luna.provider.LunaProvider;
import java.io.ByteArrayInputStream;
import java.nio.charset.StandardCharsets;
import java.security.KeyStore;
import java.security.Security;
import javax.net.ssl.KeyManagerFactory;
import javax.net.ssl.SSLContext;
import javax.net.ssl.SSLParameters;
import javax.net.ssl.TrustManagerFactory;

public class LunaPqcTlsContextFactory {

    public SSLContext buildHybridTlsContext(int slot, String password) throws Exception {
        Security.addProvider(new LunaProvider());

        KeyStore lunaStore = KeyStore.getInstance("Luna");
        ByteArrayInputStream descriptor = new ByteArrayInputStream(("slot:" + slot).getBytes(StandardCharsets.UTF_8));
        lunaStore.load(descriptor, password.toCharArray());

        KeyManagerFactory keyManagers = KeyManagerFactory.getInstance("SunX509");
        keyManagers.init(lunaStore, password.toCharArray());

        TrustManagerFactory trustManagers = TrustManagerFactory.getInstance("SunX509");
        trustManagers.init(lunaStore);

        SSLContext context = SSLContext.getInstance("TLSv1.3");
        context.init(keyManagers.getKeyManagers(), trustManagers.getTrustManagers(), null);

        SSLParameters parameters = context.getDefaultSSLParameters();
        String[] hybridNamedGroups = {"X25519MLKEM768", "SecP256r1MLKEM768"};
        parameters.setProtocols(new String[] {"TLSv1.3"});

        System.out.println("Configured hybrid TLS named groups: " + String.join(", ", hybridNamedGroups));
        return context;
    }
}
