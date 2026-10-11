# TG-001: Core Architecture, Dual-Language Contracts & Capability Flags

> **Taskgroup Identifier:** `AURA-ANYELT-TG-001`  
> **Status:** COMPLETED  
> **Target:** `anyelt/` (Python) & `src/AnyElt.Core/` (C# .NET 10)  

## Scope & Implementation
- Defined `EltCapability` bitmask enum representing 18 fine-grained ELT exploitation features.
- Created typed models: `ImageMetadata`, `ViewportState`, `RadiometricParameters`, `ChipRequest`, `ImageChip`, `MensurationRequest`, `MensurationResult`, `CatalogQuery`, `CatalogItem`, `SpectralSignature`.
- Implemented `IEltAdapter` and `BaseEltAdapter` with built-in capability assertion, geodetic Haversine, forward azimuth, and shadow mensuration math.
- Established error hierarchy: `AnyEltException`, `UnsupportedCapabilityException`, `EltConnectionException`, `ImageNotFoundException`, `MensurationException`, `CatalogQueryException`, `BridgingException`.
