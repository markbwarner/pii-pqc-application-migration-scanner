using CADP.NetCore.Crypto;
using CADP.NetCore.KeyManagement;
using CADP.NetCore.Sessions;
using System;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text;

namespace SampleCompany.Services;

public class ThalesCadpRsaEncryptionService
{
    public byte[] EncryptSamplePayload(string user, string pass, string keyName, string payload)
    {
        string profilePath = ResolveCadpProfilePath();
        NaeSession session = new(user, pass, profilePath);
        NaeKeyManagement keyManagement = new(session);
        NaeRsaKey rsaKey = (NaeRsaKey)keyManagement.GetKey(keyName);
        return rsaKey.Encrypt(Encoding.UTF8.GetBytes(payload), RSAEncryptionPadding.OaepSHA256);
    }

    private static string ResolveCadpProfilePath()
    {
        string home = Environment.GetFolderPath(Environment.SpecialFolder.UserProfile);
        string packageRoot = Path.Combine(home, ".nuget", "packages", "ciphertrust.cadp.netcore");
        string latestVersion = Directory.GetDirectories(packageRoot).Select(Path.GetFileName).OrderBy(name => name).Last() ?? "8.15.0";
        return Path.Combine(packageRoot, latestVersion, "content", "CADP.NETCore_Properties.xml");
    }
}
