using System.IO;
using System.Runtime.Serialization.Formatters.Binary;
using Microsoft.AspNetCore.Mvc;

namespace App.Controllers
{
    [ApiController]
    [Route("api/data")]
    public class DataController : ControllerBase
    {
        [HttpPost("import")]
        public IActionResult Import()
        {
            var formatter = new BinaryFormatter();
            var data = formatter.Deserialize(Request.Body);
            return Ok(data);
        }
    }
}
