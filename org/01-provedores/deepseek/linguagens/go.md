> **Navegação:** [← Mapa mestre](../../../README.md) · [↑ DeepSeek](../README.md) · [Arquiteturas](../../../02-arquiteturas/README.md) · [Grok](../../grok/README.md)

# DeepSeek API com Go (sem dependências externas)

> Go 1.21+ recomendado. Cliente da biblioteca padrão `net/http`. [Índice](../README.md).

## 1. Criar projeto

```bash
mkdir deepseek-go && cd deepseek-go
go mod init example.com/deepseek-go
# Configure DEEPSEEK_API_KEY no ambiente.
```

## 2. Exemplo completo

Salve como `main.go`:
```go
package main

import (
    "bytes"
    "context"
    "encoding/json"
    "fmt"
    "io"
    "log"
    "net/http"
    "os"
    "time"
)

type Message struct {
    Role string `json:"role"`
    Content string `json:"content"`
}
type Request struct {
    Model string `json:"model"`
    Messages []Message `json:"messages"`
    MaxTokens int `json:"max_tokens"`
}
type Response struct {
    Choices []struct {
        Message Message `json:"message"`
        FinishReason string `json:"finish_reason"`
    } `json:"choices"`
    Usage json.RawMessage `json:"usage"`
}

func main() {
    key := os.Getenv("DEEPSEEK_API_KEY")
    if key == "" { log.Fatal("Configure DEEPSEEK_API_KEY") }

    payload := Request{
        Model: "deepseek-flash",
        Messages: []Message{{Role:"user",Content:"O que é goroutine?"}},
        MaxTokens: 200,
    }
    raw, err := json.Marshal(payload)
    if err != nil { log.Fatal(err) }

    ctx, cancel := context.WithTimeout(context.Background(), 90*time.Second)
    defer cancel()
    req, err := http.NewRequestWithContext(ctx, "POST",
        "https://api.deepseek.com/chat/completions", bytes.NewReader(raw))
    if err != nil { log.Fatal(err) }
    req.Header.Set("Authorization", "Bearer "+key)
    req.Header.Set("Content-Type", "application/json")

    client := &http.Client{Timeout: 90*time.Second}
    resp, err := client.Do(req)
    if err != nil { log.Fatal(err) }
    defer resp.Body.Close()
    data, err := io.ReadAll(io.LimitReader(resp.Body, 5<<20))
    if err != nil { log.Fatal(err) }
    if resp.StatusCode != http.StatusOK {
        log.Fatalf("HTTP %d: %s", resp.StatusCode, data)
    }

    var out Response
    if err := json.Unmarshal(data, &out); err != nil { log.Fatal(err) }
    if len(out.Choices) == 0 { log.Fatal("Resposta sem choices") }
    fmt.Println(out.Choices[0].Message.Content)
    fmt.Printf("usage: %s\n", out.Usage)
}
```

Execute `go run .`. As estruturas `json:...` são tags Go; o arquivo deve manter as **crases** exibidas no bloco.

## 3. Listar modelos

Reutilize o mesmo `http.Client`, faça `GET https://api.deepseek.com/models` com header Authorization, decodifique `data[].id`. Para multiagentes, prefira uma camada `Client` que trate retries, métricas e rate limit.

## 4. Streaming

Com `"stream":true` o servidor retorna SSE; use `bufio.Reader` e processe linhas `data:`, ignorando comentários `: keep-alive` e parando em `[DONE]`. A mensagem de ferramenta pode ser fragmentada ao longo dos chunks; agregue antes de validar/acionar. Em produção limite buffer e cheque `ctx.Done()`.

**Documentação:** [Chat Completions](https://api-docs.deepseek.com/api/create-chat-completion/) e [Modelos](https://api-docs.deepseek.com/api/list-models/).


---

**Continue:** [Mapa mestre](../../../README.md) · [DeepSeek](../README.md) · [Grok/xAI](../../grok/README.md) · [Arquitetura multiagente](../../../02-arquiteturas/README.md).
