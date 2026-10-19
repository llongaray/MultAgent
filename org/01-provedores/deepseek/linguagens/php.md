> **Navegação:** [← Mapa mestre](../../../README.md) · [↑ DeepSeek](../README.md) · [Arquiteturas](../../../02-arquiteturas/README.md) · [Outro provedor](../../grok/README.md)

# DeepSeek API com PHP

> PHP 8.1+ recomendado com extensão `curl` e `json` habilitadas. A requisição deve ser executada no servidor, não em JS do navegador. [Índice](../README.md).

## 1. Configurar

```bash
php -v
php -m | grep -E 'curl|json'
# Configure DEEPSEEK_API_KEY via ambiente do servidor.
```

## 2. Exemplo `main.php`

```php
<?php
declare(strict_types=1);

$key = getenv('DEEPSEEK_API_KEY');
if (!$key) {
    throw new RuntimeException('Configure DEEPSEEK_API_KEY');
}

$payload = [
    'model' => 'deepseek-flash',
    'messages' => [
        ['role' => 'system', 'content' => 'Responda em português.'],
        ['role' => 'user', 'content' => 'O que é Composer em PHP?'],
    ],
    'max_tokens' => 250,
];
$json = json_encode($payload, JSON_THROW_ON_ERROR);

$curl = curl_init('https://api.deepseek.com/chat/completions');
curl_setopt_array($curl, [
    CURLOPT_POST => true,
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_POSTFIELDS => $json,
    CURLOPT_HTTPHEADER => [
        'Authorization: Bearer ' . $key,
        'Content-Type: application/json',
    ],
    CURLOPT_CONNECTTIMEOUT => 15,
    CURLOPT_TIMEOUT => 90,
]);
$body = curl_exec($curl);
$http = curl_getinfo($curl, CURLINFO_HTTP_CODE);
$error = curl_error($curl);
curl_close($curl);

if ($body === false || $http !== 200) {
    throw new RuntimeException("HTTP {$http}: {$error} " . (string)$body);
}

$response = json_decode($body, true, 512, JSON_THROW_ON_ERROR);
$answer = $response['choices'][0]['message']['content'] ?? null;
if (!is_string($answer)) {
    throw new RuntimeException('Resposta sem texto');
}
echo $answer . PHP_EOL;
echo 'Tokens: ' . ($response['usage']['total_tokens'] ?? '?') . PHP_EOL;
```

Execute `php main.php`. Para Linux/Nginx + PHP-FPM, disponibilize variáveis via mecanismo seguro do serviço, não necessariamente via shell interativo.

## 3. Laravel e produção

Use `Http::withToken(config('services.deepseek.key'))`, `timeout(...)` e `post(...)`; configure segredo fora do controle de versão. Valide entrada com Form Requests, restrinja taxa por tenant, trate timeouts e status HTTP.

## 4. JSON, streaming, MCP

As propriedades REST são independentes da linguagem. `response_format` permite JSON; `stream:true` exige leitor SSE com saída bufferizada; `tools` retorna sugestões de execução, nunca operações automáticas. Integre MCP somente no backend, com autorização.

**Fonte:** [Chat REST](https://api-docs.deepseek.com/api/create-chat-completion/).


---

**Continuar:** [Mapa mestre](../../../README.md) · [DeepSeek](../README.md) · [Comparação de provedores](../../../00-fundamentos/03-por-que-deepseek-e-grok.md) · [Arquiteturas](../../../02-arquiteturas/README.md).
