#include <openssl/x509.h>
#include <openssl/pem.h>

X509 *load_leaf_certificate(FILE *certificate_file) {
    if (certificate_file == NULL) {
        return NULL;
    }

    return PEM_read_X509(certificate_file, NULL, NULL, NULL);
}
