package com.example.security;

public class ProtegrityApplicationProtectorService {

    private final Protector protector = Protector.getProtector();

    public String protectCustomerSsn(String clearValue) throws Exception {
        Session session = protector.createSession("customer-service");
        return session.protect(clearValue, "ssn");
    }

    public String unprotectCustomerSsn(String protectedValue) throws Exception {
        Session session = protector.createSession("customer-service");
        return session.unprotect(protectedValue, "ssn");
    }

    public String reprotectCustomerSsn(String protectedValue) throws Exception {
        Session session = protector.createSession("customer-service");
        return session.reprotect(protectedValue, "ssn", "ssn-rotated");
    }
}
