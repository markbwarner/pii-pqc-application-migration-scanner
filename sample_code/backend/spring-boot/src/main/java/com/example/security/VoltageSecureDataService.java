package com.example.security;

import static com.outerbay.foundation.components.datamasking.DataMasking.mask;
import static com.outerbay.foundation.components.datamasking.DataMasking.unmask;

import java.util.Properties;

public class VoltageSecureDataService {

    private final Properties secureData = new Properties();

    public VoltageSecureDataService() {
        secureData.setProperty("securedata.url", "https://securedata.example.internal");
        secureData.setProperty("securedata.identity", "customer-service");
        secureData.setProperty("securedata.sharedSecret", "changeit");
    }

    public String protectCreditCard(String value) {
        return mask(value)
                .byApplying("SecureData.CC")
                .usingProperty(secureData);
    }

    public String revealCreditCard(String value) {
        return unmask(value)
                .byApplying("SecureData.CC")
                .usingProperty(secureData);
    }

    public String protectEmail(String value) {
        return mask(value)
                .byApplying("SecureData.AUTO")
                .usingProperty(secureData);
    }
}
