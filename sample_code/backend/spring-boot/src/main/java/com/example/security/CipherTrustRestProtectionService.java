package com.example.security;

import com.thales.cm.rest.cmhelper.CipherTrustManagerHelper;

import org.springframework.stereotype.Service;

@Service
public class CipherTrustRestProtectionService {

    private final CipherTrustManagerHelper cipherTrustManagerHelper = new CipherTrustManagerHelper();

    public String protectCustomerRecord(String sensitive) throws Exception {
        cipherTrustManagerHelper.username = "api-user";
        cipherTrustManagerHelper.password = "changeit";
        cipherTrustManagerHelper.cmipaddress = "ciphertrust.example.internal";
        cipherTrustManagerHelper.key = "MyAESEncryptionKey26";

        cipherTrustManagerHelper.getToken();
        return cipherTrustManagerHelper.cmRESTProtect("gcm", sensitive, "encrypt");
    }

    public String revealCustomerRecord(String ciphertext) throws Exception {
        cipherTrustManagerHelper.key = "MyAESEncryptionKey26";
        return cipherTrustManagerHelper.cmRESTProtect("gcm", ciphertext, "decrypt");
    }

    public String signAccountPayload(String payload) throws Exception {
        cipherTrustManagerHelper.key = "rsa-key5";
        return cipherTrustManagerHelper.cmRESTSign("SHA1", "na", payload, "sign");
    }

    public String verifyAccountPayload(String payload, String signature) throws Exception {
        cipherTrustManagerHelper.key = "rsa-key5";
        return cipherTrustManagerHelper.cmRESTSign("SHA1", signature, payload, "signv");
    }

    public String macCustomerMessage(String payload) throws Exception {
        cipherTrustManagerHelper.key = "hmacsha256-1";
        return cipherTrustManagerHelper.cmRESTMac("na", payload, "mac");
    }
}
