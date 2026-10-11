"""
AnyElt Exception Hierarchy.
Strongly typed exceptions for error resilience in Synapse-GEOINT pipelines.
"""


class AnyEltException(Exception):
    """Base exception for all AnyElt operations."""
    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class UnsupportedCapabilityException(AnyEltException):
    """Raised when an operation is attempted on an adapter that does not support the capability."""
    def __init__(self, adapter_name: str, capability_name: str, message: str | None = None):
        msg = message or f"ELT adapter '{adapter_name}' does not support capability '{capability_name}'."
        super().__init__(msg, {"adapter": adapter_name, "capability": capability_name})


class EltConnectionException(AnyEltException):
    """Raised when an ELT fails to connect or disconnect."""
    def __init__(self, adapter_name: str, message: str, inner_exception: Exception | None = None):
        super().__init__(f"Failed to connect to ELT '{adapter_name}': {message}", {
            "adapter": adapter_name,
            "inner_exception": str(inner_exception) if inner_exception else None
        })


class ImageNotFoundException(AnyEltException):
    """Raised when an image URI cannot be resolved or loaded."""
    def __init__(self, uri: str, message: str | None = None):
        super().__init__(message or f"Image not found or unreadable: {uri}", {"uri": uri})


class MensurationException(AnyEltException):
    """Raised when a mensuration calculation fails due to missing sensor geometry or invalid parameters."""
    def __init__(self, message: str, calculation_type: str | None = None):
        super().__init__(message, {"calculation_type": calculation_type})


class CatalogQueryException(AnyEltException):
    """Raised when a catalog search fails."""
    def __init__(self, catalog_name: str, message: str):
        super().__init__(f"Catalog query failed on '{catalog_name}': {message}", {"catalog": catalog_name})


class BridgingException(AnyEltException):
    """Raised when a cross-ELT data or command bridging operation fails."""
    def __init__(self, source_elt: str, target_elt: str, message: str):
        super().__init__(f"Bridge failed from '{source_elt}' to '{target_elt}': {message}", {
            "source_elt": source_elt,
            "target_elt": target_elt
        })
