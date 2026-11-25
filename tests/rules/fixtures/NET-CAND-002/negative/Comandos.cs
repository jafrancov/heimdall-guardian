using System.Diagnostics;

public class Comandos
{
    public void Ejecutar(string archivo)
    {
        Process.Start("notepad.exe");
        Process.Start(new ProcessStartInfo("convert.exe", "entrada.png"));
    }
}
