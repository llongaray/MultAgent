# DeepSeek API com C# / .NET

> .NET 8+ recomendado; exemplo usa `HttpClient` e `System.Text.Json`. [Índice](../README.md).

## 1. Criar projeto

```bash
dotnet new console -n DeepSeekDemo
cd DeepSeekDemo
# Configure DEEPSEEK_API_KEY na sessão de shell.
```

## 2. Substitua `Program.cs`

```csharp
using System.Net.Http.Headers;
using System.Net.Http.Json;
using System.Text.Json;

var key = Environment.GetEnvironmentVariable("DEEPSEEK_API_KEY");
if (string.IsNullOrWhiteSpace(key))
    throw new InvalidOperationException("Configure DEEPSEEK_API_KEY");

using var http = new HttpClient { Timeout = TimeSpan.FromSeconds(90) };
http.DefaultRequestHeaders.Authorization =
    new AuthenticationHeaderValue("Bearer", key);

var payload = new
{
    model = "deepseek-flash",
    messages = new object[]
    {
        new { role = "system", content = "Responda em português." },
        new { role = "user", content = "Explique injeção de dependência." }
    },
    max_tokens = 250
};

using var response = await http.PostAsJsonAsync(
    "https://api.deepseek.com/chat/completions", payload);

string body = await response.Content.ReadAsStringAsync();
if (!response.IsSuccessStatusCode)
    throw new HttpRequestException(
        $"DeepSeek HTTP {(int)response.StatusCode}: {body}");

using var json = JsonDocument.Parse(body);
var choices = json.RootElement.GetProperty("choices");
if (choices.GetArrayLength() == 0) throw new Exception("Sem choices");
var message = choices[0].GetProperty("message");
if (message.TryGetProperty("content", out var content))
    Console.WriteLine(content.GetString());
else
    Console.WriteLine(body);
```

Execute `dotnet run`.

## 3. Boas práticas em ASP.NET Core

Registre `HttpClient` com `IHttpClientFactory`; configure políticas de retry com backoff e timeout. Implemente endpoint autenticado no servidor, não coloque chave em JavaScript de cliente nem em app móvel distribuído. Valide prompts/tamanhos, imponha quota por cliente e faça logs com mascaramento.

## 4. Recursos adicionais

`GET /models` lista IDs reais; `response_format:{"type":"json_object"}` permite JSON; `stream:true` usa SSE; `tools` permite Function Calling com executor próprio. Para visão, `deepseek-flash` recebe blocos de imagem. Consulte [recursos avançados](../04-recursos-avancados.md).

**Fonte:** [Referência oficial Chat Completions](https://api-docs.deepseek.com/api/create-chat-completion/).
