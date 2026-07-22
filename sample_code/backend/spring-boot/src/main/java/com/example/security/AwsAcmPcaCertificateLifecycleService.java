package com.example.security;

import com.amazonaws.services.certificatemanager.AWSCertificateManager;
import com.amazonaws.services.certificatemanager.AWSCertificateManagerClientBuilder;
import com.amazonaws.services.certificatemanager.model.DescribeCertificateRequest;
import com.amazonaws.services.certificatemanager.model.ExportCertificateRequest;
import com.amazonaws.services.acmpca.AWSPCA;
import com.amazonaws.services.acmpca.AWSPCAClientBuilder;
import com.amazonaws.services.acmpca.model.GetCertificateRequest;
import com.amazonaws.services.acmpca.model.IssueCertificateRequest;

public class AwsAcmPcaCertificateLifecycleService {

    public void inspectAndIssue(String certificateArn, String certificateAuthorityArn) {
        AWSCertificateManager acm = AWSCertificateManagerClientBuilder.standard().withRegion("us-east-1").build();
        acm.describeCertificate(new DescribeCertificateRequest().withCertificateArn(certificateArn));
        acm.exportCertificate(new ExportCertificateRequest().withCertificateArn(certificateArn).withPassphrase(java.nio.ByteBuffer.wrap("changeit".getBytes())));

        AWSPCA pca = AWSPCAClientBuilder.standard().withRegion("us-east-1").build();
        pca.issueCertificate(new IssueCertificateRequest().withCertificateAuthorityArn(certificateAuthorityArn));
        pca.getCertificate(new GetCertificateRequest().withCertificateAuthorityArn(certificateAuthorityArn));
    }
}
