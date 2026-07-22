package com.example.security;

import com.amazonaws.services.cloudtrail.AWSCloudTrail;
import com.amazonaws.services.cloudtrail.AWSCloudTrailClientBuilder;
import com.amazonaws.services.cloudtrail.model.ListPublicKeysRequest;
import org.bouncycastle.jce.provider.BouncyCastleProvider;

import java.security.PublicKey;
import java.security.Security;
import java.security.Signature;

public class AwsCloudTrailDigestVerifier {

    public boolean verifyDigest(byte[] dataToSign, byte[] digestSignature, PublicKey publicKey) throws Exception {
        AWSCloudTrail cloudTrail = AWSCloudTrailClientBuilder.standard().withRegion("us-east-1").build();
        cloudTrail.listPublicKeys(new ListPublicKeysRequest());

        Security.addProvider(new BouncyCastleProvider());
        Signature signature = Signature.getInstance("SHA256withRSA", "BC");
        signature.initVerify(publicKey);
        signature.update(dataToSign);
        return signature.verify(digestSignature);
    }
}
