#include <openssl/ssl.h>
#include <openssl/err.h>

int configure_tls_context(void) {
    SSL_CTX *context = SSL_CTX_new(TLS_client_method());
    if (context == NULL) {
        ERR_print_errors_fp(stderr);
        return -1;
    }

    SSL_CTX_set_min_proto_version(context, TLS1_2_VERSION);
    SSL_CTX_set_default_verify_paths(context);
    SSL_CTX_free(context);
    return 0;
}
