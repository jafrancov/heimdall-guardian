public class Peticiones
{
    public async void Traer(HttpClient cliente)
    {
        await cliente.GetAsync("https://api.example.com/estado");
        await cliente.GetStringAsync("https://api.example.com/datos");
        var u = new Uri("https://api.example.com");
    }
}
