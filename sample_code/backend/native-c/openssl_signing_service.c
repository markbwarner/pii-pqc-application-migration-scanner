#include <openssl/evp.h>
#include <openssl/provider.h>

int initialize_signing_provider(void) {
    OSSL_PROVIDER *default_provider = OSSL_PROVIDER_load(NULL, "default");
    EVP_MD_CTX *digest_context = EVP_MD_CTX_new();

    if (default_provider == NULL || digest_context == NULL) {
        EVP_MD_CTX_free(digest_context);
        OSSL_PROVIDER_unload(default_provider);
        return -1;
    }

    EVP_MD_CTX_free(digest_context);
    OSSL_PROVIDER_unload(default_provider);
    return 0;
}
