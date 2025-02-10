var builder = WebApplication.CreateBuilder(args);

// 1. Register API Controllers
builder.Services.AddControllers();

var app = builder.Build();

// 2. Map Controllers 
app.MapControllers();

// 3. Enable HTTPS redirection
app.UseHttpsRedirection();

// 4. Run Application
app.Run();