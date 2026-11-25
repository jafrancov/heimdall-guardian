using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace App.Controllers
{
    [Authorize]
    [ApiController]
    [Route("api/[controller]")]
    public class PagosController : ControllerBase
    {
        private readonly IServicio _servicio;

        public PagosController(IServicio servicio)
        {
            _servicio = servicio;
        }

        [HttpGet]
        public IActionResult Lista() { return Ok(); }

        [HttpGet("{id}")]
        public async Task<ActionResult<Pago>> Detalle(int id)
        {
            return Ok();
        }

        [AllowAnonymous]
        [HttpPost("importar")]
        public IActionResult Importar() { return Ok(); }

        // [HttpDelete("comentado")]
        private void Auxiliar() { }
    }

    [ApiController]
    [Route("api/catalogos")]
    public class CatalogosController : ControllerBase
    {
        [HttpGet]
        public IActionResult Lista() { return Ok(); }

        [HttpDelete("{id}")]
        [Authorize(Roles = "Admin")]
        public IActionResult Borrar(int id) { return Ok(); }
    }
}
