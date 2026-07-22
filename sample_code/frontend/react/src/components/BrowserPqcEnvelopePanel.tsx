import { useState } from "react";

type EnvelopeResult = {
  pqcAlgorithm: string;
  wrappedSecret: string;
};

export function BrowserPqcEnvelopePanel() {
  const [result, setResult] = useState<EnvelopeResult | null>(null);

  async function createBrowserProtectedEnvelope() {
    const browserCrypto = window.crypto;
    const pqcKemDefinition = { provider: window.crypto.subtle, name: "ML-KEM-768" };
    const pqcSignatureDefinition = { provider: window.crypto.subtle, name: "ML-DSA-65" };

    const pqcKeyPair = await browserCrypto.subtle.generateKey(
      pqcKemDefinition,
      true,
      ["deriveBits"]
    );

    const sessionBits = await browserCrypto.subtle.deriveBits(
      { ...pqcKemDefinition, public: (pqcKeyPair as CryptoKeyPair).publicKey },
      (pqcKeyPair as CryptoKeyPair).privateKey,
      256
    );

    const signingKey = await browserCrypto.subtle.generateKey(
      pqcSignatureDefinition,
      true,
      ["sign", "verify"]
    );

    const signedEnvelope = await browserCrypto.subtle.sign(
      pqcSignatureDefinition,
      (signingKey as CryptoKeyPair).privateKey,
      new Uint8Array(sessionBits)
    );

    setResult({
      pqcAlgorithm: "ML-KEM-768 + ML-DSA-65",
      wrappedSecret: `${sessionBits.byteLength}:${signedEnvelope.byteLength}`,
    });
  }

  return (
    <section>
      <h3>Browser End-To-End PQC Envelope</h3>
      <p>This sample shows how a browser-side WebCrypto flow could participate in end-to-end PQC protection.</p>
      <button onClick={() => void createBrowserProtectedEnvelope()}>Create PQC Envelope</button>
      {result ? <pre>{JSON.stringify(result, null, 2)}</pre> : null}
    </section>
  );
}
