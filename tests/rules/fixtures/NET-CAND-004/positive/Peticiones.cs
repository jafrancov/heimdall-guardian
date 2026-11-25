public class Peticiones
{
    public async void Traer(HttpClient cliente, string url, string host)
    {
        await cliente.GetAsync(url);
        await cliente.GetStringAsync("https://" + host + "/datos");
        var u = new Uri(url);
    }
}
