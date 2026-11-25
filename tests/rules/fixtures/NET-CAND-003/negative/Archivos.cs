using System.IO;

public class Archivos
{
    public byte[] Leer()
    {
        var a = File.ReadAllText("/etc/app/config.ini");
        var b = File.Open("/datos/ayuda.txt", FileMode.Open);
        var c = Path.Combine("/datos", "ayuda.txt");
        File.Delete("/tmp/cache.lock");
        return null;
    }
}
