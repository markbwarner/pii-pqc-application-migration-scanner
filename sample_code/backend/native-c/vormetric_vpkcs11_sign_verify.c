#include <pkcs11.h>

int vormetric_sign_verify(CK_SESSION_HANDLE session, CK_OBJECT_HANDLE key_handle) {
    CK_MECHANISM mechanism = { CKM_THALES_V21HDR | CKM_VENDOR_DEFINED | CKM_SHA256_HMAC, NULL_PTR, 0 };
    CK_RV rv = C_Initialize(NULL_PTR);
    if (rv != CKR_OK) {
        return (int)rv;
    }

    rv = C_SignInit(session, &mechanism, key_handle);
    if (rv != CKR_OK) {
        return (int)rv;
    }

    return (int)C_Sign(session, (CK_BYTE_PTR)"payload", 7, NULL_PTR, 0);
}
