# import streamlit as st
# from main import deeper_research_topic, anthropic_multiagent_research

# st.set_page_config(
#     page_title="AI Deep Research Assistant",
#     page_icon="🚀",
#     layout="wide"
# )

# st.title("🚀 AI Deep Research Assistant")
# st.markdown("Professional multi-layer AI research powered by Cerebras + Exa")

# st.divider()

# # Input
# topic = st.text_input("Enter research topic:")

# mode = st.radio(
#     "Select Research Mode:",
#     ["Depth Search", "Multi-Agent Research"],
#     horizontal=True
# )

# st.divider()

# if st.button("Start Research") and topic.strip():

#     with st.spinner("🔍 Conducting deep research..."):

#         try:
#             if mode == "Depth Search":
#                 result = deeper_research_topic(topic)

#                 st.subheader("📊 Research Report")
#                 st.write(result["response"])

#                 st.subheader("🔗 Sources")
#                 for s in result["sources"]:
#                     st.markdown(f"- [{s['title']}]({s['url']})")

#             else:
#                 result = anthropic_multiagent_research(topic)

#                 st.subheader("📊 Executive Synthesis")
#                 st.write(result["synthesis"])

#                 st.subheader("🔗 Subagent Sources")

#                 for sub in result["subagents"]:
#                     st.markdown(f"### Subtask {sub['subtask']}")
#                     st.markdown(f"Focus: *{sub['search_focus']}*")
#                     for s in sub["sources"]:
#                         st.markdown(f"- [{s['title']}]({s['url']})")

#         except Exception as e:
#             st.error(f"❌ Error during research: {e}")


import streamlit as st
import uuid
import time
from main import deeper_research_topic, anthropic_multiagent_research
from cerebras.cloud.sdk import Cerebras
import os

st.set_page_config(page_title="AI Research Assistant", layout="wide")

# -----------------------------------
# Initialize Cerebras Client (For Title Generator)
# -----------------------------------
cerebras_client = Cerebras(api_key=os.getenv("CEREBRAS_API_KEY"))

# -----------------------------------
# Function: Generate Chat Title
# -----------------------------------
def generate_chat_title(topic):
    try:
        response = cerebras_client.chat.completions.create(
            model="llama3.1-8b",
            messages=[
                {"role": "system", "content": "Generate a short 4-6 word title for this research topic."},
                {"role": "user", "content": topic}
            ],
            max_tokens=20
        )
        return response.choices[0].message.content.strip()
    except:
        return topic[:30]  # fallback
        

# -----------------------------------
# Session State Setup
# -----------------------------------
if "conversations" not in st.session_state:
    st.session_state.conversations = {}

if "chat_titles" not in st.session_state:
    st.session_state.chat_titles = {}

if "current_chat" not in st.session_state:
    chat_id = str(uuid.uuid4())
    st.session_state.current_chat = chat_id
    st.session_state.conversations[chat_id] = []
    st.session_state.chat_titles[chat_id] = "New Chat"

# -----------------------------------
# Sidebar
# -----------------------------------
st.sidebar.title("💬 Conversations")

if st.sidebar.button("➕ New Chat"):
    chat_id = str(uuid.uuid4())
    st.session_state.current_chat = chat_id
    st.session_state.conversations[chat_id] = []
    st.session_state.chat_titles[chat_id] = "New Chat"

for chat_id, title in st.session_state.chat_titles.items():
    if st.sidebar.button(title):
        st.session_state.current_chat = chat_id

# -----------------------------------
# Main Chat Area
# -----------------------------------
st.title("🚀 AI Deep Research Assistant")

current_chat = st.session_state.current_chat
messages = st.session_state.conversations[current_chat]

# Show old messages
for msg in messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Research Mode Selector
mode = st.radio(
    "Research Mode",
    ["Depth Search", "Multi-Agent Research"],
    horizontal=True
)

# -----------------------------------
# Chat Input
# -----------------------------------
user_input = st.chat_input("Enter research topic...")

if user_input:
    messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    # Auto-generate title if first message
    if len(messages) == 1:
        new_title = generate_chat_title(user_input)
        st.session_state.chat_titles[current_chat] = new_title

    with st.chat_message("assistant"):
        progress = st.empty()

        # Step 1
        progress.markdown("🔎 **Searching sources...**")
        time.sleep(1)

        # Step 2
        progress.markdown("🧠 **Analyzing information...**")
        time.sleep(1)

        # Step 3
        progress.markdown("✍ **Synthesizing final report...**")
        time.sleep(1)

        # Run actual research
        if mode == "Depth Search":
            result = deeper_research_topic(user_input)
            response = result["response"]

            source_text = "\n\n### 🔗 Sources\n"
            for s in result["sources"]:
                source_text += f"- [{s['title']}]({s['url']})\n"

            response += source_text

        else:
            result = anthropic_multiagent_research(user_input)
            response = result["synthesis"]

            source_text = "\n\n### 🔗 Sources\n"
            for sub in result["subagents"]:
                source_text += f"\n**Subtask {sub['subtask']} ({sub['search_focus']})**\n"
                for s in sub["sources"]:
                    source_text += f"- [{s['title']}]({s['url']})\n"

            response += source_text

        progress.empty()
        st.markdown(response)

    messages.append({"role": "assistant", "content": response})
