import os
from openai import OpenAI
from dotenv import load_dotenv
from pydantic import BaseModel

class StoryResponse(BaseModel):
    title: str
    story: str


load_dotenv()

MODEL = os.environ["MODEL"]

def create_client() -> OpenAI:
    return OpenAI()

def get_user_prompt() -> str:
    return input("Enter your prompt: ").strip()

def build_story_request(user_prompt: str) -> str:
    return (
        "Write a creative story based on the user's idea.\n"
        "Follow the requested audience, tone, format, and length from the user idea.\n"
        "Return a short title and the full story content.\n\n"
        f"User idea: {user_prompt}"
    )

def generate_story_json(client: OpenAI, prompt: str, *, model: str = MODEL) -> dict:
    response = client.responses.parse(
        model=model,
        input=[{"role": "user", "content": prompt}],
        text_format=StoryResponse,
    )
    return response.output_parsed

def main() -> None:
    client = create_client()
    user_prompt = get_user_prompt()
    prompt = build_story_request(user_prompt)
    out = generate_story_json(client, prompt)

    print(out.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
