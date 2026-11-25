public class Repositorio
{
    public void Buscar(AppDb ctx, string tabla, string nombre)
    {
        var a = new SqlCommand("SELECT * FROM " + tabla, conexion);
        var b = new SqlCommand($"SELECT * FROM clientes WHERE nombre = '{nombre}'", conexion);
        ctx.Database.ExecuteSqlRaw("DELETE FROM " + tabla);
        ctx.Clientes.FromSqlRaw($"SELECT * FROM {tabla}");
    }
}
