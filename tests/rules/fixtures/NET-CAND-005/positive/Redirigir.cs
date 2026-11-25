public class Redirigir : Controller
{
    public IActionResult Ir(string destino)
    {
        if (destino == null) return Redirect(destino);
        return Redirect(Request.Query["next"]);
    }
}
