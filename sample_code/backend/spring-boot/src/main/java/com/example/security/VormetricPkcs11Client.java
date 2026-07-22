package com.example.security;

import com.vormetric.pkcs11.sample.Helper;
import com.vormetric.pkcs11.sample.Vpkcs11Session;
import sun.security.pkcs11.wrapper.CK_MECHANISM;

import static sun.security.pkcs11.wrapper.PKCS11Constants.CKM_SHA256_HMAC;

public class VormetricPkcs11Client {

    public byte[] signMessage(byte[] message, String pin, String libraryPath) throws Exception {
        Vpkcs11Session session = Helper.startUp(Helper.getPKCS11LibPath(libraryPath), pin);
        long keyHandle = Helper.findKey(session, "vpkcs11_java_sign_verify_test_key");
        CK_MECHANISM mechanism = new CK_MECHANISM(CKM_SHA256_HMAC);
        session.p11.C_SignInit(session.sessionHandle, mechanism, keyHandle);
        return session.p11.C_Sign(session.sessionHandle, message);
    }
}
