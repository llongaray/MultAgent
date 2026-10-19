> **Navegação:** [← Mapa mestre](../../../README.md) · [↑ DeepSeek](../README.md) · [Arquiteturas](../../../02-arquiteturas/README.md) · [Grok](../../grok/README.md)

# DeepSeek API com Java (JDK 11+)

> Usa `java.net.http.HttpClient`, disponível desde Java 11. Exemplo sem dependências externas; em produção use uma biblioteca JSON confiável. [Índice](../README.md).

## 1. Pré-requisitos

Instale JDK 11 ou superior, configure `DEEPSEEK_API_KEY` no ambiente e execute `java -version`.

## 2. Exemplo — `DeepSeekExample.java`

```java
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;

public class DeepSeekExample {
    public static void main(String[] args) throws Exception {
        String apiKey = System.getenv("DEEPSEEK_API_KEY");
        if (apiKey == null || apiKey.isBlank()) {
            throw new IllegalStateException("Configure DEEPSEEK_API_KEY");
        }

        // JSON fixo para teste. Para dados dinâmicos, use Jackson ou Gson.
        String payload = "{"
            + "\"model\":\"deepseek-flash\","
            + "\"messages\":["
            + "{\"role\":\"system\",\"content\":\"Responda em português.\"},"
            + "{\"role\":\"user\",\"content\":\"Explique JVM rapidamente.\"}"
            + "],\"max_tokens\":250}";

        HttpClient client = HttpClient.newBuilder()
            .connectTimeout(Duration.ofSeconds(15))
            .build();

        HttpRequest request = HttpRequest.newBuilder()
            .uri(URI.create("https://api.deepseek.com/chat/completions"))
            .timeout(Duration.ofSeconds(90))
            .header("Authorization", "Bearer " + apiKey)
            .header("Content-Type", "application/json")
            .POST(HttpRequest.BodyPublishers.ofString(payload))
            .build();

        HttpResponse<String> res = client.send(
            request, HttpResponse.BodyHandlers.ofString());
        if (res.statusCode() != 200) {
            throw new IllegalStateException(
                "DeepSeek HTTP " + res.statusCode() + ": " + res.body());
        }
        System.out.println(res.body()); // JSON bruto, inclui choices/usage.
    }
}
```

Executar:
```bash
javac DeepSeekExample.java
java DeepSeekExample
```

## 3. Extrair resposta e usar dados dinâmicos

Para produção, use Jackson (`com.fasterxml.jackson.databind.ObjectMapper`) ou Gson. Parseie `choices[0].message.content` e `usage.total_tokens`; verifique arrays vazios, `finish_reason` e status HTTP. Para inserir prompts variáveis, construa objetos Java e **serialize para JSON**, em vez de interpolar strings.

## 4. Streaming, ferramentas e modelos

- Listagem: `GET /models` com `HttpRequest.GET()` e autenticação.
- SSE: `POST /chat/completions` com `stream:true` e `BodyHandlers.ofInputStream()`; agrupe linhas `data:` até `[DONE]`.
- Tool Calling: inclua `tools` (JSON Schema), interprete `tool_calls`; valide argumentos e execute apenas handlers permitidos na aplicação.
- Defina timeouts, limite de tamanho do corpo e política de retries em 429/5xx.

**Fonte:** [Chat API oficial](https://api-docs.deepseek.com/api/create-chat-completion/).


---

**Continue:** [Mapa mestre](../../../README.md) · [DeepSeek](../README.md) · [Grok/xAI](../../grok/README.md) · [Arquitetura multiagente](../../../02-arquiteturas/README.md).
