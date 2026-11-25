using Microsoft.AspNetCore.Mvc;

[ApiController]
[Route("api/pagos")]
public class PagosController : ControllerBase
{
    [HttpGet]
    public IActionResult Lista() { return Ok(); }
}
