import React from "react";

type CertificateStatusPanelProps = {
  currentAlgorithm: string;
  certificateSubject: string;
  certificateExpiresOn: string;
};

export function CertificateStatusPanel(props: CertificateStatusPanelProps) {
  return (
    <section>
      <h2>Certificate Status</h2>
      <div>Signing Algorithm: {props.currentAlgorithm}</div>
      <div>Certificate Subject: {props.certificateSubject}</div>
      <div>Expires On: {props.certificateExpiresOn}</div>
      <div>Next Action: review backend token-signing service for PQC migration.</div>
    </section>
  );
}
