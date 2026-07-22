package com.example.security;

import com.oracle.bmc.certificatesmanagement.CertificatesManagementClient;
import com.oracle.bmc.certificatesmanagement.model.CreateCertificateAuthorityDetails;
import com.oracle.bmc.certificatesmanagement.model.CreateCertificateDetails;
import com.oracle.bmc.certificatesmanagement.requests.CreateCertificateAuthorityRequest;
import com.oracle.bmc.certificatesmanagement.requests.CreateCertificateRequest;
import com.oracle.bmc.certificatesmanagement.requests.GetCertificateAuthorityRequest;

public class OracleOciCertificatesAuthorityService {

    public void manageCertificateAuthority(CertificatesManagementClient client, CreateCertificateAuthorityDetails caDetails, CreateCertificateDetails certDetails, String certificateAuthorityId) {
        client.createCertificateAuthority(CreateCertificateAuthorityRequest.builder().createCertificateAuthorityDetails(caDetails).build());
        client.createCertificate(CreateCertificateRequest.builder().createCertificateDetails(certDetails).build());
        client.getCertificateAuthority(GetCertificateAuthorityRequest.builder().certificateAuthorityId(certificateAuthorityId).build());
    }
}
