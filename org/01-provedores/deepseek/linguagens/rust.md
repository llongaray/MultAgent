> **Navegação:** [← Mapa mestre](../../../README.md) · [↑ DeepSeek](../README.md) · [Arquiteturas](../../../02-arquiteturas/README.md) · [Outro provedor](../../grok/README.md)

# DeepSeek API com Rust

> Rust stable; exemplo usando `reqwest`, `tokio` e `serde_json`. [Índice](../README.md).

## 1. Preparar projeto

```bash
cargo new deepseek-rust
cd deepseek-rust
cargo add reqwest --features json,rustls-tls --no-default-features
cargo add tokio --features macros,rt-multi-thread
cargo add serde_json
```

Exporte `DEEPSEEK_API_KEY` para o processo.

## 2. Código `src/main.rs`

```rust
use reqwest::Client;
use serde_json::{json, Value};
use std::{env, time::Duration};

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let key = env::var("DEEPSEEK_API_KEY")?;
    let client = Client::builder()
        .timeout(Duration::from_secs(90))
        .build()?;

    let payload = json!({
        "model": "deepseek-flash",
        "messages": [
            {"role":"system","content":"Responda em português."},
            {"role":"user","content":"Explique ownership em Rust."}
        ],
        "max_tokens": 250
    });

    let response = client
        .post("https://api.deepseek.com/chat/completions")
        .bearer_auth(key)
        .json(&payload)
        .send().await?;

    let code = response.status();
    let text = response.text().await?;
    if !code.is_success() {
        return Err(format!("DeepSeek HTTP {code}: {text}").into());
    }

    let data: Value = serde_json::from_str(&text)?;
    let answer = data["choices"][0]["message"]["content"]
        .as_str()
        .ok_or("Resposta sem texto")?;
    println!("{answer}");
    println!("Uso: {}", data["usage"]);
    Ok(())
}
```

Execute `cargo run`.

## 3. Melhorias recomendadas

Substitua `Value` por structs `serde::Deserialize` quando estabilizar o contrato. Implemente limites para body, retries de 429/5xx, circuit breaker, identificação de tenant, medição de tokens e logs sem segredos. Use streaming de bytes de `reqwest` para SSE com parser dedicado; chunks não correspondem a mensagens SSE completas.

## 4. Ferramentas e modelos

`GET /models` recebe `Bearer` no header. `POST /chat/completions` com `tools` permite Function Calling, cuja execução acontece em handlers autorizados da própria aplicação. Os argumentos devem ser decodificados e validados antes da execução.

**Fonte:** [Chat Completions](https://api-docs.deepseek.com/api/create-chat-completion/).


---

**Continuar:** [Mapa mestre](../../../README.md) · [DeepSeek](../README.md) · [Comparação de provedores](../../../00-fundamentos/03-por-que-deepseek-e-grok.md) · [Arquiteturas](../../../02-arquiteturas/README.md).
