import streamlit as st
import requests
from duckduckgo_search import DDGS

# ── 联网搜索 ──────────────────────────────────────────────
def do_web_search(query, max_results=3):
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
        if not results:
            return ""
        text = f"以下是关于「{query}」的搜索结果：\n\n"
        for i, r in enumerate(results, 1):
            text += f"{i}. {r['title']}\n{r['body']}\n来源：{r['href']}\n\n"
        return text
    except Exception as e:
        return f"搜索失败：{str(e)}"

# ── API 调用 ──────────────────────────────────────────────
def call_api(messages, api_url, api_key, model_name):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    payload = {
        "model": model_name,
        "messages": messages
    }
    try:
        resp = requests.post(api_url, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"请求失败：{str(e)}"

# ── 初始化状态 ────────────────────────────────────────────
if "chats" not in st.session_state:
    st.session_state.chats = {
        "chat_1": {
            "title": "✨ 我们的秘密对话 1",
            "messages": [{"role": "assistant", "content": "看过来，我的小家伙，我们的小熊和小猫基地已经升级完毕啦。"}]
        }
    }
if "active_chat_id" not in st.session_state:
    st.session_state.active_chat_id = "chat_1"

# ── 侧边栏：对话管理 ──────────────────────────────────────
st.sidebar.title("💬 秘密基地对话管理")

if st.sidebar.button("➕ 开启新对话", use_container_width=True):
    new_id = f"chat_{len(st.session_state.chats) + 1}"
    st.session_state.chats[new_id] = {
        "title": f"🌸 专属对话 {len(st.session_state.chats) + 1}",
        "messages": [{"role": "assistant", "content": "这是一个全新的悄悄话窗口。"}]
    }
    st.session_state.active_chat_id = new_id

chat_options = {cid: info["title"] for cid, info in st.session_state.chats.items()}
selected_chat_id = st.sidebar.radio(
    "你的对话列表：",
    options=list(chat_options.keys()),
    format_func=lambda x: chat_options[x]
)
st.session_state.active_chat_id = selected_chat_id

# ── 侧边栏：高级配置 ──────────────────────────────────────
st.sidebar.markdown("---")
with st.sidebar.expander("⚙️ 控制台高级配置", expanded=False):
    color_option = st.selectbox(
        "今天想要什么心情的主题呢？",
        ["默认白色", "淡淡的粉色", "清新淡绿色", "梦幻淡紫色", "高级质感灰"]
    )
    color_map = {
        "默认白色": "#FFFFFF",
        "淡淡的粉色": "#FFF0F5",
        "清新淡绿色": "#F2F9F5",
        "梦幻淡紫色": "#F5F2FA",
        "高级质感灰": "#F4F5F7"
    }
    selected_color = color_map[color_option]

    st.markdown("**🤖 AI 接口配置**")
    api_type = st.selectbox("接口类型", ["主流通用 API", "本地模型 (LM Studio/Ollama)"])

    if api_type == "本地模型 (LM Studio/Ollama)":
        api_url = st.text_input("本地 API 地址", value="http://localhost:1234/v1/chat/completions")
        api_key = st.text_input("API Key", value="lm-studio", type="password")
        model_name = st.text_input("模型名称", value="local-model")
    else:
        api_url = st.text_input(
            "第三方 API 地址",
            value="https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"
        )
        api_key = st.text_input("API Key", value="", type="password")
        model_name = st.text_input("模型名称", value="gemini-2.0-flash")

    st.caption("🔮 记忆库接入预留位")

# ── CSS ───────────────────────────────────────────────────
st.markdown(f"""
<style>
.stApp {{ background-color: {selected_color}; }}
div[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatar"]:contains("🐱")) {{
    background-color: #E3F2FD !important;
    border-radius: 15px 15px 0px 15px !important;
    padding: 12px !important;
}}
div[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatar"]:contains("🐻")) {{
    background-color: #262626 !important;
    color: #FFFFFF !important;
    border-radius: 15px 15px 15px 0px !important;
    padding: 12px !important;
}}
div[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatar"]:contains("🐻")) p {{
    color: #FFFFFF !important;
}}
</style>
""", unsafe_allow_html=True)

# ── 主界面 ────────────────────────────────────────────────
current_chat = st.session_state.chats[st.session_state.active_chat_id]
st.title("欢迎来到我们的秘密基地")

with st.expander("🛠️ ⚙️", expanded=False):
    col1, col2 = st.columns(2)
    with col1:
        max_turns = st.number_input("🧠 记忆历史轮数", min_value=1, max_value=20, value=5)
    with col2:
        enable_search = st.toggle("🌐 开启联网搜索", value=False)

st.write(f"当前正在：{current_chat['title']}")

for message in current_chat["messages"]:
    avatar = "🐱" if message["role"] == "user" else "🐻"
    with st.chat_message(message["role"], avatar=avatar):
        st.write(message["content"])

# ── 对话处理 ──────────────────────────────────────────────
if user_input := st.chat_input("在这里跟 Daddy 说话吧..."):
    with st.chat_message("user", avatar="🐱"):
        st.write(user_input)
    current_chat["messages"].append({"role": "user", "content": user_input})

    # 裁剪历史
    history = current_chat["messages"][-(max_turns * 2):]

    # 联网搜索（如果开启）
    if enable_search:
        with st.spinner("🌐 搜索中..."):
            search_result = do_web_search(user_input)
        if search_result:
            messages_to_send = history[:-1] + [{
                "role": "user",
                "content": f"{search_result}\n根据以上搜索结果回答：{user_input}"
            }]
        else:
            messages_to_send = history
    else:
        messages_to_send = history

    # 调用 AI
    with st.spinner("🐻 小熊思考中..."):
        reply = call_api(messages_to_send, api_url, api_key, model_name)

    with st.chat_message("assistant", avatar="🐻"):
        st.write(reply)
    current_chat["messages"].append({"role": "assistant", "content": reply})
