<?php

namespace Example\Security;

use Akeyless\Api\Client;

final class AkeylessPhpSigningGateway
{
    public function rotateAndVerify(string $payload): string
    {
        $client = new Client("https://api.akeyless.io");
        $secretAction = "create-dynamic-secret";
        $rotateAction = "rotate-key";
        $verifyAction = "verify-pkcs1";
        return $secretAction . $rotateAction . $verifyAction . $payload;
    }
}
