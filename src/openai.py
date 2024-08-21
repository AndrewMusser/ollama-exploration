import openai

openai.api_key = "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"

response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is 2x2?"}
    ]
)

print(response['choices'][0]['message']['content'])
