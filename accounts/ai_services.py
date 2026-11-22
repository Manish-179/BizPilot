import json
import os
import time

from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class GeminiAPIError(Exception):
    pass


def _call_gemini(prompt, api_key, model):
    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"{model}:generateContent?key={api_key}"
    )

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 700,
        },
    }

    request = Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urlopen(request, timeout=45) as response:
        data = json.loads(response.read().decode("utf-8"))

    candidates = data.get("candidates", [])

    if not candidates:
        raise GeminiAPIError(
            "Gemini did not return a response. Please try again."
        )

    parts = candidates[0].get("content", {}).get("parts", [])

    result = "\n".join(
        part.get("text", "")
        for part in parts
    ).strip()

    if not result:
        raise GeminiAPIError("Gemini returned an empty response.")

    return result


def generate_gemini_text(prompt):
    api_key = os.environ.get("GEMINI_API_KEY")

    if not api_key:
        raise GeminiAPIError(
            "Gemini API key is not configured on the server."
        )

    primary_model = os.environ.get(
        "GEMINI_MODEL",
        "gemini-3.8-flash"
    )

    fallback_model = os.environ.get(
        "GEMINI_FALLBACK_MODEL",
        "gemini-3.5-flash-lite"
    )

    models = list(dict.fromkeys([
        primary_model,
        fallback_model
    ]))

    last_error = None

    for model in models:
        for attempt in range(3):
            try:
                return _call_gemini(
                    prompt,
                    api_key,
                    model
                )

            except HTTPError as exc:
                try:
                    details = json.loads(
                        exc.read().decode("utf-8")
                    )

                    message = details.get(
                        "error", {}
                    ).get(
                        "message",
                        "Gemini request failed."
                    )

                except Exception:
                    message = "Gemini request failed."

                last_error = message

                retryable = exc.code in (
                    429, 500, 502, 503, 504
                )

                model_unavailable = exc.code == 404

                if retryable and attempt < 2:
                    time.sleep(2 ** attempt)
                    continue

                if retryable or model_unavailable:
                    break

                raise GeminiAPIError(message) from exc

            except (URLError, TimeoutError) as exc:
                last_error = (
                    "Could not connect to Gemini. "
                    "Check your internet connection."
                )

                if attempt < 2:
                    time.sleep(2 ** attempt)
                    continue

                break

            except (ValueError, KeyError) as exc:
                raise GeminiAPIError(
                    "Gemini returned an unreadable response."
                ) from exc

            except GeminiAPIError:
                raise

    raise GeminiAPIError(
        "Gemini AI is temporarily unavailable. "
        f"Please try again later. Details: {last_error}"
    )