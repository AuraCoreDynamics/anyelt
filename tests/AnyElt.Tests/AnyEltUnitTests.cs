namespace AnyElt.Tests;

using Xunit;
using AnyElt.Core;
using AnyElt.Adapters;

public class AnyEltUnitTests
{
    [Fact]
    public void VerifyAllAdaptersSelfDeclareCapabilities()
    {
        var adapters = EltRegistry.GetAllAdapters();
        Assert.Equal(2, adapters.Count);

        foreach (var adapter in adapters)
        {
            Assert.False(string.IsNullOrWhiteSpace(adapter.Name));
            Assert.False(string.IsNullOrWhiteSpace(adapter.Version));
            Assert.False(string.IsNullOrWhiteSpace(adapter.EltType));
            Assert.NotEqual(EltCapability.None, adapter.Capabilities);
        }
    }

    [Fact]
    public void VerifyAuraMistWebEltOperationsOnDisk()
    {
        string tempDir = Path.Combine(Path.GetTempPath(), "anyelt_auramist_" + Guid.NewGuid().ToString("N"));
        string tempFile = Path.Combine(tempDir, "dc_recon.ntf");

        try
        {
            Directory.CreateDirectory(tempDir);
            byte[] nitfBytes = AnyElt.Core.IO.RasterReader.CreateSyntheticNitfBytes("MISSION_AURAMIST_DC");
            File.WriteAllBytes(tempFile, nitfBytes);

            var adapter = new AuraMistAdapter();
            Assert.True(adapter.HasCapability(EltCapability.DirectLoading));
            Assert.True(adapter.HasCapability(EltCapability.MensurationShadow));
            Assert.True(adapter.HasCapability(EltCapability.RpcProjection));

            var meta = adapter.LoadImage(tempFile);
            Assert.NotNull(meta);
            Assert.Equal("MISSION_AURAMIST_DC", meta.ProductId);
            Assert.Equal(46.8, meta.SunElevationDeg);
            Assert.NotNull(meta.Rpc);
            Assert.True(meta.Tres.ContainsKey("RPC00B"));

            // Roam to DC coords
            var vp = adapter.RoamToGeo(38.8951, -77.0364, 14.0);
            Assert.NotNull(vp.CenterGeo);
            Assert.Equal(38.8951, vp.CenterGeo.Lat);

            // Adjust WebGL radiometrics
            var rad = adapter.ApplyRadiometrics(new RadiometricParameters
            {
                Brightness = 0.25,
                Contrast = 1.4,
                DraMode = DraMode.AutoPercentile
            });
            Assert.Equal(0.25, rad.Brightness);

            // Shadow Mensuration (h = L * tan(theta_sun))
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

            // Chip extraction
            var chip = adapter.ExtractChip(new ChipRequest
            {
                ImageUri = tempFile,
                SensorBounds = new PixelBBox(0, 0, 128, 128),
                OutputFormat = "PNG"
            });
            Assert.NotNull(chip);
            Assert.Equal(128, chip.Width);
            Assert.Equal(0x89, chip.Data[0]);
            Assert.Equal((byte)'P', chip.Data[1]);
        }
        finally
        {
            if (Directory.Exists(tempDir))
            {
                try { Directory.Delete(tempDir, true); } catch { }
            }
        }
    }

    [Fact]
    public void VerifyAuraMistRejectsMissingFilesWithoutMockFallbacks()
    {
        var adapter = new AuraMistAdapter();
        Assert.Throws<ImageNotFoundException>(() => adapter.LoadImage("non_existent_recon.ntf"));
    }

    [Fact]
    public void VerifyQgisBridgeAdapterOperationsOnDisk()
    {
        string tempDir = Path.Combine(Path.GetTempPath(), "anyelt_qgis_" + Guid.NewGuid().ToString("N"));
        string tempFile = Path.Combine(tempDir, "sample_qgis.ntf");

        try
        {
            Directory.CreateDirectory(tempDir);
            byte[] nitfBytes = AnyElt.Core.IO.RasterReader.CreateSyntheticNitfBytes("QGIS_SAMPLE_01");
            File.WriteAllBytes(tempFile, nitfBytes);

            var qgis = new QgisAdapter(9180);
            Assert.True(qgis.HasCapability(EltCapability.GroundRoam));
            Assert.False(qgis.HasCapability(EltCapability.SensorRoam)); // QGIS does not do native sensor-space roam

            var meta = qgis.LoadImage(tempFile);
            Assert.NotNull(meta);
            Assert.Equal("QGIS_SAMPLE_01", meta.ProductId);

            var vp = qgis.RoamToGeo(38.8951, -77.0364, 12.0);
            Assert.NotNull(vp.CenterGeo);
            Assert.Equal(38.8951, vp.CenterGeo.Lat);

            // Chip extraction
            var chip = qgis.ExtractChip(new ChipRequest
            {
                ImageUri = tempFile,
                GroundBounds = meta.BBox,
                OutputFormat = "PNG"
            });
            Assert.NotNull(chip);
            Assert.Equal(0x89, chip.Data[0]);
        }
        finally
        {
            if (Directory.Exists(tempDir))
            {
                try { Directory.Delete(tempDir, true); } catch { }
            }
        }
    }

