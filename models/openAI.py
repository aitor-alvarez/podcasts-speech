import openai
from creds.creds import OPENAI_KEY

openai.api_key = OPENAI_KEY


def get_completion_response(instruction, engine="gpt-3.5-turbo"):
    try:
        response = openai.ChatCompletion.create(
            model=engine,
            messages=instruction
        )
        return response
    except openai.error.OpenAIError as e:
        print(f"OpenAIError: {e}.")
        if "Please reduce your prompt" in str(e):
            print(f"The following prompt is too long: \n {instruction}")
        return None
