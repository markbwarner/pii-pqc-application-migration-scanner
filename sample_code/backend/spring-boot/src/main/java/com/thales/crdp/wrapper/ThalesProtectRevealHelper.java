package com.thales.crdp.wrapper;

public abstract class ThalesProtectRevealHelper {

    protected String metadata;
    protected String policyType;
    protected boolean showMetadata = true;
    protected String policyName;
    protected String revealUser;
    protected String defaultPolicy;

    public abstract String protectData(String plainText, String protectionPolicyName, String policyType);

    public abstract String revealData(String encryptedData, String protectionPolicyName, String policyType);

    public String parseProtectedValue(String protectedValue) {
        this.metadata = protectedValue.substring(0, 7);
        return protectedValue.substring(7);
    }

    protected boolean isValid(String value) {
        return value != null && value.length() >= 2;
    }
}
