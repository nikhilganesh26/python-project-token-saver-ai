import time
import database
import llm

database.init_db()

def check(prompt, user_id, force_fresh=False):
    """Checks the database for this prompt.
    Hit  -> return the saved answer straight back to the frontend.
    Miss -> send the prompt to llm.py, which hands the answer on to promptsaver.py.
    """
    start = time.time()

    found = None if force_fresh else database.find_exact(prompt)

    if found:
        answer, tokens = found
        database.log_request(user_id, prompt, was_hit=True)
        return {
            "answer": answer,
            "source": "cache",
            "tokens": tokens,
            "seconds": time.time() - start,
        }

    database.log_request(user_id, prompt, was_hit=False)
    return llm.answer(prompt, user_id, start)