package com.example.security;

import com.amazonaws.encryptionsdk.AwsCrypto;
import com.amazonaws.encryptionsdk.CryptoResult;
import com.amazonaws.encryptionsdk.kms.KmsMasterKeyProvider;
import software.amazon.awssdk.services.kms.KmsClient;
import software.amazon.cryptography.materialproviders.IKeyring;
import software.amazon.cryptography.materialproviders.MaterialProviders;
import software.amazon.cryptography.materialproviders.model.CreateAwsKmsKeyringInput;

public class AwsEncryptionSdkKeyringService {

    public byte[] encrypt(byte[] plaintext, String kmsKeyArn) {
        AwsCrypto crypto = AwsCrypto.standard();
        KmsMasterKeyProvider provider = KmsMasterKeyProvider.builder().buildStrict(kmsKeyArn);

        MaterialProviders materialProviders = MaterialProviders.builder().MaterialProvidersConfig(config -> {}).build();
        IKeyring keyring = materialProviders.CreateAwsKmsKeyring(CreateAwsKmsKeyringInput.builder()
                .kmsKeyId(kmsKeyArn)
                .kmsClient(KmsClient.create())
                .build());

        CryptoResult<byte[], ?> result = crypto.encryptData(provider, plaintext);
        return result.getResult();
    }
}
