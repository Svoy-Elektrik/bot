import anthropic
import os

client = anthropic.Anthropic(api_key=os.getenv("CLAUDE_API_KEY"))

def generate_text(prompt: str, max_tokens: int = 1500):
    response = client.messages.create(
        model="claude-3-5-sonnet-latest",
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text
