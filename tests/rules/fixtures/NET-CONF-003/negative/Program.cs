public class Arranque
{
    public void Configura(CorsPolicyBuilder policy, CorsPolicyBuilder publica)
    {
        policy.WithOrigins("https://padron.interno.example").AllowAnyHeader().AllowCredentials();
        publica.AllowAnyOrigin().AllowAnyHeader();
    }
}
