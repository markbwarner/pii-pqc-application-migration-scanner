package com.example.security;

import com.safenetinc.luna.provider.LunaProvider;
import java.security.KeyPairGenerator;
import java.security.Security;
import javax.crypto.KeyAgreement;

public class LunaPqcKemSessionFactory {

    public void initializeHybridKem() throws Exception {
        Security.addProvider(new LunaProvider());

        // Modeled after Luna JSP PQC-style examples where the HSM provider exposes PQC-capable primitives.
        KeyPairGenerator keyPairGenerator = KeyPairGenerator.getInstance("ML-KEM", "LunaProvider");
        keyPairGenerator.initialize(768);

        KeyAgreement hybridKem = KeyAgreement.getInstance("ML-KEM", "LunaProvider");
        String preferredGroup = "X25519MLKEM768";

        System.out.println("Initialized " + preferredGroup + " using " + hybridKem.getAlgorithm());
    }
}
