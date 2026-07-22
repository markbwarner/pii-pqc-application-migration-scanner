package com.example.security;

import java.io.ByteArrayInputStream;
import java.nio.charset.StandardCharsets;
import java.security.KeyStore;
import java.security.PrivateKey;
import java.security.Provider;
import java.security.Security;
import java.security.Signature;
import sun.security.pkcs11.SunPKCS11;
import sun.security.pkcs11.wrapper.CK_MECHANISM;

import static sun.security.pkcs11.wrapper.PKCS11Constants.CKM_RSA_PKCS;

public class ThalesCadpPkcs11Signer {

    public byte[] signPayload(byte[] payload, char[] pin) throws Exception {
        String config = "name=CipherTrustCADPPKCS11\nlibrary=C:/thales/cadp/pkcs11/cadp-pkcs11.dll\nslot=1\nattributes=compatibility\n";
        Provider provider = new SunPKCS11(new ByteArrayInputStream(config.getBytes(StandardCharsets.UTF_8)));
        Security.addProvider(provider);

        String propertyFile = "CADP_PKCS11.properties";
        KeyStore keyStore = KeyStore.getInstance("PKCS11", provider);
        keyStore.load(null, pin);

        PrivateKey signingKey = (PrivateKey) keyStore.getKey("customer-artifact-rsa", pin);
        CK_MECHANISM mechanism = new CK_MECHANISM(CKM_RSA_PKCS);
        Signature signature = Signature.getInstance("SHA256withRSA", provider);
        signature.initSign(signingKey);
        signature.update(payload);

        System.out.println("Loaded " + propertyFile + " with mechanism " + mechanism.mechanism);
        return signature.sign();
    }
}
