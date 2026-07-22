#include <pkcs11.h>
#include "cadp/cadp.h"

int sign_with_ciphertrust_slot(CK_SESSION_HANDLE session, CK_OBJECT_HANDLE private_key) {
    CK_MECHANISM mechanism = { CKM_RSA_PKCS, NULL_PTR, 0 };
    CK_RV rv = C_Initialize(NULL_PTR);
    if (rv != CKR_OK) {
        return (int)rv;
    }

    rv = C_OpenSession(1, CKF_SERIAL_SESSION | CKF_RW_SESSION, NULL_PTR, NULL_PTR, &session);
    if (rv != CKR_OK) {
        return (int)rv;
    }

    rv = C_Login(session, CKU_USER, (CK_UTF8CHAR_PTR)"changeit", 8);
    if (rv != CKR_OK) {
        return (int)rv;
    }

    rv = C_SignInit(session, &mechanism, private_key);
    if (rv != CKR_OK) {
        return (int)rv;
    }

    return (int)C_Sign(session, (CK_BYTE_PTR)"payload", 7, NULL_PTR, 0);
}
