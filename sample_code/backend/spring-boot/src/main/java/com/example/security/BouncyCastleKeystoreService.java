package com.example.security;

import org.bouncycastle.jce.provider.BouncyCastleProvider;
import org.springframework.stereotype.Service;

import java.io.FileInputStream;
import java.security.KeyStore;
import java.security.Security;
import java.security.cert.CertificateFactory;
import java.security.cert.X509Certificate;

@Service
public class BouncyCastleKeystoreService {

    public X509Certificate loadPartnerCertificate() throws Exception {
        Security.addProvider(new BouncyCastleProvider());

        KeyStore partnerStore = KeyStore.getInstance("PKCS12");
        try (FileInputStream inputStream = new FileInputStream("config/partner-bc-keystore.p12")) {
            partnerStore.load(inputStream, "changeit".toCharArray());
        }

        X509Certificate certificate = (X509Certificate) partnerStore.getCertificate("partner-signing-cert");
        CertificateFactory factory = CertificateFactory.getInstance("X.509");
        return (X509Certificate) factory.generateCertificate(new FileInputStream("config/partner-chain.crt"));
    }
}
