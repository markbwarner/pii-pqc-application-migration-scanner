package com.example.security;

import com.amazonaws.services.kms.AWSKMS;
import com.amazonaws.services.kms.AWSKMSClientBuilder;
import com.amazonaws.services.kms.model.CreateKeyResult;
import com.amazonaws.services.s3.AmazonS3Encryption;
import com.amazonaws.services.s3.AmazonS3EncryptionClientBuilder;
import com.amazonaws.services.s3.model.KMSEncryptionMaterialsProvider;

public class AwsS3KmsEncryptionClient {

    public AmazonS3Encryption createEncryptionClient() {
        AWSKMS kms = AWSKMSClientBuilder.standard().withRegion("us-east-1").build();
        CreateKeyResult keyResult = kms.createKey();
        String kmsKeyId = keyResult.getKeyMetadata().getKeyId();
        KMSEncryptionMaterialsProvider materials = new KMSEncryptionMaterialsProvider(kmsKeyId);
        return AmazonS3EncryptionClientBuilder.standard()
                .withRegion("us-east-1")
                .withEncryptionMaterials(materials)
                .build();
    }
}
