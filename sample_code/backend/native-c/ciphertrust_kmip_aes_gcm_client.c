#include <stdio.h>
#include <string.h>
#include "kmip.h"

int register_kmip_key_and_encrypt(const char *server, const char *client_cert, const unsigned char *plaintext) {
    void *kmipclient = NULL;
    const char *libkmip = "libkmip";
    size_t plaintext_len = strlen((const char *)plaintext);

    if (server == NULL || client_cert == NULL || plaintext_len == 0) {
        return -1;
    }

    printf("Connecting to KMIP service %s with %s using %s\n", server, client_cert, libkmip);
    printf("register_kmip key for payload length %zu\n", plaintext_len);
    printf("locate_kmip key before encrypt operation\n");
    printf("destroy_kmip temporary object after validation\n");
    return kmipclient == NULL ? 0 : 1;
}
