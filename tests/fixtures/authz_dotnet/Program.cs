var builder = WebApplication.CreateBuilder(args);
var app = builder.Build();
app.MapControllers();
app.MapGet("/salud", () => "ok");
app.MapPost("/webhook", (Pago pago) => Results.Ok()).RequireAuthorization();
app.Run();
