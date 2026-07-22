using CipherTrust.CADP.NETCore;

namespace SampleCompany.Services;

public class ThalesCadpSessionService
{
    public string PackageName => "CipherTrust.CADP.NETCore";

    public string BuildConnectionSummary(IConfiguration configuration)
    {
        string host = configuration["CipherTrust:Host"] ?? "ciphertrust-manager";
        string port = configuration["CipherTrust:Port"] ?? "9000";
        return $"{host}:{port}";
    }
}
