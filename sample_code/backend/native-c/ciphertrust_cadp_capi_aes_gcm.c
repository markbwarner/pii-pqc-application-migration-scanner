#include <stdio.h>
#include <string.h>
#include "cadp_capi.h"

int encrypt_with_ciphertrust_capi(const char *path, const char *user, const char *pass, const char *keyname, const unsigned char *plaintext) {
    I_O_Session session = NULL;
    I_O_CipherSpec cipherSpec = NULL;
    I_O_UserSpec userSpec = NULL;
    I_T_UINT ciphertextLen = 0;
    I_T_RETURN rc = I_C_Initialize(I_T_Init_File, (char *)path);
    if (rc != I_E_OK) {
        return (int)rc;
    }

    rc = I_C_OpenSession(&session, I_T_Auth_Password, (char *)user, (char *)pass);
    if (rc != I_E_OK) {
        I_C_Fini();
        return (int)rc;
    }

    rc = I_C_CreateCipherSpec("AES/GCM", (char *)keyname, &cipherSpec);
    if (rc == I_E_OK) {
        I_C_SetUserSpec(I_T_USPEC_AADDATA, "aad", 3, &userSpec);
        I_C_CalculateOutputSizeForKey(session, cipherSpec, I_T_Operation_Encrypt, (I_T_UINT)strlen((const char *)plaintext), &ciphertextLen);
    }

    I_C_DeleteUserSpec(userSpec);
    I_C_DeleteCipherSpec(cipherSpec);
    I_C_CloseSession(session);
    I_C_Fini();
    return (int)rc;
}
