> **Navegação:** [← Mapa mestre](../../../README.md) · [↑ DeepSeek](../README.md) · [Arquiteturas](../../../02-arquiteturas/README.md) · [Grok](../../grok/README.md)

# DeepSeek API em C com libcurl

> C não tem cliente HTTP/JSON na biblioteca padrão. Exemplo mínimo usa **libcurl** para HTTP e mostra o JSON bruto, evitando parsing inseguro. [Índice](../README.md).

## 1. Dependências

Ubuntu/Debian:
```bash
sudo apt update
sudo apt install -y build-essential libcurl4-openssl-dev
```

macOS (Homebrew): `brew install curl` (ajustar include/linker para Homebrew). Windows: instale libcurl com vcpkg ou MSYS2 e vincule a biblioteca apropriada.

## 2. Código `main.c`

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <curl/curl.h>

struct Buffer {
    char *data;
    size_t size;
};

static size_t on_data(char *ptr, size_t size, size_t nmemb, void *userdata) {
    size_t n = size * nmemb;
    struct Buffer *buf = (struct Buffer *)userdata;
    if (n > 5 * 1024 * 1024 - buf->size - 1) return 0;
    char *p = realloc(buf->data, buf->size + n + 1);
    if (!p) return 0;
    buf->data = p;
    memcpy(buf->data + buf->size, ptr, n);
    buf->size += n;
    buf->data[buf->size] = '\0';
    return n;
}

int main(void) {
    const char *key = getenv("DEEPSEEK_API_KEY");
    if (!key || !*key) {
        fprintf(stderr, "Defina DEEPSEEK_API_KEY\n");
        return 1;
    }

    CURL *curl = curl_easy_init();
    if (!curl) return 1;
    struct Buffer buf = { NULL, 0 };
    const char *body =
        "{\"model\":\"deepseek-flash\","
        "\"messages\":[{\"role\":\"user\","
        "\"content\":\"Explique ponteiros em C.\"}],"
        "\"max_tokens\":200}";
    char auth[512];
    if (snprintf(auth, sizeof(auth), "Authorization: Bearer %s", key)
        >= (int)sizeof(auth)) {
        fprintf(stderr, "Chave muito longa\n");
        curl_easy_cleanup(curl);
        return 1;
    }
    struct curl_slist *headers = NULL;
    headers = curl_slist_append(headers, "Content-Type: application/json");
    headers = curl_slist_append(headers, auth);
    curl_easy_setopt(curl, CURLOPT_URL,
        "https://api.deepseek.com/chat/completions");
    curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);
    curl_easy_setopt(curl, CURLOPT_POSTFIELDS, body);
    curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, on_data);
    curl_easy_setopt(curl, CURLOPT_WRITEDATA, &buf);
    curl_easy_setopt(curl, CURLOPT_TIMEOUT, 90L);

    CURLcode status = curl_easy_perform(curl);
    long http_status = 0;
    curl_easy_getinfo(curl, CURLINFO_RESPONSE_CODE, &http_status);

    if (status != CURLE_OK || http_status != 200) {
        fprintf(stderr, "curl=%d http=%ld\n", (int)status, http_status);
    } else if (buf.data) {
        puts(buf.data);
    }

    free(buf.data);
    curl_slist_free_all(headers);
    curl_easy_cleanup(curl);
    return status == CURLE_OK && http_status == 200 ? 0 : 1;
}
```

## 3. Compilar e executar

```bash
cc -Wall -Wextra -O2 main.c -o deepseek $(pkg-config --cflags --libs libcurl)
./deepseek
```

O código exibe o JSON **inteiro**. Para extrair `choices[0].message.content`, use uma biblioteca de JSON como cJSON ou jansson, valide tipos e erros. Não use `strstr` para interpretar JSON em produção.

## 4. Cuidados em C

- O corpo literal de exemplo é fixo. Para dados vindos de usuários, **serialize com biblioteca JSON**, nunca concatene strings sem escape.
- Limite crescimento de buffers, timeouts, tamanho de respostas e tempo de conexão.
- Preserve TLS/validação de certificado; nunca use `CURLOPT_SSL_VERIFYPEER=0`.
- Não logue Authorization nem `DEEPSEEK_API_KEY`.
- Para streaming, processe SSE incrementalmente e isole chunks de ferramentas.

**Fonte:** [Chat Completions REST](https://api-docs.deepseek.com/api/create-chat-completion/).


---

**Continue:** [Mapa mestre](../../../README.md) · [DeepSeek](../README.md) · [Grok/xAI](../../grok/README.md) · [Arquitetura multiagente](../../../02-arquiteturas/README.md).
