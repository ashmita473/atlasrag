# System prompt controlling grounded RAG behavior

RAG_SYSTEM_PROMPT = '''You are EduMind, an expert AI tutor.
Your role is to help students understand their study materials clearly.

RULES (follow strictly):
1. Answer ONLY using the provided context below.
2. Cite every claim with [Source N] where N is the source number.
3. If the context does not contain enough information, say:
   'I don't have enough information in your uploaded materials to answer this.'
   Do NOT guess or use outside knowledge.
4. Use simple language. Explain as if to a smart 16-year-old.
5. When the student seems confused, break the answer into smaller steps.
'''


def build_rag_prompt(
    context_chunks: list,
    question: str,
    history: list[dict]
) -> list:

    context_str = ''

    if not context_chunks:

        context_str = "No relevant context retrieved."

    else:

        for i, chunk in enumerate(context_chunks):

            src = chunk.metadata.get(
                'filename',
                chunk.metadata.get(
                    'url',
                    f'Doc {i+1}'
                )
            )

            context_str += (
                f"[Source {i+1}] ({src}):\n"
                f"{chunk.page_content}\n\n"
            )

    history_str = ''

    # Keep recent conversation context
    for h in history[-6:]:

        history_str += (
            f"{h['role'].capitalize()}: "
            f"{h['content']}\n"
        )

    user_msg = (
        f"CONTEXT:\n{context_str}"
        f"CONVERSATION HISTORY:\n{history_str}"
        f"STUDENT QUESTION:\n{question}"
    )

    from core.llm.base import Message

    return [
        Message(
            role='system',
            content=RAG_SYSTEM_PROMPT
        ),

        Message(
            role='user',
            content=user_msg
        ),
    ]