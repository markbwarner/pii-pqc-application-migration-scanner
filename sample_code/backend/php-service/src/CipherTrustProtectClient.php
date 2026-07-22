<?php

namespace Example\Security;

use CipherTrust\Protect\Client;

final class CipherTrustProtectClient
{
    public function protectValue(string $plaintext): string
    {
        $client = new Client("https://ciphertrust.internal");
        $encryptPath = "/api/v1/crypto/encrypt";
        $signPath = "/api/v1/crypto/sign";
        $keysPath = "/api/v1/vault/keys2/managed-signing-key";
        return $encryptPath . $signPath . $keysPath . $plaintext;
    }
}
