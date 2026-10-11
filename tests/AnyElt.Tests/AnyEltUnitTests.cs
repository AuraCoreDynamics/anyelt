namespace AnyElt.Tests;

using Xunit;
using AnyElt.Core;
using AnyElt.Adapters;
using AnyElt.Extensions;

public class AnyEltUnitTests
{
    [Fact]
    public void VerifyAllAdaptersSelfDeclareCapabilities()
    {
        var adapters = EltRegistry.GetAllAdapters();
        Assert.Equal(7, adapters.Count);

        foreach (var adapter in adapters)
        {
            Assert.False(string.IsNullOrWhiteSpace(adapter.Name));
            Assert.False(string.IsNullOrWhiteSpace(adapter.Version));
            Assert.False(string.IsNullOrWhiteSpace(adapter.EltType));
            Assert.NotEqual(EltCapability.None, adapter.Capabilities);
        }
    }

    [Fact]
    public void VerifyAuraMistWebEltOperations()
    {
        var adapter = new AuraMistAdapter();
        Assert.True(adapter.HasCapability(EltCapability.DirectLoading));
        Assert.True(adapter.HasCapability(EltCapability.MensurationShadow));
        Assert.True(adapter.HasCapability(EltCapability.RpcProjection));

        var meta = adapter.LoadImage("nitf://auratiles/dc_recon.ntf");
        Assert.NotNull(meta);
        Assert.Equal("WORLDVIEW-03/PAN", meta.SensorId);
        Assert.Equal(46.8, meta.SunElevationDeg);
        Assert.NotNull(meta.Rpc);

        // Test Roam
        var vp = adapter.RoamToGeo(38.8951, -77.0364, 14.0);
        Assert.NotNull(vp.CenterGeo);
        Assert.Equal(38.8951, vp.CenterGeo.Lat);

        // Test Radiometrics
        var rad = adapter.ApplyRadiometrics(new RadiometricParameters
        {
            Brightness = 0.25,
            Contrast = 1.4,
            DraMode = DraMode.AutoPercentile
        });
        Assert.Equal(0.25, rad.Brightness);

        // Test Shadow Mensuration (h = L * tan(theta_sun))
        // L = 20m, theta = 46.8 deg -> h = 20 * tan(0.8168 rad) = 21.295m
        var res = adapter.Mensurate(new MensurationRequest
        {
            ImageUri = meta.Uri,
            CalculationType = "SHADOW_HEIGHT",
            ShadowLengthM = 20.0,
            SunElevationDeg = 46.8
        });
        Assert.Equal("meters", res.Unit);
        Assert.InRange(res.CalculatedValue, 21.2, 21.4);
    }

    [Fact]
    public void VerifySocetGxpPhotogrammetryAndCatalogSearch()
    {
        var gxp = new SocetGxpAdapter("C:\\Workspaces\\GEOINT_GXP");
        Assert.True(gxp.HasCapability(EltCapability.CatalogSearch));
        Assert.True(gxp.HasCapability(EltCapability.MultiSpectral));

        var meta = gxp.LoadImage("file://san_diego.ntf");
        Assert.Equal(4, meta.BandCount);
        Assert.Equal(52.4, meta.SunElevationDeg);

        // Query GXP Xplorer Catalog
        var items = gxp.QueryCatalog(new CatalogQuery
        {
            SensorId = "GEOEYE-01",
            Limit = 5
        });
        Assert.NotEmpty(items);
        Assert.Equal("GXP_XPLORER_ITEM_1001", items[0].ItemId);
        Assert.Contains("San Diego", items[0].Title);
    }

    [Fact]
    public void VerifyRemoteViewDirectLoadingAndMensuration()
    {
        var rv = new RemoteViewAdapter();
        Assert.True(rv.HasCapability(EltCapability.DirectLoading));
        Assert.True(rv.HasCapability(EltCapability.SensorRoam));

        var meta = rv.LoadImage("C:\\Imagery\\virginia_beach.ntf");
        Assert.Equal("WORLDVIEW-01/PAN", meta.SensorId);

        // Sensor Roam
        var vp = rv.RoamToPixel(1500, 1500, 2.0);
        Assert.NotNull(vp.CenterPixel);
        Assert.Equal(1500, vp.CenterPixel.X);

        // Haversine Distance
        var distRes = rv.Mensurate(new MensurationRequest
        {
            ImageUri = meta.Uri,
            CalculationType = "DISTANCE_2D",
            PointAGeo = new GeoPoint(36.85, -75.97),
            PointBGeo = new GeoPoint(36.86, -75.97)
        });
        Assert.Equal("meters", distRes.Unit);
        Assert.InRange(distRes.CalculatedValue, 1100.0, 1120.0);
    }

    [Fact]
    public void VerifyQgisBridgeAdapterOperations()
    {
        var qgis = new QgisAdapter(9180);
        Assert.True(qgis.HasCapability(EltCapability.GroundRoam));
        Assert.False(qgis.HasCapability(EltCapability.SensorRoam)); // QGIS does not do native sensor-space roam

        var meta = qgis.LoadImage("C:\\Data\\sentinel.tif");
        Assert.Equal(12, meta.BandCount);

        var vp = qgis.RoamToGeo(45.4215, -75.6972, 12.0);
        Assert.NotNull(vp.CenterGeo);
    }

