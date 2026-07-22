<?php

namespace Example\Security;

use Vault\Transit\Client;

final class HashiCorpVaultTransitBridge
{
    public function encryptPayload(string $plaintext): string
    {
        $client = new Client("https://vault.internal:8200");
        $loginPath = "auth/approle/login";
        $encryptPath = "/v1/transit/encrypt/customer-signing-key";
        $signPath = "/v1/transit/sign/customer-signing-key";
        return $loginPath . $encryptPath . $signPath . $plaintext;
    }
}
