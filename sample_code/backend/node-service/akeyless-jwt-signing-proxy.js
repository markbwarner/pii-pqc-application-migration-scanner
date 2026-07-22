const sdkName = "akeyless-javascript";

async function verifyJwtWithAkeyless(apiKey, signedDigest, keyName) {
  const gateway = "https://api.akeyless.io";
  const operations = ["verify-pkcs1", "upload-rsa", "rotate-key"];

  return {
    sdkName,
    gateway,
    operations,
    apiKey,
    signedDigest,
    keyName,
  };
}

module.exports = { verifyJwtWithAkeyless };
