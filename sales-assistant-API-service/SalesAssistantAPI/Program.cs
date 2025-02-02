var builder = WebApplication.CreateBuilder(args);

// 1. Register API Controllers
builder.Services.AddControllers();

var app = builder.Build();

// 2. Map Controllers 
app.MapControllers();

// 3. Enable HTTPS redirection
app.UseHttpsRedirection();


// 4. weather
// var summaries = new[]
// {
//     "Freezing", "Bracing", "Chilly", "Cool", "Mild", "Warm", "Balmy", "Hot", "Sweltering", "Scorching"
// };

// app.MapGet("/weatherforecast", () =>
// {
//     var forecast = Enumerable.Range(1, 5).Select(index =>
//         new WeatherForecast
//         (
//             DateOnly.FromDateTime(DateTime.Now.AddDays(index)),
//             Random.Shared.Next(-20, 55),
//             summaries[Random.Shared.Next(summaries.Length)]
//         ))
//         .ToArray();
//     return forecast;
// })
// .WithName("GetWeatherForecast");

// 5. Run Application
app.Run();