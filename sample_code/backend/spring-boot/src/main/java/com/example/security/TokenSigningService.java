package com.example.security;

import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.SignatureAlgorithm;
import org.springframework.stereotype.Service;

import java.io.FileInputStream;
import java.security.KeyStore;
import java.security.PrivateKey;
import java.security.Signature;
import java.security.interfaces.RSAPrivateKey;
import java.security.interfaces.RSAPublicKey;
import java.security.cert.X509Certificate;
import java.time.Instant;
import java.util.Date;

@Service
public class TokenSigningService {

    private final RSAPrivateKey signingKey;
    private final X509Certificate signingCertificate;

    public TokenSigningService() throws Exception {
        KeyStore keyStore = KeyStore.getInstance("PKCS12");
        try (FileInputStream inputStream = new FileInputStream("config/auth-service-keystore.p12")) {
            keyStore.load(inputStream, "changeit".toCharArray());
        }

        this.signingKey = (RSAPrivateKey) keyStore.getKey("auth-service", "changeit".toCharArray());
        this.signingCertificate = (X509Certificate) keyStore.getCertificate("auth-service");
    }

    public String issueCustomerToken(String customerId, String scope) {
        return Jwts.builder()
                .setSubject(customerId)
                .claim("scope", scope)
                .setIssuer("customer-api")
                .setIssuedAt(Date.from(Instant.now()))
                .signWith(signingKey, SignatureAlgorithm.RS256)
                .compact();
    }

    public boolean verifyDetachedSignature(byte[] payload, byte[] detachedSignature) throws Exception {
        Signature verifier = Signature.getInstance("SHA256withRSA");
        verifier.initVerify((RSAPublicKey) signingCertificate.getPublicKey());
        verifier.update(payload);
        return verifier.verify(detachedSignature);
    }

    public PrivateKey exportSigningKeyForLegacyBatchJob() {
        return signingKey;
    }
}
