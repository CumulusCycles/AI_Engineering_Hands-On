"""Same demo as stateless_demo.py, but conversation history is kept and resent."""

from openai import OpenAI


BASE_URL = "http://localhost:11434/v1"
MODEL = "llama3.2:3b"


client = OpenAI(base_url=BASE_URL, api_key="ollama")


def call_llm(messages: list[dict]) -> str:
    resp = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0,
    )
    return resp.choices[0].message.content or ""


def stateful_example() -> None:
    print("\n=== Stateful Example (full history in each call) ===")
    history: list[dict] = [{"role": "user", "content": "Hi, I'm Rob."}]
    a1 = call_llm(history)
    print("User: Hi, I'm Rob.")
    print(f"Assistant: {a1}")

    history.append({"role": "assistant", "content": a1})
    history.append({"role": "user", "content": "What's my name?"})
    a2 = call_llm(history)
    print("User: What's my name?")
    print(f"Assistant: {a2}")

    print(
        "\nNotice: call #2 included prior turns in `messages`, so the model "
        "can use the earlier message."
    )


def main() -> None:
    print("Ollama base URL:", BASE_URL)
    print("Model:", MODEL)
    print("Tip: make sure Ollama is running and model is pulled.")
    print("     ollama serve")
    print("     ollama pull llama3.2:3b")

    stateful_example()


if __name__ == "__main__":
    main()
