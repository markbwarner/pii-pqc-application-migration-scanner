package com.example.security;

import com.oracle.bmc.certificates.CertificatesClient;
import com.oracle.bmc.certificates.requests.GetCaBundleRequest;
import com.oracle.bmc.certificates.requests.GetCertificateAuthorityBundleRequest;

public class OracleOciCertificatesBundleClient {

    public void fetchBundles(CertificatesClient client, String caBundleId, String certificateAuthorityId) {
        client.getCaBundle(GetCaBundleRequest.builder().caBundleId(caBundleId).build());
        client.getCertificateAuthorityBundle(GetCertificateAuthorityBundleRequest.builder().certificateAuthorityId(certificateAuthorityId).build());
    }
}
