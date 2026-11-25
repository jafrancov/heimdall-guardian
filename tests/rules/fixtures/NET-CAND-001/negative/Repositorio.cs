public class Repositorio
{
    public void Buscar(AppDb ctx, string nombre)
    {
        var a = new SqlCommand("SELECT * FROM clientes", conexion);
        a.Parameters.AddWithValue("@nombre", nombre);
        ctx.Database.ExecuteSqlRaw("DELETE FROM sesiones WHERE expira < GETDATE()");
        ctx.Clientes.FromSqlInterpolated($"SELECT * FROM clientes WHERE nombre = {nombre}");
    }
}
