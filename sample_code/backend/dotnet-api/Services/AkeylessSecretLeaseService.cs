namespace SampleCompany.Api.Services;

public class AkeylessSecretLeaseService
{
    public string Gateway => "https://api.akeyless.io";
    public string DotNetSdkMarker => "akeyless-csharp-netcore";

    public string CreateDynamicSecret(string targetName)
    {
        return $"create-dynamic-secret:{targetName}";
    }

    public string UploadRsaKey(string keyName)
    {
        return $"upload-rsa:{keyName}";
    }
}
