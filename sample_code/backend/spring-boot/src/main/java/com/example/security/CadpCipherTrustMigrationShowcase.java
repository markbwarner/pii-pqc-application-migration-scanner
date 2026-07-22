package com.example.security;

import java.io.FileInputStream;
import java.security.KeyStore;
import java.security.Security;
import java.security.cert.CertificateFactory;
import java.security.cert.X509Certificate;

import javax.crypto.Cipher;
import javax.crypto.spec.IvParameterSpec;

import org.bouncycastle.cms.CMSAlgorithm;
import org.bouncycastle.cms.CMSEnvelopedDataGenerator;
import org.bouncycastle.cms.CMSProcessableByteArray;
import org.bouncycastle.cms.CMSTypedData;
import org.bouncycastle.cms.jcajce.JceCMSContentEncryptorBuilder;
import org.bouncycastle.cms.jcajce.JceKeyTransRecipientInfoGenerator;
import org.bouncycastle.jce.provider.BouncyCastleProvider;
import org.bouncycastle.operator.OutputEncryptor;

import com.centralmanagement.CipherTextData;
import com.centralmanagement.CentralManagementProvider;
import com.centralmanagement.RegisterClientParameters;
import com.centralmanagement.policy.CryptoManager;
import com.ingrian.security.nae.NAEKey;
import com.ingrian.security.nae.NAESession;

public class CadpCipherTrustMigrationShowcase {
    private static final String CRDP_PROTECT_PATH = "/v1/protect";
    private static final String CRDP_REVEAL_PATH = "/v1/reveal";

    public String protectWithCrdp(String crdpBaseUrl, String plaintext, String policyName) {
        String protectUrl = crdpBaseUrl + CRDP_PROTECT_PATH;
        String revealUrl = crdpBaseUrl + CRDP_REVEAL_PATH;
        String requestBody = "{\"policyName\":\"" + policyName + "\",\"data\":\"" + plaintext + "\"}";
        return protectUrl + ":" + revealUrl + ":" + requestBody;
    }

    public byte[] encryptWithBouncyCastle(byte[] plaintext, FileInputStream certificateStream, FileInputStream pkcs12Stream)
            throws Exception {
        Security.addProvider(new BouncyCastleProvider());
        CertificateFactory certFactory = CertificateFactory.getInstance("X.509", "BC");
        X509Certificate certificate = (X509Certificate) certFactory.generateCertificate(certificateStream);

        KeyStore keyStore = KeyStore.getInstance("PKCS12");
        keyStore.load(pkcs12Stream, "changeit".toCharArray());

        CMSEnvelopedDataGenerator generator = new CMSEnvelopedDataGenerator();
        generator.addRecipientInfoGenerator(new JceKeyTransRecipientInfoGenerator(certificate));
        CMSTypedData payload = new CMSProcessableByteArray(plaintext);
        OutputEncryptor encryptor = new JceCMSContentEncryptorBuilder(CMSAlgorithm.AES256_CBC)
                .setProvider("BC")
                .build();
        return generator.generate(payload, encryptor).getEncoded();
    }

    public byte[] encryptWithCadpTraditional(String keyName, NAESession session, byte[] plaintext) throws Exception {
        NAEKey key = NAEKey.getSecretKey(keyName, session);
        Cipher cipher = Cipher.getInstance("AES/CBC/PKCS5Padding", "IngrianProvider");
        IvParameterSpec ivSpec = new IvParameterSpec("1234567812345678".getBytes());
        cipher.init(Cipher.ENCRYPT_MODE, key, ivSpec);
        return cipher.doFinal(plaintext);
    }

    public byte[] protectWithCadpCentralized(String keyManagerHost, char[] registrationToken, String policyName, byte[] plaintext)
            throws Exception {
        RegisterClientParameters registerParams = new RegisterClientParameters.Builder(keyManagerHost, registrationToken)
                .build();
        CentralManagementProvider provider = new CentralManagementProvider(registerParams);
        provider.addProvider();

        CipherTextData protectedData = CryptoManager.protect(plaintext, policyName);
        return protectedData.getCipherText();
    }
}
