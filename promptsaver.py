import time
import database

database.init_db()

def save_and_return(prompt, answer, tokens, user_id, start):
    """Called by llm.py after the model answers.
    Saves the prompt and answer to the local database, then returns the
    final result for the frontend to display."""
    database.save(prompt, answer, tokens, user_id)
    return {
        "answer": answer,
        "source": "model",
        "tokens": tokens,
        "seconds": time.time() - start,
    }