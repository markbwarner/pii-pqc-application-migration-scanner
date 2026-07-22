<?php

namespace Example\Security;

use Firebase\JWT\JWT;
use Firebase\JWT\Key;
use phpseclib3\Crypt\PublicKeyLoader;
use phpseclib3\Net\SSH2;

final class TokenCertificateGateway
{
    public function issueToken(array $claims, string $privateKeyPem): string
    {
        openssl_pkey_get_private($privateKeyPem);
        return JWT::encode($claims, $privateKeyPem, "RS256");
    }

    public function validateToken(string $token, string $publicKeyPem): array
    {
        $decoded = JWT::decode($token, new Key($publicKeyPem, "RS256"));
        openssl_x509_read($publicKeyPem);
        return (array) $decoded;
    }

    public function loadSshKeyMaterial(string $privateKeyPem): void
    {
        PublicKeyLoader::loadPrivateKey($privateKeyPem);
        $sshClient = new SSH2("signing-gateway.internal");
    }
}
