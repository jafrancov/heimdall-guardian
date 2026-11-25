using System.Runtime.Serialization.Formatters.Binary;
using Newtonsoft.Json;

public class Importador
{
    public object Lee(System.IO.Stream entrada)
    {
        var formatter = new BinaryFormatter();
        var opciones = new JsonSerializerSettings { TypeNameHandling = TypeNameHandling.All };
        return formatter.Deserialize(entrada);
    }
}
