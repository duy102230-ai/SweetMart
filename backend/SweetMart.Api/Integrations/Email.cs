using System.Net;
using System.Net.Mail;
using Microsoft.Extensions.Options;

namespace SweetMart.Api.Integrations;

public class SmtpOptions
{
    public string Host { get; set; } = "smtp.gmail.com";
    public int Port { get; set; } = 587;
    public string User { get; set; } = "";
    public string Password { get; set; } = "";
    public string From { get; set; } = "";
    public bool Enabled => !string.IsNullOrWhiteSpace(User) && !string.IsNullOrWhiteSpace(Password);
}

public interface IEmailSender
{
    Task GuiAsync(string den, string tieuDe, string noiDungHtml, CancellationToken ct = default);
}

public class SmtpEmailSender(IOptions<SmtpOptions> options) : IEmailSender
{
    public async Task GuiAsync(string den, string tieuDe, string noiDungHtml, CancellationToken ct = default)
    {
        var o = options.Value;
        using var client = new SmtpClient(o.Host, o.Port) { EnableSsl = true, Credentials = new NetworkCredential(o.User, o.Password) };
        using var msg = new MailMessage(string.IsNullOrEmpty(o.From) ? o.User : o.From, den, tieuDe, noiDungHtml) { IsBodyHtml = true };
        await client.SendMailAsync(msg, ct);
    }
}

/// <summary>Dùng khi chưa cấu hình SMTP: chỉ ghi nội dung email ra log.</summary>
public class LogEmailSender(ILogger<LogEmailSender> logger) : IEmailSender
{
    public Task GuiAsync(string den, string tieuDe, string noiDungHtml, CancellationToken ct = default)
    {
        logger.LogInformation("[EMAIL] Tới: {To} | {Subject}\n{Body}", den, tieuDe, noiDungHtml);
        return Task.CompletedTask;
    }
}

/// <summary>Gửi email ở nền để không làm chậm request; lỗi gửi chỉ ghi log (R12).</summary>
public class EmailQueue(IServiceScopeFactory scopes, ILogger<EmailQueue> logger)
{
    public void Enqueue(string den, string tieuDe, string noiDungHtml)
    {
        _ = Task.Run(async () =>
        {
            try
            {
                using var scope = scopes.CreateScope();
                await scope.ServiceProvider.GetRequiredService<IEmailSender>().GuiAsync(den, tieuDe, noiDungHtml);
            }
            catch (Exception ex)
            {
                logger.LogWarning(ex, "Không gửi được email tới {To}", den);
            }
        });
    }
}
