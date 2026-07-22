# Voltage SecureData Reference

This note captures the official references currently used to anchor Voltage or SecureData scanner support.

## Product Family Names

The current OpenText documentation uses names such as:

- `Voltage Fusion`
- `SecureData Appliance`
- `SecureData SimpleAPI`
- `Data Privacy and Protection Appliance (SecureData)`

## References

1. Structured Data Manager compatibility page
   This page lists supported integrations including `Voltage Fusion 25.4`, `Data Privacy and Protection Appliance (SecureData Appliance) 7.0.3`, and `Data Privacy and Protection Simple API (SecureData SimpleAPI) 6.22.0.5`.

2. SecureData integration page
   This page shows concrete SecureData masking and unmasking examples such as:

   - `import static com.outerbay.foundation.components.datamasking.DataMasking.mask`
   - `import static com.outerbay.foundation.components.datamasking.DataMasking.unmask`
   - `.byApplying('SecureData.CC')`
   - `.byApplying('SecureData.AUTO')`
   - `.byApplying('SecureData.ORA-DATE')`
   - `.usingProperty(secureData)`

## Why These Matter For Scanning

These references give us stable, product-specific strings that can appear in application code, configuration, or integration layers and therefore act as useful dependency and implementation markers.

The scanner now uses these references to detect likely Voltage or SecureData related code paths in Java and configuration-style integrations.
