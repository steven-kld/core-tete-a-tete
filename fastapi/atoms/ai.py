import os, openai
from dotenv import load_dotenv

load_dotenv()

def init_openai():
    return openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def respond_with_ai(prompt, openai_client, max_tokens=1000, model="gpt-4.1", role="user"):
    response = openai_client.chat.completions.create(
        model=model,
        messages=[{
            "role": role,
            "content": prompt
        }],
        response_format={
            "type": "text"
        },
        temperature=0,
        max_tokens=max_tokens,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )

    input_tokens = response.usage.prompt_tokens       # ← number of input tokens
    output_tokens = response.usage.completion_tokens   # ← number of output tokens
    in_cost, out_cost = gpt_cost(model, input_tokens, output_tokens)

    return response.choices[0].message.content, in_cost, out_cost

def gpt_cost(model: str, input_tokens: int, output_tokens: int):
    PRICING = {
        "gpt-4.1": {
            "input": 2.00 / 1000000,
            "output": 8.00 / 1000000
        },
        "gpt-4.1-mini": {
            "input": 0.40 / 1000000,
            "output": 1.60 / 1000000
        },
        "gpt-4.1-nano": {
            "input": 0.10 / 1000000,
            "output": 0.40 / 1000000
        }
    }
    p = PRICING[model]
    return round(input_tokens * p["input"], 6), round(output_tokens * p["output"], 6)

