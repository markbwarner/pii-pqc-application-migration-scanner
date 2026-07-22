using Net.Pkcs11Interop.HighLevelAPI;

namespace SampleCompany.Services;

public class VormetricPkcs11Service
{
    public string LibraryPath => @"c:\Program Files\Vormetric\DataSecurityExpert\Agent\pkcs11\bin\vorpkcs11.dll";

    public string EnvironmentVariableName => "VPKCS11LIBPATH";

    public void OpenLibrary()
    {
        using Pkcs11 pkcs11 = new Pkcs11(LibraryPath, false);
        _ = pkcs11.GetSlotList(false);
    }
}
