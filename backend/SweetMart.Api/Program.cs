using System.Text;
using System.Text.Json.Serialization;
using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Options;
using Microsoft.IdentityModel.Tokens;
using Microsoft.OpenApi.Models;
using SweetMart.Api.Background;
using SweetMart.Api.Common;
using SweetMart.Api.Data;
using SweetMart.Api.Integrations;
using SweetMart.Api.Services;

var builder = WebApplication.CreateBuilder(args);
var cfg = builder.Configuration;

// ---------- Cấu hình (khóa bí mật đọc từ appsettings.Development.json hoặc biến môi trường, không đưa lên Git) ----------
builder.Services.Configure<JwtOptions>(cfg.GetSection("Jwt"));
builder.Services.Configure<VnPayOptions>(cfg.GetSection("VnPay"));
builder.Services.Configure<GhnOptions>(cfg.GetSection("Ghn"));
builder.Services.Configure<SmtpOptions>(cfg.GetSection("Smtp"));

builder.Services.AddDbContext<AppDbContext>(o => o.UseSqlServer(cfg.GetConnectionString("Default")));

// ---------- Nghiệp vụ ----------
builder.Services.AddScoped<TonKhoService>();
builder.Services.AddScoped<KhuyenMaiService>();
builder.Services.AddScoped<DonHangService>();
builder.Services.AddScoped<ThanhToanService>();
builder.Services.AddScoped<AuthService>();
builder.Services.AddScoped<BaoCaoService>();
builder.Services.AddHostedService<HuyDonQuaHanService>();

// ---------- Tích hợp: dùng bản giả lập khi chưa cấu hình khóa ----------
builder.Services.AddSingleton<VnPayClient>();
builder.Services.AddSingleton<EmailQueue>();
if (cfg.GetSection("Ghn").Get<GhnOptions>()?.Enabled == true)
    builder.Services.AddHttpClient<IGhnClient, GhnClient>(c => c.Timeout = TimeSpan.FromSeconds(10));
else
    builder.Services.AddSingleton<IGhnClient, FakeGhnClient>();
if (cfg.GetSection("Smtp").Get<SmtpOptions>()?.Enabled == true)
    builder.Services.AddScoped<IEmailSender, SmtpEmailSender>();
else
    builder.Services.AddScoped<IEmailSender, LogEmailSender>();

// ---------- Xác thực JWT, phân quyền theo vai trò ----------
var jwt = cfg.GetSection("Jwt").Get<JwtOptions>() ?? new JwtOptions();
if (jwt.Key.Length < 32) throw new InvalidOperationException("Jwt:Key phải dài tối thiểu 32 ký tự.");
builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme).AddJwtBearer(o =>
{
    o.TokenValidationParameters = new TokenValidationParameters
    {
        ValidIssuer = jwt.Issuer,
        ValidAudience = jwt.Audience,
        IssuerSigningKey = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(jwt.Key)),
        ClockSkew = TimeSpan.FromMinutes(1)
    };
});
builder.Services.AddAuthorization();

builder.Services.AddControllers().AddJsonOptions(o => o.JsonSerializerOptions.Converters.Add(new JsonStringEnumConverter()));
builder.Services.AddCors(o => o.AddDefaultPolicy(p =>
    p.WithOrigins(cfg.GetSection("App:CorsOrigins").Get<string[]>() ?? ["http://localhost:5173"]).AllowAnyHeader().AllowAnyMethod()));
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen(c =>
{
    c.SwaggerDoc("v1", new OpenApiInfo { Title = "SweetMart API", Version = "v1" });
    c.AddSecurityDefinition("Bearer", new OpenApiSecurityScheme { Type = SecuritySchemeType.Http, Scheme = "bearer", BearerFormat = "JWT" });
    c.AddSecurityRequirement(new OpenApiSecurityRequirement
    {
        [new OpenApiSecurityScheme { Reference = new OpenApiReference { Type = ReferenceType.SecurityScheme, Id = "Bearer" } }] = []
    });
});

var app = builder.Build();

using (var scope = app.Services.CreateScope())
{
    var db = scope.ServiceProvider.GetRequiredService<AppDbContext>();
    await db.Database.MigrateAsync();                       // áp dụng migration
    if (app.Environment.IsDevelopment() || cfg.GetValue<bool>("Seed:Enabled"))
        await DbSeeder.SeedAsync(db, cfg);
}

app.UseMiddleware<ErrorHandlingMiddleware>();
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}
app.UseCors();
app.UseAuthentication();
app.UseAuthorization();
app.MapControllers();
app.MapGet("/health", () => Results.Ok(new { status = "ok" }));
app.Run();

public partial class Program;
