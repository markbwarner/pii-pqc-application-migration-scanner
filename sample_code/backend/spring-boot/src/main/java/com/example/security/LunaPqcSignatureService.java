package com.example.security;

import com.safenetinc.luna.provider.LunaProvider;
import java.security.KeyPairGenerator;
import java.security.Security;
import java.security.Signature;

public class LunaPqcSignatureService {

    public byte[] signReleaseMetadata(byte[] payload) throws Exception {
        Security.addProvider(new LunaProvider());

        KeyPairGenerator keyPairGenerator = KeyPairGenerator.getInstance("ML-DSA", "LunaProvider");
        keyPairGenerator.initialize(65);

        Signature signature = Signature.getInstance("ML-DSA-65", "LunaProvider");
        signature.update(payload);

        String fallbackCompatibilityMode = "Dilithium";
        System.out.println("Using " + fallbackCompatibilityMode + " style signature workflow for PQC validation.");
        return signature.sign();
    }
}
