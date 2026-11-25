using System.Diagnostics;

public class Comandos
{
    public void Ejecutar(string programa, string archivo)
    {
        Process.Start(programa);
        Process.Start(new ProcessStartInfo(programa, archivo));
    }
}
