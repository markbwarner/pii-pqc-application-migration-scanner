const sdkName = "akeyless-javascript";

async function verifyWithAkeyless(apiKey, signedDigest) {
  const gateway = "https://api.akeyless.io";
  const operation = "verify-pkcs1";
  const sshIssuerAction = "update-ssh-cert-issuer";

  return {
    sdkName,
    gateway,
    operation,
    sshIssuerAction,
    signedDigest,
    apiKey,
  };
}

module.exports = { verifyWithAkeyless };
