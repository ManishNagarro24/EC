import openai
openai.api_key = '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'
def call_gpt(prompt):
    final_prompt = "Write me a professionally sounding email "
    final_prompt+="Your role is of an email creator for marketing purpose. "
    final_prompt+=prompt
    final_prompt+=" Generate an email content based on above info"
    response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=final_prompt,
            max_tokens=1000,
            temperature=0,
            stop=None
        )
    generated_content = response.choices[0].text.strip()
    return generated_content

if __name__ == '__main__':
    call_gpt()