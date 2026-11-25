using System.Security.Cryptography;

public class Claves
{
    public byte[] Resume(byte[] datos)
    {
        using var sha = SHA256.Create();
        using var aes = Aes.Create();
        return sha.ComputeHash(datos);
    }
}
