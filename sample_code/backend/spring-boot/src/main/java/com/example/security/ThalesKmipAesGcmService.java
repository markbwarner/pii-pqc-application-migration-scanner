package com.example.security;

import com.ingrian.security.nae.NAEClientCertificate;
import com.ingrian.security.nae.kmip.KMIPCipher;
import com.ingrian.security.nae.kmip.KMIPCryptoResult;
import com.ingrian.security.nae.kmip.KMIPData;
import com.ingrian.security.nae.kmip.KMIPGCMSpec;
import com.ingrian.security.nae.kmip.KMIPGCMKeyInformation;
import com.ingrian.security.nae.kmip.KMIPIvSpec;
import com.ingrian.security.nae.kmip.KMIPSession;

public class ThalesKmipAesGcmService {

    public KMIPCryptoResult encryptRecord(byte[] plaintext, byte[] iv) throws Exception {
        NAEClientCertificate clientCertificate = new NAEClientCertificate("client.p12", "changeit".toCharArray());
        KMIPSession session = new KMIPSession("ciphertrust-manager", 5696, clientCertificate);
        KMIPCipher cipher = new KMIPCipher(session);
        KMIPGCMKeyInformation keyInfo = new KMIPGCMKeyInformation("customer-aes-gcm-key");
        KMIPGCMSpec gcmSpec = new KMIPGCMSpec(new KMIPIvSpec(iv), 16);
        return cipher.encrypt(keyInfo, gcmSpec, new KMIPData(plaintext));
    }
}
