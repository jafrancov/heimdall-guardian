using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

[Authorize]
public class CuentasController : ControllerBase
{
    [AllowAnonymous]
    [HttpPost("importar")]
    public IActionResult Importar() { return Ok(); }

    [HttpDelete]
    [AllowAnonymous]
    public IActionResult Borrar() { return Ok(); }
}
