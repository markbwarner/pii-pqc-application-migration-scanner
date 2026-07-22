package com.thales.crdp.wrapper;

import com.centralmanagement.CentralManagementProvider;
import com.centralmanagement.CipherTextData;
import com.centralmanagement.RegisterClientParameters;
import com.centralmanagement.policy.CryptoManager;

public class ThalesCADPProtectRevealHelper extends ThalesProtectRevealHelper {

    public ThalesCADPProtectRevealHelper(String keyManagerHost, String registrationToken, String metadata, String policyType, boolean showMetadata) {
        RegisterClientParameters registerClientParameters = new RegisterClientParameters.Builder(
                keyManagerHost,
                registrationToken.toCharArray())
                .build();
        CentralManagementProvider centralManagementProvider = new CentralManagementProvider(registerClientParameters);
        centralManagementProvider.addProvider();
        this.metadata = metadata;
        this.policyType = policyType;
        this.showMetadata = showMetadata;
    }

    @Override
    public String protectData(String plainText, String protectionPolicyName, String policyType) {
        if (!isValid(plainText)) {
            return plainText;
        }
        CipherTextData cipherTextData = CryptoManager.protect(plainText.getBytes(), protectionPolicyName);
        String protectedValue = new String(cipherTextData.getCipherText());
        if (policyType.equalsIgnoreCase("external")) {
            this.metadata = new String(cipherTextData.getVersion());
            return protectedValue;
        }
        this.metadata = protectedValue.substring(0, 7);
        return showMetadata ? protectedValue : parseProtectedValue(protectedValue);
    }

    @Override
    public String revealData(String encryptedData, String protectionPolicyName, String policyType) {
        CipherTextData cipherTextData = new CipherTextData();
        cipherTextData.setCipherText(encryptedData.getBytes());
        if (policyType.equalsIgnoreCase("external") && metadata != null) {
            cipherTextData.setVersion(metadata.getBytes());
        }
        return new String(CryptoManager.reveal(cipherTextData, protectionPolicyName, revealUser));
    }

    public String[] reprotectData(String[] protectedValues, String protectionPolicyName, String policyType) {
        CipherTextData[] cipherTextBatch = new CipherTextData[protectedValues.length];
        for (int i = 0; i < protectedValues.length; i++) {
            cipherTextBatch[i] = new CipherTextData();
            cipherTextBatch[i].setCipherText(protectedValues[i].getBytes());
            if (policyType.equalsIgnoreCase("external") && metadata != null) {
                cipherTextBatch[i].setVersion(metadata.getBytes());
            }
        }
        CipherTextData[] reprotectedBatch = CryptoManager.reprotect(cipherTextBatch, protectionPolicyName);
        String[] results = new String[reprotectedBatch.length];
        for (int i = 0; i < reprotectedBatch.length; i++) {
            results[i] = new String(reprotectedBatch[i].getCipherText());
        }
        return results;
    }
}
