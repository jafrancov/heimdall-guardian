using System.IO;
using System.Xml.Serialization;
using System.Text.Json;
using Newtonsoft.Json;

public class Datos
{
    public object Cargar(string json)
    {
        var a = JsonConvert.DeserializeObject("{\"id\":1}");
        var b = new XmlSerializer(typeof(Datos));
        var c = JsonSerializer.Deserialize<Datos>(json);
        var d = new XmlSerializer(Type.GetType("Datos"));
        return a;
    }
}
