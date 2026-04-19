import requests
import time


def call_model(model, prompt, tokens, timeout):
    """
    V10.3.3 STABLE MODEL CALLER

    FIXES:
    - жесткий контроль таймаута
    - ограничение контекста (tokens)
    - keep_alive (ускоряет повторные вызовы)
    - стабильный retry с backoff
    - защита от перегрузки RAM
    """

    url = "http://localhost:11434/api/generate"

    # ❗ ЖЕСТКО РЕЖЕМ ПРОМПТ (критично для скорости)
    if len(prompt) > 12000:
        prompt = prompt[:12000]

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,

        # =========================
        # OLLAMA OPTIONS (ВАЖНО)
        # =========================
        "options": {
            "num_predict": tokens,      # контроль ответа
            "temperature": 0.2,         # стабильность
            "top_p": 0.9,
            "num_ctx": 2048             # ❗ ограничение контекста
        },

        # ускоряет повторные вызовы
        "keep_alive": "5m"
    }

    max_retries = 3
    base_timeout = timeout

    for attempt in range(1, max_retries + 1):

        try:
            r = requests.post(
                url,
                json=payload,
                timeout=base_timeout
            )

            if r.status_code != 200:
                return f"[HTTP ERROR] {r.status_code}: {r.text}"

            data = r.json()
            response = data.get("response", "")

            if response and response.strip():
                return response.strip()

            raise ValueError("Empty model response")

        except requests.exceptions.Timeout:
            print(f"[TIMEOUT] attempt {attempt}/{max_retries}")

        except Exception as e:
            print(f"[MODEL ERROR] attempt {attempt}: {e}")

        # =========================
        # BACKOFF
        # =========================
        time.sleep(1.5 * attempt)
        base_timeout += 20  # мягче увеличиваем, не убиваем систему

    return "[MODEL ERROR] max retries exceeded"