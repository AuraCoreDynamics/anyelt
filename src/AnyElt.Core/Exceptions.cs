namespace AnyElt.Core;

public class AnyEltException : Exception
{
    public Dictionary<string, object?> Details { get; }

    public AnyEltException(string message, Dictionary<string, object?>? details = null)
        : base(message)
    {
        Details = details ?? new Dictionary<string, object?>();
    }
}

public class UnsupportedCapabilityException : AnyEltException
{
    public UnsupportedCapabilityException(string adapterName, string capabilityName)
        : base($"ELT adapter '{adapterName}' does not support capability '{capabilityName}'.",
               new Dictionary<string, object?> { ["Adapter"] = adapterName, ["Capability"] = capabilityName })
    {
    }
}

public class EltConnectionException : AnyEltException
{
    public EltConnectionException(string adapterName, string message, Exception? inner = null)
        : base($"Failed to connect to ELT '{adapterName}': {message}",
               new Dictionary<string, object?> { ["Adapter"] = adapterName, ["InnerException"] = inner?.Message })
    {
    }
}

public class ImageNotFoundException : AnyEltException
{
    public ImageNotFoundException(string uri)
        : base($"Image not found or unreadable: {uri}",
               new Dictionary<string, object?> { ["Uri"] = uri })
    {
    }
}

public class MensurationException : AnyEltException
{
    public MensurationException(string message, string? calculationType = null)
        : base(message, new Dictionary<string, object?> { ["CalculationType"] = calculationType })
    {
    }
}

public class CatalogQueryException : AnyEltException
{
    public CatalogQueryException(string catalogName, string message)
        : base($"Catalog query failed on '{catalogName}': {message}",
               new Dictionary<string, object?> { ["Catalog"] = catalogName })
    {
    }
}

public class BridgingException : AnyEltException
{
    public BridgingException(string sourceElt, string targetElt, string message)
        : base($"Bridge failed from '{sourceElt}' to '{targetElt}': {message}",
               new Dictionary<string, object?> { ["SourceElt"] = sourceElt, ["TargetElt"] = targetElt })
    {
    }
}
