namespace AnyElt.Core;

public abstract class BaseEltAdapter : IEltAdapter
{
    protected bool _connected;
    protected ImageMetadata? _currentImage;
    protected ViewportState _viewport = new();

    public string Name { get; }
    public string Version { get; }
    public string EltType { get; }
    public abstract EltCapability Capabilities { get; }

    protected BaseEltAdapter(string name, string version, string eltType)
    {
        Name = name;
        Version = version;
        EltType = eltType;
    }

    public bool HasCapability(EltCapability capability) => (Capabilities & capability) == capability;

    protected void RequireCapability(EltCapability capability)
    {
        if (!HasCapability(capability))
        {
            throw new UnsupportedCapabilityException(Name, capability.ToString());
        }
    }

    public virtual bool Connect(string? connectionString = null)
    {
        _connected = true;
        return true;
    }

    public virtual void Disconnect()
    {
        _connected = false;
    }

    public bool IsConnected => _connected;

    public virtual ImageMetadata LoadImage(string uri)
    {
        RequireCapability(EltCapability.DirectLoading);
        var meta = GetMetadata(uri);
        _currentImage = meta;
        _viewport.LayerUri = uri;
        if (meta.BBox != null)
        {
            _viewport.CenterGeo = new GeoPoint(meta.BBox.CenterLat, meta.BBox.CenterLon);
        }
        _viewport.CenterPixel = new PixelPoint(meta.Width / 2.0, meta.Height / 2.0);
        return meta;
    }

    public abstract ImageMetadata GetMetadata(string uri);

    public ImageMetadata? CurrentImage => _currentImage;

    public virtual ViewportState GetViewport() => _viewport;

    public virtual ViewportState SetViewport(ViewportState viewport)
    {
        _viewport = viewport;
        return _viewport;
    }

    public virtual ViewportState RoamToGeo(double lat, double lon, double? zoom = null)
    {
        RequireCapability(EltCapability.GroundRoam);
        _viewport.CenterGeo = new GeoPoint(lat, lon);
        if (zoom.HasValue) _viewport.ZoomLevel = zoom.Value;
        return _viewport;
    }

    public virtual ViewportState RoamToPixel(double x, double y, double? zoom = null)
    {
        RequireCapability(EltCapability.SensorRoam);
        _viewport.CenterPixel = new PixelPoint(x, y);
        if (zoom.HasValue) _viewport.ZoomLevel = zoom.Value;
        return _viewport;
    }

    public virtual RadiometricParameters ApplyRadiometrics(RadiometricParameters parameters)
    {
        RequireCapability(EltCapability.RadiometricEnhancement);
        _viewport.Radiometrics = parameters;
        return parameters;
    }

    public virtual ImageChip ExtractChip(ChipRequest request)
    {
        if (request.SensorBounds != null)
        {
            RequireCapability(EltCapability.ChippingSensor);
        }
        else if (request.GroundBounds != null)
        {
            RequireCapability(EltCapability.ChippingGround);
        }
        else
        {
            throw new ArgumentException("ChipRequest must specify either SensorBounds or GroundBounds.");
        }

        int w = request.SensorBounds != null ? request.SensorBounds.Width : 256;
        int h = request.SensorBounds != null ? request.SensorBounds.Height : 256;
        w = Math.Clamp(w, 1, 4096);
        h = Math.Clamp(h, 1, 4096);

        byte[] pngHeader = [0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A];
        byte[] payload = new byte[pngHeader.Length + 64];
        Array.Copy(pngHeader, payload, pngHeader.Length);
        Array.Fill(payload, (byte)128, pngHeader.Length, 64);

        return new ImageChip
        {
            ChipId = $"chip_{EltType}_{w}x{h}",
            SourceUri = request.ImageUri,
            Width = w,
            Height = h,
            Format = request.OutputFormat,
            Data = payload,
            SensorBounds = request.SensorBounds,
            GroundBounds = request.GroundBounds,
            Metadata = new Dictionary<string, object>
            {
                ["Adapter"] = Name,
                ["Bands"] = request.Bands ?? [1]
            }
        };
    }

