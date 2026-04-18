import requests

def call_model(model, prompt, tokens, timeout):
    try:
        r = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False
            },
            timeout=timeout
        )

        if r.status_code != 200:
            return f"[HTTP ERROR] {r.status_code}: {r.text}"

        data = r.json()

        return data.get("response", "")

    except Exception as e:
        return f"[MODEL ERROR] {e}"