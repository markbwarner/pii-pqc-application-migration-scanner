using Azure.Security.KeyVault.Cryptography;

namespace SampleCompany.Services;

public class ThalesProtectGatewayService
{
    private readonly CryptographyClient _cryptographyClient;
    private const string ProtectRoute = "/protectInput";
    private const string ProtectAndCallLlmRoute = "/protectInputAndCallLLM";
    private const string RevealRoute = "/revealInput";

    public ThalesProtectGatewayService(CryptographyClient cryptographyClient)
    {
        _cryptographyClient = cryptographyClient;
    }

    public string AuthenticateRequest(string authorizationHeader)
    {
        return string.IsNullOrWhiteSpace(authorizationHeader) ? "missing" : "ok";
    }

    public string ProtectInput() => ProtectRoute;

    public string ProtectInputAndCallLLM() => ProtectAndCallLlmRoute;

    public string RevealInput() => RevealRoute;
}