    [Fact]
    public void VerifyISpyCatalogOnlyAdapterRejectsDirectLoadingAndPerformsCatalogSearch()
    {
        var ispy = new ISpyAdapter("https://ispy.nga.mil/api", "SECRET_KEY");
        Assert.True(ispy.HasCapability(EltCapability.CatalogSearch));
        Assert.False(ispy.HasCapability(EltCapability.DirectLoading));

        // Attempting Direct Loading on a catalog-only ELT must throw UnsupportedCapabilityException
        Assert.Throws<UnsupportedCapabilityException>(() => ispy.LoadImage("local_file.ntf"));

        // Query catalog
        var results = ispy.QueryCatalog(new CatalogQuery { SensorId = "WORLDVIEW-02" });
        Assert.NotEmpty(results);
        Assert.Equal("ISPY_RECORD_2026_0901", results[0].ItemId);
    }

    [Fact]
    public void VerifyImageJGeointExtensionTransformsProcessorIntoElt()
    {
        var ij = new ImageJAdapter();
        Assert.True(ij.HasCapability(EltCapability.DirectLoading));
        Assert.True(ij.HasCapability(EltCapability.RpcProjection));
        Assert.True(ij.HasCapability(EltCapability.ScriptingMacro));

        var meta = ij.LoadImage("C:\\Scientific\\sample.tif");
        Assert.NotNull(meta.Rpc);
        Assert.True(meta.Tres.ContainsKey("RPC00B"));

        string macro = ij.ExecuteMacro(["run('Enhance Contrast', 'saturated=0.35');", "run('Sharpen');"]);
        Assert.Contains("Enhance Contrast", macro);
        Assert.Contains("setBatchMode", macro);
    }

    [Fact]
    public void VerifyQuasarHyperspectralExtensionAndSpectralAngleMapper()
    {
        var quasar = new QuasarAdapter();
        Assert.True(quasar.HasCapability(EltCapability.Hyperspectral));
        Assert.True(quasar.HasCapability(EltCapability.SpectralSignature));

        var meta = quasar.LoadImage("C:\\Hyperspectral\\aviris.h5");
        Assert.Equal(224, meta.BandCount);

        var sigVeg = quasar.ExtractSpectralSignature("Healthy Vegetation", new PixelBBox(10, 10, 50, 50));
        var sigWater = quasar.ExtractSpectralSignature("Deep Water", new PixelBBox(60, 60, 100, 100));

        Assert.Equal(224, sigVeg.ReflectanceValues.Count);
        Assert.Equal(224, sigWater.ReflectanceValues.Count);

        // Compare SAM angle
        double sam = quasar.CompareSpectralSignatures(sigVeg, sigWater);
        Assert.True(sam > 0.1); // Distinct signatures

        // Same signature should have ~0 angle
        double samSame = quasar.CompareSpectralSignatures(sigVeg, sigVeg);
        Assert.InRange(samSame, 0.0, 0.0001);
    }

    [Fact]
    public void VerifyCrossEltBridgeViewportSyncWithCoordinateSpaceTranslation()
    {
        var gxp = new SocetGxpAdapter();
        var qgis = new QgisAdapter();

        gxp.LoadImage("file://sd.ntf");
        qgis.LoadImage("file://sd_map.tif");

        // Roam GXP to pixel (2048, 2048) in sensor space
        gxp.RoamToPixel(2048, 2048, 5.0);

        var bridge = new EltBridge(gxp, qgis);
        var targetVp = bridge.SyncViewport();

        Assert.NotNull(targetVp.CenterGeo);
        Assert.InRange(targetVp.CenterGeo.Lat, 32.6, 32.8);
    }

    [Fact]
    public void VerifyCrossEltBridgeChipTransfer()
    {
        var gxp = new SocetGxpAdapter();
        var ij = new ImageJAdapter();

        gxp.LoadImage("file://sd.ntf");

        var bridge = new EltBridge(gxp, ij);
        var chip = bridge.TransferChip(new ChipRequest
        {
            ImageUri = "file://sd.ntf",
            SensorBounds = new PixelBBox(100, 100, 356, 356),
            OutputFormat = "PNG"
        });

        Assert.NotNull(chip);
        Assert.Equal(256, chip.Width);
        Assert.Equal(256, chip.Height);
        Assert.NotEmpty(chip.Data);
    }

    [Fact]
    public void VerifyEltSessionBrokerFindBestAdapter()
    {
        var broker = new EltSessionBroker();
        foreach (var adapter in EltRegistry.GetAllAdapters())
        {
            broker.Register(adapter);
        }

        // Search for adapter that supports both Hyperspectral and SpectralSignature
        var bestHyp = broker.FindBestAdapter(EltCapability.Hyperspectral | EltCapability.SpectralSignature);
        Assert.NotNull(bestHyp);
        Assert.Equal("quasar", bestHyp.EltType);

        // Search for adapter that supports both CatalogSearch and MultiSpectral
        var bestGxp = broker.FindBestAdapter(EltCapability.CatalogSearch | EltCapability.MultiSpectral);
        Assert.NotNull(bestGxp);
        Assert.Equal("socet_gxp", bestGxp.EltType);
    }

    [Fact]
    public void VerifyCapabilityMatrixMarkdownGeneration()
    {
        string matrixMd = EltRegistry.GenerateCapabilityMatrixMarkdown();
        Assert.Contains("AnyElt Universal Capability Matrix", matrixMd);
        Assert.Contains("AuraMist Web ELT Adapter", matrixMd);
        Assert.Contains("BAE Systems SOCET GXP Adapter", matrixMd);
        Assert.Contains("NGA iSPY Catalog Adapter", matrixMd);
        Assert.Contains("✔", matrixMd);
    }
}
