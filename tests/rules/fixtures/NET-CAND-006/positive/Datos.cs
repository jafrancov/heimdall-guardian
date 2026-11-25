using System.IO;
using System.Runtime.Serialization.Formatters.Binary;
using System.Runtime.Serialization.Formatters.Soap;
using System.Runtime.Serialization;
using System.Xml.Serialization;
using System.Web.Script.Serialization;
using Newtonsoft.Json;

public class Datos
{
    public object Cargar(Stream flujo, string json, string tipo, SimpleTypeResolver resolutor)
    {
        var a = new BinaryFormatter().Deserialize(flujo);
        var formatter = new SoapFormatter();
        var b = formatter.Deserialize(flujo);
        var c = new NetDataContractSerializer().Deserialize(flujo);
        var d = new LosFormatter().Deserialize(json);
        var e = new ObjectStateFormatter().Deserialize(json);
        var f = JsonConvert.DeserializeObject(json, new JsonSerializerSettings());
        var g = new XmlSerializer(Type.GetType(tipo));
        var h = new JavaScriptSerializer(resolutor);
        return a;
    }
}
