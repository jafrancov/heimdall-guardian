using System.Xml;
using System.Xml.Linq;

public class Lector
{
    public void Leer(string contenido)
    {
        var doc = new XmlDocument();
        doc.LoadXml("<a><b/></a>");
        doc.Load("config.xml");
        var r = XmlReader.Create("config.xml");
        var t = new XmlTextReader("config.xml");
        var x = XDocument.Load("config.xml");
        var e = XElement.Parse(contenido);
        var cfg = configuration.Load(contenido);
    }
}
