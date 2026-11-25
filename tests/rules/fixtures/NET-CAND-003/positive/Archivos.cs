using System.IO;

public class Archivos
{
    public byte[] Leer(string ruta, string nombre)
    {
        var a = File.ReadAllText(ruta);
        var b = File.Open(ruta, FileMode.Open);
        var c = Path.Combine("/datos", nombre);
        File.Delete(ruta);
        return null;
    }
}
