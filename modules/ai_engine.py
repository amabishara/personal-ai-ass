from openai import OpenAI

from config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)


def get_ai_response(user_input, user_context="", assistant_role=None):
    try:
        role = assistant_role or "You are a personalized productivity assistant."
        system_prompt = f"{role} Context: {user_context}"

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input},
            ],
        )
        return response.choices[0].message.content
    except Exception as error:
        return f"AI Service Offline. Please check your API key. (Error: {error})"
