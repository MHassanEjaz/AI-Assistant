import os
from dotenv import load_dotenv
from exa_py import Exa
from cerebras.cloud.sdk import Cerebras

# --------------------------------------------------
# Load Environment Variables
# --------------------------------------------------
load_dotenv()

CEREBRAS_API_KEY = os.getenv("CEREBRAS_API_KEY")
EXA_API_KEY = os.getenv("EXA_API_KEY")

if not CEREBRAS_API_KEY:
    raise ValueError("❌ Cerebras API key not found. Check your environment variables.")
if not EXA_API_KEY:
    raise ValueError("❌ Exa API key not found. Check your environment variables.")

# Initialize API clients
exa = Exa(api_key=EXA_API_KEY)
client = Cerebras(api_key=CEREBRAS_API_KEY)


# --------------------------------------------------
# Web Search Function
# --------------------------------------------------
def search_web(query, num=5):
    result = exa.search_and_contents(
        query,
        type="auto",
        num_results=num,
        text={"max_characters": 800},
    )

    sources = []
    for r in result.results:
        if r.text:
            sources.append({
                "title": r.title,
                "url": getattr(r, "url", ""),
                "content": r.text[:600]
            })

    return sources


# --------------------------------------------------
# AI Response Function
# --------------------------------------------------
def ask_ai(prompt, max_tokens=800):
    response = client.chat.completions.create(
        model="gpt-oss-120b",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        temperature=0.7,
    )

    return response.choices[0].message.content


# --------------------------------------------------
# Depth Research (2-Layer)
# --------------------------------------------------
def deeper_research_topic(query):
    # Layer 1 Search
    sources_layer1 = search_web(query, 6)

    if not sources_layer1:
        return {"response": "No sources found.", "sources": []}

    # Generate follow-up query
    context_preview = "\n".join(
        [f"{s['title']}: {s['content'][:250]}" for s in sources_layer1[:4]]
    )

    follow_up_prompt = f"""
    Based on this research preview:

    {context_preview}

    What is the best follow-up search query to deepen understanding of:
    "{query}"

    Respond with only the search query.
    """

    follow_up_query = ask_ai(follow_up_prompt).strip().replace('"', "")

    # Layer 2 Search
    sources_layer2 = search_web(follow_up_query, 4)

    all_sources = sources_layer1 + sources_layer2

    # Final Analysis
    full_context = "\n\n".join(
        [f"{s['title']} ({s['url']}): {s['content']}" for s in all_sources[:8]]
    )

    final_prompt = f"""
    Using all research below:

    {full_context}

    Provide:

    SUMMARY:
    (3-4 professional sentences)

    KEY INSIGHTS:
    - Insight 1
    - Insight 2
    - Insight 3
    - Insight 4

    DEPTH GAINED:
    (1 sentence explaining what new understanding the follow-up search added)
    """

    final_response = ask_ai(final_prompt)

    return {
        "response": final_response,
        "sources": all_sources
    }


# --------------------------------------------------
# Multi-Agent Research
# --------------------------------------------------
def anthropic_multiagent_research(query):

    sub_queries = [
        f"{query} core fundamentals",
        f"{query} latest developments 2026",
        f"{query} applications and industry impact"
    ]

    subagents = []

    for i, q in enumerate(sub_queries, 1):
        results = search_web(q, 3)
        subagents.append({
            "subtask": i,
            "search_focus": q,
            "sources": results
        })

    combined_context = ""

    for sub in subagents:
        for s in sub["sources"]:
            combined_context += f"{s['title']} ({s['url']}): {s['content']}\n\n"

    synthesis_prompt = f"""
    ORIGINAL QUERY: {query}

    Research Data:
    {combined_context}

    Provide:

    EXECUTIVE SUMMARY:
    (2-3 strong sentences)

    INTEGRATED FINDINGS:
    • Key foundational insight
    • Key recent development
    • Key real-world application
    • Cross-cutting strategic insight

    STRATEGIC IMPLICATIONS:
    (Short forward-looking insight)
    """

    synthesis = ask_ai(synthesis_prompt)

    return {
        "synthesis": synthesis,
        "subagents": subagents
    }
