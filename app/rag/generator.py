import logging

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)


def generate_answer(question: str, contexts: list[dict]) -> str:
    settings = get_settings()

    context = "\n\n---\n\n".join(c["text"] for c in contexts)
    context = context[: settings.max_context_chars]

    prompt = f"""You are RAGForge, a grounded question-answering assistant.

Use ONLY the supplied context.
Do not invent facts.
If the answer is not contained in the context, clearly say that the
indexed documents do not contain enough information.

CONTEXT:
{context}

QUESTION:
{question}

ANSWER:"""

    try:
        response = httpx.post(
            f"{settings.ollama_base_url.rstrip('/')}/api/generate",
            json={
                "model": settings.ollama_model,
                "prompt": prompt,
                "stream": False,
            },
            timeout=120,
        )

        response.raise_for_status()

        answer = response.json().get("response", "").strip()

        if answer:
            return answer

    except httpx.HTTPError as exc:
        logger.warning("Ollama generation failed: %s", exc)

    # Deterministic fallback keeps RAGForge usable when Ollama
    # is unavailable. Retrieval and source attribution still work.
    return "Relevant information retrieved from the indexed documents:\n\n" + context
