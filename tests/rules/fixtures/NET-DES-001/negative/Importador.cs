using System.Text.Json;
using Newtonsoft.Json;

public class Importador
{
    public Pago Lee(string entrada)
    {
        var opciones = new JsonSerializerSettings { TypeNameHandling = TypeNameHandling.None };
        return JsonSerializer.Deserialize<Pago>(entrada);
    }
}
