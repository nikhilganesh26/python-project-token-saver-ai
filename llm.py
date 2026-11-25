import ollama

MODEL = "llama3.2:1b"   # change this one word to switch models later

def ask_model(prompt):
    """Asks Ollama and returns (answer, tokens). Raises RuntimeError if it fails."""
    try:
        response = ollama.chat(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
        )
    except Exception as e:
        raise RuntimeError(
            f"Could not get an answer from Ollama. Is it running, and is "
            f"'{MODEL}' downloaded? ({e})"
        )

    answer = response["message"]["content"].strip()
    if not answer:
        raise RuntimeError("The model returned an empty answer, so nothing was saved.")

    # Ollama reports real token counts: prompt tokens + generated tokens
    tokens = (response.get("prompt_eval_count") or 0) + (response.get("eval_count") or 0)
    return answer, tokens

def answer(prompt, user_id, start):
    """Called by dbchecker.py on a cache miss.
    Answers the prompt, then hands prompt + answer to promptsaver.py,
    which saves them and returns the final result for the frontend."""
    import promptsaver
    text, tokens = ask_model(prompt)
    return promptsaver.save_and_return(prompt, text, tokens, user_id, start)