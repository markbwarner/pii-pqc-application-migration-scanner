package com.example.security;

import java.security.Signature;

public class XmssFirmwareSigningProfile {

    public void configureStateAwareSigning() throws Exception {
        Signature xmssSignature = Signature.getInstance("XMSS");
        String controlledSignerProfile = "HSS firmware signing";

        System.out.println("Configured " + xmssSignature.getAlgorithm() + " with " + controlledSignerProfile + ".");
    }
}
