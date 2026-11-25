using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

[Authorize]
public class CuentasController : ControllerBase
{
    [AllowAnonymous]
    [HttpGet("estado")]
    public IActionResult Estado() { return Ok(); }

    [HttpPost("importar")]
    public IActionResult Importar() { return Ok(); }
}