    public virtual MensurationResult Mensurate(MensurationRequest request)
    {
        string calc = request.CalculationType.ToUpperInvariant();

        if (calc == "SHADOW_HEIGHT")
        {
            RequireCapability(EltCapability.MensurationShadow);
            double? l = request.ShadowLengthM;
            double? theta = request.SunElevationDeg ?? _currentImage?.SunElevationDeg;

            if (!l.HasValue || !theta.HasValue)
            {
                throw new MensurationException("SHADOW_HEIGHT requires both ShadowLengthM and SunElevationDeg.", "SHADOW_HEIGHT");
            }

            double thetaRad = theta.Value * Math.PI / 180.0;
            double heightM = l.Value * Math.Tan(thetaRad);

            return new MensurationResult
            {
                CalculatedValue = Math.Round(heightM, 3),
                Unit = "meters",
                FormulaApplied = "h = L * tan(theta_sun)",
                ConfidenceScore = 0.98,
                Details = new Dictionary<string, object>
                {
                    ["ShadowLengthM"] = l.Value,
                    ["SunElevationDeg"] = theta.Value
                }
            };
        }
        else if (calc is "DISTANCE_2D" or "DISTANCE_3D")
        {
            RequireCapability(EltCapability.MensurationDistance);
            var pA = request.PointAGeo;
            var pB = request.PointBGeo;

            if (pA == null || pB == null)
            {
                throw new MensurationException("DISTANCE requires PointAGeo and PointBGeo.", calc);
            }

            const double rEarth = 6371008.8; // meters
            double dLat = (pB.Lat - pA.Lat) * Math.PI / 180.0;
            double dLon = (pB.Lon - pA.Lon) * Math.PI / 180.0;
            double lat1 = pA.Lat * Math.PI / 180.0;
            double lat2 = pB.Lat * Math.PI / 180.0;

            double a = Math.Pow(Math.Sin(dLat / 2.0), 2) +
                       Math.Cos(lat1) * Math.Cos(lat2) * Math.Pow(Math.Sin(dLon / 2.0), 2);
            double c = 2.0 * Math.Atan2(Math.Sqrt(a), Math.Sqrt(Math.Max(0.0, 1.0 - a)));
            double d2D = rEarth * c;

            double dist = calc == "DISTANCE_3D" ? Math.Sqrt(Math.Pow(d2D, 2) + Math.Pow(pB.AltM - pA.AltM, 2)) : d2D;

            return new MensurationResult
            {
                CalculatedValue = Math.Round(dist, 3),
                Unit = "meters",
                FormulaApplied = calc == "DISTANCE_2D" ? "Haversine Spherical Surface Geodesic" : "3D Euclidean Geodesic",
                ConfidenceScore = 0.99,
                Details = new Dictionary<string, object>
                {
                    ["PointA"] = pA,
                    ["PointB"] = pB
                }
            };
        }
        else if (calc == "AZIMUTH")
        {
            RequireCapability(EltCapability.MensurationDistance);
            var pA = request.PointAGeo;
            var pB = request.PointBGeo;

            if (pA == null || pB == null)
            {
                throw new MensurationException("AZIMUTH requires PointAGeo and PointBGeo.", "AZIMUTH");
            }

            double lat1 = pA.Lat * Math.PI / 180.0;
            double lat2 = pB.Lat * Math.PI / 180.0;
            double dLon = (pB.Lon - pA.Lon) * Math.PI / 180.0;

            double y = Math.Sin(dLon) * Math.Cos(lat2);
            double x = Math.Cos(lat1) * Math.Sin(lat2) - Math.Sin(lat1) * Math.Cos(lat2) * Math.Cos(dLon);
            double azimuthDeg = (Math.Atan2(y, x) * 180.0 / Math.PI + 360.0) % 360.0;

            return new MensurationResult
            {
                CalculatedValue = Math.Round(azimuthDeg, 2),
                Unit = "degrees",
                FormulaApplied = "Forward Geodetic Azimuth",
                ConfidenceScore = 1.0,
                Details = new Dictionary<string, object>
                {
                    ["PointA"] = pA,
                    ["PointB"] = pB
                }
            };
        }
        else
        {
            throw new MensurationException($"Unsupported calculation type: {calc}", calc);
        }
    }

    public virtual IReadOnlyList<CatalogItem> QueryCatalog(CatalogQuery query)
    {
        RequireCapability(EltCapability.CatalogSearch);
        return Array.Empty<CatalogItem>();
    }

    public virtual GeoPoint ProjectPixelToGround(string uri, PixelPoint pixel)
    {
        RequireCapability(EltCapability.RpcProjection);
        var meta = GetMetadata(uri);
        if (meta.BBox != null)
        {
            double normX = pixel.X / Math.Max(1, meta.Width);
            double normY = pixel.Y / Math.Max(1, meta.Height);
            double lon = meta.BBox.MinLon + normX * (meta.BBox.MaxLon - meta.BBox.MinLon);
            double lat = meta.BBox.MaxLat - normY * (meta.BBox.MaxLat - meta.BBox.MinLat);
            return new GeoPoint(lat, lon);
        }
        return new GeoPoint(0.0, 0.0);
    }

    public virtual PixelPoint ProjectGroundToPixel(string uri, GeoPoint geo)
    {
        RequireCapability(EltCapability.RpcProjection);
        var meta = GetMetadata(uri);
        if (meta.Rpc != null)
        {
            return meta.Rpc.EvaluateForward(geo.Lat, geo.Lon, geo.AltM);
        }
        if (meta.BBox != null)
        {
            double normLon = (geo.Lon - meta.BBox.MinLon) / Math.Max(0.000001, meta.BBox.MaxLon - meta.BBox.MinLon);
            double normLat = (meta.BBox.MaxLat - geo.Lat) / Math.Max(0.000001, meta.BBox.MaxLat - meta.BBox.MinLat);
            return new PixelPoint(normLon * meta.Width, normLat * meta.Height);
        }
        return new PixelPoint(0.0, 0.0);
    }
}
