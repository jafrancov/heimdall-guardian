using System.Data.SqlClient;
using Microsoft.EntityFrameworkCore;

public class Repositorio
{
    public void Buscar(SqlConnection cn, AppDb db, string nombre)
    {
        var a = new SqlCommand("SELECT * FROM Usuarios WHERE Nombre = @nombre", cn);
        a.Parameters.AddWithValue("@nombre", nombre);
        db.Database.ExecuteSqlInterpolated($"DELETE FROM Usuarios WHERE Nombre = {nombre}");
        var c = db.Usuarios.FromSqlRaw("SELECT * FROM Usuarios WHERE Nombre = {0}", nombre);
    }
}
