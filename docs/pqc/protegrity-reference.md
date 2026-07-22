# Protegrity Reference

This note captures the official references currently used to anchor Protegrity scanner support.

## Product and API Names

The references used for scanner support come from two Protegrity tracks:

- `Application Protector Java APIs`
- `Protegrity REST APIs`
- `Developer Edition API Service`
- `Protegrity Developer Java` or `ProtegrityDeveloperJava`

## Confirmed References

1. Protegrity Application Protector Java APIs
   The AP Java documentation describes a `Protector` object, session creation, and `protect`, `unprotect`, and `reprotect` methods.

2. Protegrity REST APIs
   The REST docs describe `Policy Management REST APIs` and `Encrypted Resilient Package APIs`.

3. Protegrity Developer Edition API
   The Developer Edition docs describe tokenization and encryption features, Java library builds, and session-oriented protect and unprotect flows.

## Why These Matter For Scanning

These references give the scanner stable strings that can appear in Java, Python, or configuration-driven integrations and indicate an application may depend on a managed tokenization or encryption platform.
