package com.example.security;

import com.ingrian.security.nae.IngrianProvider;
import com.ingrian.security.nae.NAEKey;
import com.ingrian.security.nae.NAESession;

import java.security.Security;

public class OracleGoldenGateCipherTrustKeyProvider {

    public byte[] resolveGoldenGateKey(String keyName, String user, char[] password) throws Exception {
        Security.addProvider(new IngrianProvider());
        NAESession session = NAESession.getSession(user, password);
        return NAEKey.getSecretKey(keyName, session).export(true)[0].getKeyData().getBytes();
    }
}
