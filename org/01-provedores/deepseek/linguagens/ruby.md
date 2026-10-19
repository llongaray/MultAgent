> **Navegação:** [← Mapa mestre](../../../README.md) · [↑ DeepSeek](../README.md) · [Arquiteturas](../../../02-arquiteturas/README.md) · [Grok](../../grok/README.md)

# DeepSeek API com Ruby (Net::HTTP)

> Ruby 3+ recomendado; não exige gem para a chamada básica. [Índice](../README.md).

## 1. Pré-requisitos

Instale Ruby e configure `DEEPSEEK_API_KEY` no ambiente da máquina/servidor. Para projetos com Bundler, inclua dependências apenas quando necessárias; `net/http` e `json` são distribuídos com Ruby (podem requerer gems default conforme instalação).

## 2. Arquivo `main.rb`

```ruby
require "net/http"
require "uri"
require "json"

key = ENV.fetch("DEEPSEEK_API_KEY")
uri = URI("https://api.deepseek.com/chat/completions")

payload = {
  model: "deepseek-flash",
  messages: [
    { role: "system", content: "Responda em pt-BR." },
    { role: "user", content: "Explique blocos e closures em Ruby." }
  ],
  reasoning_effort: "low",
  max_tokens: 250
}

http = Net::HTTP.new(uri.host, uri.port)
http.use_ssl = true
http.open_timeout = 10
http.read_timeout = 90

req = Net::HTTP::Post.new(uri)
req["Authorization"] = "Bearer #{key}"
req["Content-Type"] = "application/json"
req.body = JSON.generate(payload)

response = http.request(req)
unless response.is_a?(Net::HTTPSuccess)
  abort("DeepSeek HTTP #{response.code}: #{response.body}")
end

data = JSON.parse(response.body)
content = data.dig("choices", 0, "message", "content")
abort("Resposta sem texto") unless content.is_a?(String)
puts content
puts "Tokens: #{data.dig("usage", "total_tokens")}"
```

Execute `ruby main.rb`. O exemplo usa string interpolation Ruby apenas para headers/logs: **não** imprima a chave em mensagens de erro.

## 3. Modelos e ferramentas

Para modelos, use `Net::HTTP::Get.new(URI("https://api.deepseek.com/models"))` com o mesmo header e interprete `data`. Para ferramentas, adicione `tools` à estrutura JSON, interprete `choices[0].message.tool_calls`, valide `arguments`, execute somente handlers autorizados e devolva mensagens `role:"tool"`.

## 4. Streaming

Adicione `stream:true` ao payload e use `http.request(req) {|res| res.read_body {|chunk| ... }}`. Acumule linhas SSE `data:` (chunks podem quebrar no meio de uma linha), ignore `: keep-alive` e encerre em `[DONE]`. Não analise chunks como JSON independente antes de reconstituir cada linha.

**Fonte:** [DeepSeek Chat Completions](https://api-docs.deepseek.com/api/create-chat-completion/).


---

**Continue:** [Mapa mestre](../../../README.md) · [DeepSeek](../README.md) · [Grok/xAI](../../grok/README.md) · [Arquitetura multiagente](../../../02-arquiteturas/README.md).
