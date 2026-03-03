import os
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
FREE_MODELS = [
    "openrouter/free",
    "arcee-ai/trinity-large-preview:free",
    "arcee-ai/trinity-mini:free",
    "deepseek/deepseek-r1:free",
    "google/gemma-2b-it:free",
    "google/gemma-7b-it:free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "meta-llama/llama-3.1-8b-instruct:free",
    "microsoft/phi-3-mini-4k-instruct:free",
    "mistralai/mistral-7b-instruct:free",
    "qwen/qwen2.5-7b-instruct:free",
]

MODEL_DISPLAY_NAMES = {
    "openrouter/free": "Free Models Router (Recommended)",
    "arcee-ai/trinity-large-preview:free": "Trinity Large Preview",
    "arcee-ai/trinity-mini:free": "Trinity Mini (Fast)",
    "deepseek/deepseek-r1:free": "DeepSeek R1 (Reasoning)",
    "google/gemma-2b-it:free": "Gemma 2B (Lightweight)",
    "google/gemma-7b-it:free": "Gemma 7B",
    "meta-llama/llama-3.3-70b-instruct:free": "Llama 3.3 70B",
    "meta-llama/llama-3.1-8b-instruct:free": "Llama 3.1 8B",
    "microsoft/phi-3-mini-4k-instruct:free": "Phi-3 Mini",
    "mistralai/mistral-7b-instruct:free": "Mistral 7B",
    "qwen/qwen2.5-7b-instruct:free": "Qwen 2.5 7B",
}

LEVELS = ["Beginner", "Intermediate", "Advanced"]
MAX_HISTORY_MESSAGES = 20
REQUEST_TIMEOUT_SECONDS = 60


def build_system_prompt(level: str) -> str:
    return f"""
You are an AI Tutor helping a {level} learner.
Adapt the depth and vocabulary to this level.

For every answer, use exactly this structure with section headers:
1) Simple explanation
2) Real-world example
3) Mathematical explanation
4) 2 quiz questions
5) Suggest next topic

Rules:
- Keep explanations accurate, clear, and educational.
- If the user asks a non-educational question, gently steer back to learning.
- If the user asks unsafe content, refuse briefly and suggest a safe study alternative.
- Use markdown formatting for readability.
""".strip()


def sanitize_history(messages: list[dict]) -> list[dict]:
    sanitized = [m for m in messages if m.get("role") in {"user", "assistant"} and m.get("content")]
    return sanitized[-MAX_HISTORY_MESSAGES:]


def get_model_candidates() -> list[str]:
    preferred_model = os.getenv("OPENROUTER_MODEL", "").strip()
    if preferred_model:
        return [preferred_model, *FREE_MODELS]
    
    if hasattr(st.session_state, "selected_model") and st.session_state.selected_model:
        selected = st.session_state.selected_model
        if selected in FREE_MODELS:
            return [selected] + [m for m in FREE_MODELS if m != selected]
    
    return FREE_MODELS


def is_model_unavailable_response(response: requests.Response) -> bool:
    if response.status_code not in {400, 404}:
        return False

    try:
        payload = response.json()
    except ValueError:
        return False

    error_text = str(payload).lower()
    return (
        "model_not_available" in error_text
        or "unable to access non-serverless model" in error_text
        or "no endpoints found" in error_text
        or "no endpoint" in error_text
        or "not found" in error_text
    )


def call_openrouter(api_key: str, level: str, history: list[dict], user_message: str) -> str:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    messages = [{"role": "system", "content": build_system_prompt(level)}]
    messages.extend(sanitize_history(history))
    messages.append({"role": "user", "content": user_message})

    last_error: str | None = None

    for model_name in get_model_candidates():
        payload = {
            "model": model_name,
            "messages": messages,
            "temperature": 0.5,
        }

        try:
            response = requests.post(
                OPENROUTER_URL,
                headers=headers,
                json=payload,
                timeout=REQUEST_TIMEOUT_SECONDS,
            )
        except requests.exceptions.Timeout as exc:
            raise RuntimeError("Request timed out. Please try again.") from exc
        except requests.exceptions.RequestException as exc:
            raise RuntimeError("Network error while contacting OpenRouter.") from exc

        if response.status_code == 200:
            data = response.json()
            try:
                return data["choices"][0]["message"]["content"].strip()
            except (KeyError, IndexError, TypeError) as exc:
                raise RuntimeError("Unexpected response format from OpenRouter.") from exc

        if is_model_unavailable_response(response):
            last_error = f"Model unavailable: {model_name}"
            continue

        details = response.text[:500]
        raise RuntimeError(f"OpenRouter API error ({response.status_code}): {details}")

    raise RuntimeError(
        last_error
        or "No available free OpenRouter model could be used. Try again later or set OPENROUTER_MODEL to another :free model."
    )


def init_session_state() -> None:
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "level" not in st.session_state:
        st.session_state.level = "Beginner"
    if "selected_model" not in st.session_state:
        st.session_state.selected_model = FREE_MODELS[0]


def render_chat_history(messages: list[dict]) -> None:
    for msg in messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])


def main() -> None:
    st.set_page_config(page_title="AI Tutor", page_icon="🎓", layout="centered")

    st.title("🎓 AI Tutor")
    st.caption("Learn any topic with structured explanations, examples, math, and quizzes.")

    init_session_state()

    with st.sidebar:
        st.header("Settings")
        
        model_display_options = [MODEL_DISPLAY_NAMES.get(m, m) for m in FREE_MODELS]
        current_index = FREE_MODELS.index(st.session_state.selected_model) if st.session_state.selected_model in FREE_MODELS else 0
        
        selected_display = st.selectbox(
            "Choose AI Model",
            options=model_display_options,
            index=current_index,
            help="Free Models Router automatically selects the best available free model"
        )
        
        selected_model_id = FREE_MODELS[model_display_options.index(selected_display)]
        if selected_model_id != st.session_state.selected_model:
            st.session_state.selected_model = selected_model_id
            st.success(f"Model updated to {selected_display}")
        
        st.markdown("---")
        
        selected_level = st.selectbox(
            "Choose your learning level",
            options=LEVELS,
            index=LEVELS.index(st.session_state.level),
        )

        if selected_level != st.session_state.level:
            st.session_state.level = selected_level
            st.info("Learning level updated. New responses will follow this level.")

        if st.button("Clear chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

        st.markdown("---")
        st.markdown("💡 **Tip**: Use Free Models Router for automatic best model selection")
        st.markdown("Set your OpenRouter key as environment variable: `OPENROUTER_API_KEY`.")

    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        st.error("Missing OPENROUTER_API_KEY environment variable.")
        st.stop()

    render_chat_history(st.session_state.messages)

    user_prompt = st.chat_input("Ask me to teach any topic...")
    if not user_prompt:
        return

    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.markdown("Thinking...")

        try:
            assistant_text = call_openrouter(
                api_key=api_key,
                level=st.session_state.level,
                history=st.session_state.messages,
                user_message=user_prompt,
            )
            placeholder.markdown(assistant_text)
            st.session_state.messages.append({"role": "assistant", "content": assistant_text})
        except RuntimeError as exc:
            error_msg = f"⚠️ {exc}"
            placeholder.markdown(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})


if __name__ == "__main__":
    main()
