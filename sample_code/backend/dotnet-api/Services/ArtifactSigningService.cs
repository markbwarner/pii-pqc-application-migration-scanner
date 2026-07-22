using System.Security.Cryptography.Pkcs;
using System.Security.Cryptography.X509Certificates;

namespace SampleCompany.Services;

public class ArtifactSigningService
{
    private readonly X509Certificate2 _signingCertificate;

    public ArtifactSigningService(IConfiguration configuration)
    {
        _signingCertificate = new X509Certificate2(
            configuration["Signing:CertificatePath"],
            configuration["Signing:CertificatePassword"]);
    }

    public byte[] SignReleaseManifest(byte[] manifestBytes)
    {
        ContentInfo content = new(manifestBytes);
        SignedCms signedCms = new(content, detached: true);
        CmsSigner signer = new(SubjectIdentifierType.IssuerAndSerialNumber, _signingCertificate);
        signedCms.ComputeSignature(signer);
        return signedCms.Encode();
    }
}
