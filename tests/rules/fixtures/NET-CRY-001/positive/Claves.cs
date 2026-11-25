using System.Security.Cryptography;

public class Claves
{
    public byte[] Resume(byte[] datos)
    {
        using var md5 = MD5.Create();
        var sha = new SHA1Managed();
        var des = new DESCryptoServiceProvider();
        return md5.ComputeHash(datos);
    }
}
