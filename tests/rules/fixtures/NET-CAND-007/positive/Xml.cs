using System.Xml;
using System.Xml.Linq;

public class Lector
{
    public void Leer(string contenido, string ruta)
    {
        var doc = new XmlDocument();
        doc.LoadXml(contenido);
        doc.Load(ruta);
        var r = XmlReader.Create(ruta, new XmlReaderSettings { DtdProcessing = DtdProcessing.Parse });
        var t = new XmlTextReader(ruta);
        var x = XDocument.Load(ruta);
        var e = XElement.Load(ruta);
    }
}
