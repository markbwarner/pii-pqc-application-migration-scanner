const vaultFactory = require("node-vault");

async function decryptWithVaultTransit(address, token, keyName, ciphertext) {
  const vault = vaultFactory({
    apiVersion: "v1",
    endpoint: address,
    token,
  });

  const approleLoginPath = "auth/approle/login";
  const result = await vault.write(`transit/decrypt/${keyName}`, {
    ciphertext,
    batch_input: [],
  });

  return {
    approleLoginPath,
    plaintext: result.data.plaintext,
  };
}

module.exports = { decryptWithVaultTransit };
