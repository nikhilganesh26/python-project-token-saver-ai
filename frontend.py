import threading
import streamlit as st
import dbchecker

CSS = """
<style>
#MainMenu, footer {visibility: hidden;}
.block-container {max-width: 820px; padding-top: 2rem;}
.welcome {text-align: center; margin-top: 18vh;}
.welcome h1 {font-size: 2.2rem; margin-bottom: 0.3rem;}
.welcome p {opacity: 0.65;}
</style>
"""

@st.cache_resource
def _user_counter():
    """One counter shared by every tab for as long as the server runs."""
    return {"n": 0, "lock": threading.Lock()}

def _next_user_name():
    counter = _user_counter()
    with counter["lock"]:
        counter["n"] += 1
        return f"user{counter['n']}"

def _init_state():
    defaults = {"messages": [], "tokens_used": 0, "tokens_saved": 0,
                "requests": 0, "hits": 0}
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)

def _notice(source):
    if source == "cache":
        st.success("♻️ Asked before. This answer came from the saved cache, "
                   "so the model wasn't used.")
    else:
        st.info("🆕 New prompt. Nobody has asked this before, so the model "
                "answered it and it's now saved for next time.")

def _caption(result):
    from_cache = result["source"] == "cache"
    label = "⚡ Cache" if from_cache else "🤖 Model"
    verb = "saved" if from_cache else "used"
    return f"{label} · {result.get('tokens', 0):,} tokens {verb} · {result['seconds']:.2f}s"

def render():
    st.set_page_config(page_title="TokenSaver AI", page_icon="💾")
    st.markdown(CSS, unsafe_allow_html=True)
    _init_state()

    # Sidebar
    with st.sidebar:
        st.title("💾 TokenSaver AI")
        if st.button("➕ New chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

        if "default_name" not in st.session_state:
            st.session_state.default_name = _next_user_name()
        user_id = st.text_input("Your name", value=st.session_state.default_name)

        fresh = st.checkbox("Skip cache (force a fresh answer)")
        st.divider()
        counters = st.container()  # filled at the end so it's up to date

    # Welcome screen or conversation
    if not st.session_state.messages:
        st.markdown(
            '<div class="welcome"><h1>What can I help with?</h1>'
            "<p>Every prompt is checked against the cache before the model runs.</p></div>",
            unsafe_allow_html=True,
        )

    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            if m.get("source"):
                _notice(m["source"])
            st.markdown(m["content"])
            if m.get("caption"):
                st.caption(m["caption"])

    # New prompt
    prompt = st.chat_input("Message TokenSaver AI...")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            try:
                with st.spinner("Checking whether this was asked before..."):
                    result = dbchecker.check(prompt, user_id, fresh)
            except RuntimeError as e:
                st.error(str(e))
            else:
                _notice(result["source"])
                st.markdown(result["answer"])
                caption = _caption(result)
                st.caption(caption)

                tokens = result.get("tokens", 0)
                st.session_state.requests += 1
                if result["source"] == "cache":
                    st.session_state.hits += 1
                    st.session_state.tokens_saved += tokens
                else:
                    st.session_state.tokens_used += tokens

                st.session_state.messages.append({
                    "role": "assistant", "content": result["answer"],
                    "source": result["source"], "caption": caption,
                })

    # Token counter
    with counters:
        st.subheader("Token counter")
        col1, col2 = st.columns(2)
        col1.metric("Used", f"{st.session_state.tokens_used:,}")
        col2.metric("Saved", f"{st.session_state.tokens_saved:,}")
        st.metric("Answered from cache",
                  f"{st.session_state.hits} of {st.session_state.requests}")

if __name__ == "__main__":
    render()