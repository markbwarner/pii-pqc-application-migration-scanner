package com.example.security;

import com.thales.crdp.wrapper.ThalesCADPProtectRevealHelper;
import com.thales.crdp.wrapper.ThalesProtectRevealHelper;
import com.thales.crdp.wrapper.ThalesRestProtectRevealHelper;

import java.util.List;
import java.util.Properties;

public class ThalesGcpProtectRevealBatchProcessor {

    private final Properties properties = new Properties();

    public ThalesGcpProtectRevealBatchProcessor() {
        properties.setProperty("KEYMGRHOST", "ciphertrust-manager.example.internal");
        properties.setProperty("CRDPTKN", "registration-token-value");
        properties.setProperty("CRDPIP", "ciphertrust-crdp.example.internal");
        properties.setProperty("POLICYTYPE", "external");
        properties.setProperty("POLICYNAME", "customer-alpha-policy");
        properties.setProperty("REVEALUSER", "batch-processor");
    }

    public void processBatch(List<String> records, boolean useRestHelper) {
        String policyType = properties.getProperty("POLICYTYPE");
        ThalesProtectRevealHelper helper = useRestHelper
                ? new ThalesRestProtectRevealHelper(properties.getProperty("CRDPIP"), "1010000", policyType, true)
                : new ThalesCADPProtectRevealHelper(properties.getProperty("KEYMGRHOST"), properties.getProperty("CRDPTKN"), null, policyType, true);

        helper.revealUser = properties.getProperty("REVEALUSER");
        helper.policyName = properties.getProperty("POLICYNAME");
        helper.defaultPolicy = "customer-fallback-policy";

        for (String record : records) {
            String protectedValue = helper.protectData(record, helper.policyName, policyType);
            helper.revealData(protectedValue, helper.policyName, policyType);
        }
    }
}
