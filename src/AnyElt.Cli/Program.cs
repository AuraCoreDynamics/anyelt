namespace AnyElt.Cli;

using AnyElt.Core;
using AnyElt.Adapters;

public class Program
{
    public static int Main(string[] args)
    {
        if (args.Length == 0 || args[0] is "-h" or "--help" or "help")
        {
            PrintUsage();
            return 0;
        }

        string cmd = args[0].ToLowerInvariant();
        switch (cmd)
        {
            case "matrix":
                Console.WriteLine(EltRegistry.GenerateCapabilityMatrixMarkdown());
                return 0;

            case "adapters":
                Console.WriteLine("Registered AnyElt Adapters (.NET 10):");
                foreach (var adapter in EltRegistry.GetAllAdapters())
                {
                    Console.WriteLine($" - {adapter.Name} [{adapter.EltType} v{adapter.Version}]");
                }
                return 0;

            case "inspect":
                if (args.Length < 2)
                {
                    Console.Error.WriteLine("Error: Missing image URI. Usage: anyelt inspect <uri> [--elt <type>]");
                    return 1;
                }
                string uri = args[1];
                string eltKey = "auramist";
                if (args.Length >= 4 && args[2] == "--elt") eltKey = args[3];

                var a = EltRegistry.Create(eltKey);
                var meta = a.LoadImage(uri);
                Console.WriteLine($"Loaded into {a.Name}:");
                Console.WriteLine($" - Product ID: {meta.ProductId}");
                Console.WriteLine($" - Sensor ID:  {meta.SensorId}");
                Console.WriteLine($" - Format:     {meta.Format}");
                Console.WriteLine($" - Dimensions: {meta.Width} x {meta.Height}");
                Console.WriteLine($" - Bit Depth:  {meta.BitDepth}");
                Console.WriteLine($" - Sun Elev:   {meta.SunElevationDeg}°");
                Console.WriteLine($" - TRE Count:  {meta.Tres.Count}");
                return 0;

            case "mensurate-shadow":
                if (args.Length < 3)
                {
                    Console.Error.WriteLine("Usage: anyelt mensurate-shadow <shadow_length_m> <sun_elevation_deg>");
                    return 1;
                }
                double len = double.Parse(args[1]);
                double sunElev = double.Parse(args[2]);
                var adapterInst = EltRegistry.Create("auramist");
                var res = adapterInst.Mensurate(new MensurationRequest
                {
                    ImageUri = "synthetic_layer",
                    CalculationType = "SHADOW_HEIGHT",
                    ShadowLengthM = len,
                    SunElevationDeg = sunElev
                });
                Console.WriteLine("Mensuration Result:");
                Console.WriteLine($" - Calculated Height: {res.CalculatedValue} {res.Unit}");
                Console.WriteLine($" - Formula:           {res.FormulaApplied}");
                Console.WriteLine($" - Confidence:        {res.ConfidenceScore * 100:F1}%");
                return 0;

            default:
                Console.Error.WriteLine($"Unknown command: {cmd}");
                PrintUsage();
                return 1;
        }
    }

    private static void PrintUsage()
    {
        Console.WriteLine("AnyElt: Universal Electronic Light Table (ELT) Abstraction CLI (.NET 10)");
        Console.WriteLine();
        Console.WriteLine("Usage: anyelt <command> [options]");
        Console.WriteLine();
        Console.WriteLine("Commands:");
        Console.WriteLine("  matrix                         Display the full ELT capability matrix");
        Console.WriteLine("  adapters                       List all registered ELT adapters");
        Console.WriteLine("  inspect <uri> [--elt <type>]   Inspect metadata and TREs using an ELT adapter");
        Console.WriteLine("  mensurate-shadow <len> <elev>  Calculate object height from shadow length");
        Console.WriteLine();
    }
}
