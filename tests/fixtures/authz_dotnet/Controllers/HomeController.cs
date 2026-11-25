using Microsoft.AspNetCore.Mvc;

namespace App.Controllers
{
    public class HomeController : Controller
    {
        public IActionResult Index()
        {
            return View();
        }

        [HttpPost]
        [ValidateAntiForgeryToken]
        public IActionResult Guardar(Modelo modelo)
        {
            return View();
        }

        [NonAction]
        public string Formatea(string valor) { return valor; }
    }
}
