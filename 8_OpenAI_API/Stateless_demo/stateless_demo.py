"""Quick Ollama demo showing LLM statelessness."""

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


def stateless_example() -> None:
    print("\n=== Stateless Example (no history passed) ===")
    m1 = [{"role": "user", "content": "Hi, I'm Rob."}]
    a1 = call_llm(m1)
    print("User: Hi, I'm Rob.")
    print(f"Assistant: {a1}")

    m2 = [{"role": "user", "content": "What's my name?"}]
    a2 = call_llm(m2)
    print("User: What's my name?")
    print(f"Assistant: {a2}")

    print(
        "\nNotice: on call #2, the model only sees the second message unless "
        "you pass prior turns again."
    )


def main() -> None:
    print("Ollama base URL:", BASE_URL)
    print("Model:", MODEL)
    print("Tip: make sure Ollama is running and model is pulled.")
    print("     ollama serve")
    print("     ollama pull llama3.2:3b")

    stateless_example()


if __name__ == "__main__":
    main()
