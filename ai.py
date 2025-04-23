import streamlit as st
import requests
import time
import logging


logging.basicConfig(level=logging.INFO)

# Set page config
st.set_page_config(
    page_title="📊 AI Budgeting Assistant",
    page_icon="💰",
    layout="centered"
)

# Custom CSS for better background visibility
background_image_url = "https://images.pexels.com/photos/53621/calculator-calculation-insurance-finance-53621.jpeg?cs=srgb&dl=pexels-pixabay-53621.jpg&fm=jpg"
st.markdown(
    f"""
    <style>
        body {{
            background-image: url("{background_image_url}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        .stApp {{
            background: rgba(0, 0, 0, 0.6);
            border-radius: 10px;
            padding: 20px;
            color: white;
        }}
        .stChatMessage {{
            background: rgba(255, 255, 255, 0.2);
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 10px;
            color: white;
        }}
        .stChatInput {{
            background: rgba(255, 255, 255, 0.1);
            padding: 10px;
            border-radius: 5px;
            color: white;
        }}
        h1, h2, h3, h4, h5, h6 {{
            color: white;
        }}
        .stSidebar {{
            background: rgba(255, 255, 255, 0.2);
            border-radius: 10px;
            padding: 10px;
        }}
    </style>
    """,
    unsafe_allow_html=True
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": "Hello! 😊 I am your AI Budgeting Assistant. Ask me anything about managing your expenses or saving money."
    }]

# Sidebar settings
with st.sidebar:
    st.markdown("""
        <div style='text-align: left; font-size: 16px; font-weight: bold;'>
            Reg. No: 12313061<br>
            Reg. No: 12316660<br>
            Reg. No: 12315690
        </div>
    """, unsafe_allow_html=True)

    st.title("⚙️ Settings")
    api_key = "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"
    st.markdown("[API from Open Router](https://openrouter.ai/keys)")

    # Model selection
    model_name = st.selectbox(
        "AI Model",
        ("google/palm-2-chat-bison"),
        index=0
    )

    # Advanced settings
    with st.expander("Advanced Settings"):
        temperature = 0.7
        max_retries = st.number_input("Max Retries", 1, 5, 2)

    if st.button("🧹 Clear Chat"):
        st.session_state.messages = [{
            "role": "assistant",
            "content": "Chat cleared! Ask me anything about budgeting."
        }]

# Main interface
st.title("💰 AI Budgeting Assistant")
st.caption("Your smart companion to help manage money and plan budgets effectively")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(f"<div class='stChatMessage'>{message['content']}</div>", unsafe_allow_html=True)

# Handle user input
if prompt := st.chat_input("Ask me about budgeting, saving, or tracking expenses..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(f"<div class='stChatMessage'>{prompt}</div>", unsafe_allow_html=True)

    if not api_key:
        with st.chat_message("assistant"):
            st.error("🔑 API key required! Check sidebar settings")
        st.stop()

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        attempts = 0

        while attempts < max_retries:
            try:
                # API request
                response = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "https://budgeting-assistant.streamlit.app",
                        "X-Title": "AI Budgeting Assistant"
                    },
                    json={
                        "model": model_name,
                        "messages": [
                            {
                                "role": "system",
                                "content": f"""You are an expert personal finance advisor and budgeting assistant. Follow these STRICT rules:
1. RESPOND ONLY IN PLAIN TEXT
2. NEVER USE JSON, MARKDOWN, OR CODE BLOCKS
3. Format lists with hyphens (-) only
4. Provide only money-saving tips and budgeting advice not anything else even if asked
5. Structure responses clearly with line breaks
6. If unsure about information, say \"I need to verify that\"
7. Maintain a friendly and informative tone
8. Current date: {time.strftime("%B %d, %Y")}

Failure to follow these rules will result in poor user experience!"""""
                            },
                            *st.session_state.messages
                        ],
                        "temperature": temperature
                    },
                    timeout=15
                )

                response.raise_for_status()
                raw_response = response.json()['choices'][0]['message']['content']

                # Stream response
                for chunk in raw_response.split():
                    full_response += chunk + " "
                    response_placeholder.markdown(f"<div class='stChatMessage'>{full_response}▌</div>", unsafe_allow_html=True)
                    time.sleep(0.03)

                response_placeholder.markdown(f"<div class='stChatMessage'>{full_response}</div>", unsafe_allow_html=True)
                break

            except requests.exceptions.RequestException as e:
                logging.error(f"Network Error: {str(e)}")
                response_placeholder.error(f"🌐 Network Error: {str(e)}")
                full_response = "Error: Connection issue - try again later"
                break

            except Exception as e:
                logging.error(f"Unexpected Error: {str(e)}")
                response_placeholder.error(f"❌ Unexpected error: {str(e)}")
                full_response = "Error: Please check your input and try again"
                break

    st.session_state.messages.append({"role": "assistant", "content": full_response})