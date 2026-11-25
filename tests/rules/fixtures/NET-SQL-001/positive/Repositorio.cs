using System.Data.SqlClient;
using Microsoft.EntityFrameworkCore;

public class Repositorio
{
    public void Buscar(SqlConnection cn, AppDb db, string nombre)
    {
        var a = new SqlCommand("SELECT * FROM Usuarios WHERE Nombre = '" + nombre + "'", cn);
        var b = new SqlCommand($"SELECT * FROM Usuarios WHERE Nombre = '{nombre}'", cn);
        db.Database.ExecuteSqlRaw($"DELETE FROM Usuarios WHERE Nombre = '{nombre}'");
        var c = db.Usuarios.FromSqlRaw("SELECT * FROM Usuarios WHERE Nombre = '" + nombre + "'");
        a.CommandText = "SELECT * FROM Usuarios WHERE Id = " + nombre;
    }
}
