"""
Part 1 - Token/Cost Optimization

Problem: agent pipeline was using ~100K tokens per query, too expensive.
Implemented 2 fixes: RAG (send only relevant chunk) and history summarization.

"""


def count_tokens(text):
    # rough approximation, ~4 chars per token for english text
    return max(1, len(text) // 4)


# fake big document to simulate the "too much context" problem
FAKE_LARGE_DOCUMENT = """
[Company Policy Document - Section 1: Leave Policy]
Employees are entitled to 24 paid leaves per year...
""" * 50

USER_QUERY = "How many paid leaves do I get per year?"


def naive_approach(query, full_document):
    # sends the whole document every time - this is the expensive way
    prompt = f"""
    You are a helpful assistant. Answer the user's question using the
    document below.

    DOCUMENT:
    {full_document}

    QUESTION: {query}
    """
    return prompt


def rag_approach(query, full_document):
    # only grab the paragraphs that look relevant instead of sending everything
    # in a real setup this would be embeddings + a vector db (mongodb atlas
    # vector search / pinecone etc), keeping it simple here with keyword match
    paragraphs = full_document.split("\n")
    relevant = [p for p in paragraphs if "leave" in p.lower()][:2]
    relevant_context = "\n".join(relevant)

    prompt = f"""
    You are a helpful assistant. Answer the user's question using the
    relevant context below.

    RELEVANT CONTEXT:
    {relevant_context}

    QUESTION: {query}
    """
    return prompt


def simulate_long_history():
    # pretend this is a long back and forth conversation
    messages = [
        {"role": "user", "content": "Hi, I want to know about my leaves"},
        {"role": "assistant", "content": "Sure, I can help with that. Are you full-time or part-time?"},
        {"role": "user", "content": "I'm full-time"},
        {"role": "assistant", "content": "Great, full-time employees get different leave categories..."},
        {"role": "user", "content": "What about sick leave separately?"},
        {"role": "assistant", "content": "Sick leave is tracked separately from paid leave..."},
    ] * 5
    return messages


def naive_history(messages, query):
    history_text = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
    return f"CONVERSATION HISTORY:\n{history_text}\n\nNEW QUESTION: {query}"


def summarized_history(messages, query):
    # in production this summary would come from an actual LLM call
    # (something like "summarize this conversation in 1-2 lines"), hardcoding
    # it here since I don't have API access set up in this environment
    summary = "User is a full-time employee asking about leave policy, specifically paid and sick leave."
    return f"CONVERSATION SUMMARY:\n{summary}\n\nNEW QUESTION: {query}"


if __name__ == "__main__":
    before_prompt = naive_approach(USER_QUERY, FAKE_LARGE_DOCUMENT)
    after_prompt = rag_approach(USER_QUERY, FAKE_LARGE_DOCUMENT)

    before_tokens = count_tokens(before_prompt)
    after_tokens = count_tokens(after_prompt)

    print("RAG vs full document")
    print(f"before: {before_tokens} tokens, after: {after_tokens} tokens")
    print(f"reduction: {round((1 - after_tokens/before_tokens) * 100, 1)}%\n")

    messages = simulate_long_history()
    before_hist = naive_history(messages, "Can you remind me the leave count?")
    after_hist = summarized_history(messages, "Can you remind me the leave count?")

    before_hist_tokens = count_tokens(before_hist)
    after_hist_tokens = count_tokens(after_hist)

    print("summarized vs full history")
    print(f"before: {before_hist_tokens} tokens, after: {after_hist_tokens} tokens")
    print(f"reduction: {round((1 - after_hist_tokens/before_hist_tokens) * 100, 1)}%")
