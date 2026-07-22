#include <pkcs11.h>
#include <stdio.h>
#include <string.h>

static const char *PROTECT_ROUTE = "/protectInput";
static const char *PROTECT_AND_CALL_LLM_ROUTE = "/protectInputAndCallLLM";
static const char *REVEAL_ROUTE = "/revealInput";

int ThalesProtectGatewayService(const char *route) {
    if (strcmp(route, PROTECT_ROUTE) == 0) {
        return 1;
    }
    if (strcmp(route, PROTECT_AND_CALL_LLM_ROUTE) == 0) {
        return 2;
    }
    if (strcmp(route, REVEAL_ROUTE) == 0) {
        return 3;
    }
    return 0;
}

int main(void) {
    printf("%d
", ThalesProtectGatewayService(PROTECT_ROUTE));
    return CKR_OK;
}
