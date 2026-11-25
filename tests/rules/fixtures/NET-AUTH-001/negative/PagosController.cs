using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

[Authorize]
[ApiController]
public class PagosController : ControllerBase
{
    [HttpGet]
    public IActionResult Lista() { return Ok(); }
}

[Authorize(Roles = "Admin")]
public class AdminController : Controller
{
    public IActionResult Index() { return View(); }
}

public class MixtoController : Controller
{
    [Authorize]
    public IActionResult Privado() { return View(); }
}

public class Servicio : IServicio
{
    public void Ejecuta() { }
}