    [Fact]
    public void VerifyQgisRejectsMissingFilesWithoutMockFallbacks()
    {
        var qgis = new QgisAdapter();
        Assert.Throws<ImageNotFoundException>(() => qgis.LoadImage("missing_raster.tif"));
    }

    [Fact]
    public void VerifyQgisRejectsSensorRoamWithoutCapability()
    {
        var qgis = new QgisAdapter();
        Assert.Throws<UnsupportedCapabilityException>(() => qgis.RoamToPixel(100, 100));
    }

    [Fact]
    public void VerifyCrossEltBridgeBetweenAuraMistAndQgis()
    {
        string tempDir = Path.Combine(Path.GetTempPath(), "anyelt_bridge_" + Guid.NewGuid().ToString("N"));
        string tempFile = Path.Combine(tempDir, "dc_flight.ntf");

        try
        {
            Directory.CreateDirectory(tempDir);
            byte[] nitfBytes = AnyElt.Core.IO.RasterReader.CreateSyntheticNitfBytes("DC_FLIGHT_BRIDGE");
            File.WriteAllBytes(tempFile, nitfBytes);

            var auramist = new AuraMistAdapter();
            var qgis = new QgisAdapter();

            auramist.LoadImage(tempFile);
            qgis.LoadImage(tempFile);

            // Roam AuraMist to DC
            auramist.RoamToGeo(38.8951, -77.0364, 15.0);

            var bridge = new EltBridge(auramist, qgis);
            var targetVp = bridge.SyncViewport();

            Assert.NotNull(targetVp.CenterGeo);
            Assert.Equal(38.8951, targetVp.CenterGeo.Lat);
            Assert.Equal(-77.0364, targetVp.CenterGeo.Lon);

            // Transfer chip from AuraMist to QGIS
            var chip = bridge.TransferChip(new ChipRequest
            {
                ImageUri = tempFile,
                SensorBounds = new PixelBBox(10, 10, 138, 138),
                OutputFormat = "PNG"
            });

            Assert.NotNull(chip);
            Assert.Equal(128, chip.Width);
            Assert.Equal(128, chip.Height);
            Assert.Equal(0x89, chip.Data[0]);
        }
        finally
        {
            if (Directory.Exists(tempDir))
            {
                try { Directory.Delete(tempDir, true); } catch { }
            }
        }
    }

    [Fact]
    public void VerifyEltSessionBrokerFindBestAdapter()
    {
        var broker = new EltSessionBroker();
        foreach (var adapter in EltRegistry.GetAllAdapters())
        {
            broker.Register(adapter);
        }

        // Search for adapter that supports MensurationShadow and RpcProjection
        var bestShadow = broker.FindBestAdapter(EltCapability.MensurationShadow | EltCapability.RpcProjection);
        Assert.NotNull(bestShadow);
        Assert.Equal("auramist", bestShadow.EltType);

        // Search for GroundRoam
        var bestGround = broker.FindBestAdapter(EltCapability.GroundRoam);
        Assert.NotNull(bestGround);
    }

    [Fact]
    public void VerifyCapabilityMatrixMarkdownGeneration()
    {
        string matrixMd = EltRegistry.GenerateCapabilityMatrixMarkdown();
        Assert.Contains("AnyElt Universal Capability Matrix", matrixMd);
        Assert.Contains("AuraMist Web ELT Adapter", matrixMd);
        Assert.Contains("QGIS PyQGIS Bridge Adapter", matrixMd);
        Assert.DoesNotContain("SOCET GXP", matrixMd);
        Assert.DoesNotContain("RemoteView", matrixMd);
        Assert.DoesNotContain("iSPY", matrixMd);
        Assert.Contains("✔", matrixMd);
    }
}
