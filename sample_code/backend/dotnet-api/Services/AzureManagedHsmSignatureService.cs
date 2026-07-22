using Azure.Security.KeyVault.Administration;
using Azure.Security.KeyVault.Cryptography;
using Azure.Security.KeyVault.Keys;

namespace SampleCompany.Services;

public class AzureManagedHsmSignatureService
{
    private readonly Uri _managedHsmKeyId = new("https://customer-signing-hsm.managedhsm.azure.net/keys/release-signing-key/abcd1234");

    public CryptographyClient CreateClient()
    {
        return new CryptographyClient(_managedHsmKeyId, new Azure.Identity.DefaultAzureCredential());
    }

    public KeyClient CreateKeyClient()
    {
        return new KeyClient(new Uri("https://customer-signing-hsm.managedhsm.azure.net/"), new Azure.Identity.DefaultAzureCredential());
    }


    public KeyVaultAdministrationClient CreateAdministrationClient()
    {
        return new KeyVaultAdministrationClient(new Uri("https://customer-signing-hsm.managedhsm.azure.net/"), new Azure.Identity.DefaultAzureCredential());
    }
}
