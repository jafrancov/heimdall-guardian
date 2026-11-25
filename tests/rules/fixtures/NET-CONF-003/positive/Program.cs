public class Arranque
{
    public void Configura(CorsPolicyBuilder policy, CorsPolicyBuilder otra)
    {
        policy.AllowAnyOrigin().AllowAnyHeader().AllowCredentials();
        otra.AllowCredentials().AllowAnyMethod().AllowAnyOrigin();
    }
}
