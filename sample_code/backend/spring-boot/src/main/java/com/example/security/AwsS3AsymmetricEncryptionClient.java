package com.example.security;

import com.amazonaws.services.s3.AmazonS3Encryption;
import com.amazonaws.services.s3.AmazonS3EncryptionClientBuilder;
import com.amazonaws.services.s3.model.EncryptionMaterials;
import com.amazonaws.services.s3.model.StaticEncryptionMaterialsProvider;

import java.security.KeyPair;
import java.security.KeyPairGenerator;
import java.security.spec.X509EncodedKeySpec;

public class AwsS3AsymmetricEncryptionClient {

    public AmazonS3Encryption createEncryptionClient() throws Exception {
        KeyPairGenerator keyPairGenerator = KeyPairGenerator.getInstance("RSA");
        keyPairGenerator.initialize(3072);
        KeyPair keyPair = keyPairGenerator.generateKeyPair();
        X509EncodedKeySpec publicKeySpec = new X509EncodedKeySpec(keyPair.getPublic().getEncoded());

        EncryptionMaterials materials = new EncryptionMaterials(keyPair);
        return AmazonS3EncryptionClientBuilder.standard()
                .withEncryptionMaterials(new StaticEncryptionMaterialsProvider(materials))
                .build();
    }
}
