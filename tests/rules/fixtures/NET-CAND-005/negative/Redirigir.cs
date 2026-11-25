public class Redirigir : Controller
{
    public IActionResult Ir(string destino)
    {
        if (Url.IsLocalUrl(destino)) return LocalRedirect(destino);
        return Redirect("/inicio");
    }
}
