"""Talks to the AI. One function, stream_reply(), works with every provider.

messages look like: [{"role": "user", "content": "hi"}, {"role": "assistant", "content": "..."}]
stream_reply yields the answer in small text pieces, so the UI can show it as it is typed.
"""

import asyncio
import re
from collections.abc import AsyncIterator

import anthropic
import openai

from app.config import settings

MAX_TOKENS = 64000  # upper limit on answer length; streaming keeps long answers safe


async def stream_reply(system: str, messages: list[dict]) -> AsyncIterator[str]:
    """Pick the provider from LLM_PROVIDER and stream its answer."""
    provider = settings.LLM_PROVIDER
    if provider == "openai":
        stream = _stream_openai(system, messages)
    elif provider == "anthropic":
        stream = _stream_anthropic(system, messages)
    else:
        stream = _stream_mock(messages)

    # On failure, send the error as chat text instead of crashing the request.
    # The specific errors come first so each gets a clear message.
    try:
        async for piece in stream:
            yield piece
    except (openai.AuthenticationError, anthropic.AuthenticationError):
        yield f"\n\n**Error:** the {provider} API key is missing or wrong. Check backend/.env."
    except (openai.RateLimitError, anthropic.RateLimitError):
        yield f"\n\n**Error:** {provider} rate limit reached. Wait a moment and try again."
    except (openai.APIConnectionError, anthropic.APIConnectionError):
        yield f"\n\n**Error:** could not connect to {provider}. Check your internet or base URL."
    except (openai.APIStatusError, anthropic.APIStatusError) as e:
        yield f"\n\n**Error from {provider}** ({e.status_code}): {e.message}"


# ---------- mock: fake answer, no API key needed ----------

MOCK_ANSWER = """This is a **mock reply** (LLM_PROVIDER=mock). You said:

> {question}

Here is a table to test the UI:

| Provider  | Needs API key | Runs locally |
|-----------|---------------|--------------|
| mock      | No            | Yes          |
| openai    | Yes           | No           |
| anthropic | Yes           | No           |

And a code block:

```python
def greet(name: str) -> str:
    return f"Hello, {{name}}!"

print(greet("KS Chatbot"))
```

Set `LLM_PROVIDER` in `backend/.env` to use a real AI."""


async def _stream_mock(messages: list[dict]) -> AsyncIterator[str]:
    question = messages[-1]["content"] if messages else "(nothing)"
    text = MOCK_ANSWER.format(question=question)
    # Split into words *and* the spaces/newlines between them, so the layout survives.
    for piece in re.split(r"(\s+)", text):
        if piece:
            yield piece
            await asyncio.sleep(0.02)  # pretend the AI is typing


# ---------- openai: OpenAI or any OpenAI-compatible API (Groq, Gemini, Ollama...) ----------

async def _stream_openai(system: str, messages: list[dict]) -> AsyncIterator[str]:
    client = openai.AsyncOpenAI(
        # Ollama ignores the key, but the SDK requires some text here.
        api_key=settings.OPENAI_API_KEY or "not-set",
        base_url=settings.OPENAI_BASE_URL or None,  # None = official OpenAI address
    )
    # OpenAI takes the system prompt as the first message.
    stream = await client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[{"role": "system", "content": system}, *messages],
        stream=True,
    )
    async for chunk in stream:
        if chunk.choices and chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content


# ---------- anthropic: Claude ----------

async def _stream_anthropic(system: str, messages: list[dict]) -> AsyncIterator[str]:
    client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY or None)
    # client.beta is needed for "fallbacks": if Claude declines a message for
    # safety reasons, Anthropic retries it on a backup model in the same call.
    async with client.beta.messages.stream(
        model=settings.ANTHROPIC_MODEL,
        max_tokens=MAX_TOKENS,
        system=system,
        messages=messages,
        output_config={"effort": "medium"},  # how hard Claude thinks; medium suits chat
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
    ) as stream:
        async for text in stream.text_stream:
            yield text
        final = await stream.get_final_message()

    # Even the backup model declined: say so instead of ending silently.
    if final.stop_reason == "refusal":
        yield "\n\n_Claude declined to answer this message._"
