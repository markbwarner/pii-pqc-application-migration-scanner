package com.example.security;

import com.safenetinc.luna.provider.LunaProvider;
import java.security.KeyPairGenerator;
import java.security.Security;
import javax.crypto.KeyAgreement;

public class LunaHqcKemFallbackService {

    public void prepareFallbackKem() throws Exception {
        Security.addProvider(new LunaProvider());

        KeyPairGenerator backupKemGenerator = KeyPairGenerator.getInstance("HQC", "LunaProvider");
        backupKemGenerator.initialize(256);

        KeyAgreement backupKem = KeyAgreement.getInstance("HQC", "LunaProvider");
        System.out.println("Prepared backup KEM workflow using " + backupKem.getAlgorithm());
    }
}
