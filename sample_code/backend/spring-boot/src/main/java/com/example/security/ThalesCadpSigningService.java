package com.example.security;

import com.ingrian.security.nae.IngrianProvider;
import com.ingrian.security.nae.NAEKey;
import com.ingrian.security.nae.NAEPrivateKey;
import com.ingrian.security.nae.NAESession;
import org.springframework.stereotype.Service;

import java.security.Security;
import java.security.Signature;

@Service
public class ThalesCadpSigningService {

    public byte[] signCustomerArtifact(byte[] payload) throws Exception {
        Security.addProvider(new IngrianProvider());

        NAESession session = NAESession.getSession(
                "ciphertrust-user",
                "changeit".toCharArray());

        NAEPrivateKey signingKey = NAEKey.getPrivateKey("customer-artifact-rsa", session);
        Signature signature = Signature.getInstance("SHA256withRSA", "IngrianProvider");
        signature.initSign(signingKey);
        signature.update(payload);
        return signature.sign();
    }
}
