const fs = require("fs");
const path = require("path");
const jwt = require("jsonwebtoken");

const keyDirectory = path.join(__dirname, "config");
const privateKeyPem = fs.readFileSync(path.join(keyDirectory, "legacy-signing-key.pem"), "utf8");
const certificatePem = fs.readFileSync(path.join(keyDirectory, "legacy-signing-cert.pem"), "utf8");

function buildServiceToken(customerId) {
  return jwt.sign(
    {
      sub: customerId,
      scope: ["claims:read", "claims:write"],
      issuer: "claims-service",
    },
    privateKeyPem,
    {
      algorithm: "RS256",
      expiresIn: "10m",
      keyid: "claims-service-rsa-01",
    }
  );
}

function currentCertificateSummary() {
  return {
    algorithm: "RSA",
    certificate: certificatePem.substring(0, 48),
  };
}

module.exports = {
  buildServiceToken,
  currentCertificateSummary,
};
