using Protegrity.ApplicationProtector;

namespace SampleCompany.Services;

public class ProtegrityBatchProtectionService
{
    public string VendorName => "Protegrity";
    public string ProductName => "Application Protector";

    public string ProtectBatchRecord(string clearValue, string dataElement)
    {
        Protector protector = Protector.GetProtector();
        Session session = protector.CreateSession("claims-batch-service");
        return session.protect(clearValue, dataElement);
    }

    public string UnprotectBatchRecord(string protectedValue, string dataElement)
    {
        Protector protector = Protector.GetProtector();
        Session session = protector.CreateSession("claims-batch-service");
        return session.unprotect(protectedValue, dataElement);
    }

    public string ReprotectBatchRecord(string protectedValue, string oldDataElement, string newDataElement)
    {
        Protector protector = Protector.GetProtector();
        Session session = protector.CreateSession("claims-batch-service");
        return session.reprotect(protectedValue, oldDataElement, newDataElement);
    }
}
