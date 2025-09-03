import streamlit as st
from utilities.a2a import agent_connector, agent_discovery
from utilities.mcp import mcp_discovery
from a2a.client import A2ACardResolver
import httpx
import asyncio
from config import config

    
async def retrieve_host_card(host_agent_url: str) -> agent_connector.AgentConnector:
    
    # C: the first step is to find host_agent_card
    host_agent_card = None
    async with httpx.AsyncClient(timeout=300) as httpx_client:
        try:
            resolver = A2ACardResolver(base_url=host_agent_url, httpx_client=httpx_client)
            host_agent_card  = await resolver.get_agent_card()
            if host_agent_card:
                print(f"🌳🌳🌳 Discovered agent: {host_agent_card.name} at {host_agent_url}")
            else:
                print(f"⭐️⭐️⭐️ No AgentCard found at {host_agent_url}")
        except Exception as e:
            print(f"💥💥💥 Error retrieving AgentCard from {host_agent_url}: {e}")
    
    # C: connect to the host agent
    return host_agent_card

async def retrieve_all_tools():
    mcp_servers = []
    agents = []
    
    mcp_discover = mcp_discovery.MCPDiscovery()
    mcps = mcp_discover.list_all_servers()
    for server_name, server_info in mcps.items():
        mcp_servers.append({"name": server_name, "url": server_info['args'][0], "status": "✅ Running"})
        
    agent_discover = agent_discovery.AgentDiscovery()
    agent_cards = await agent_discover.list_agent_cards()
    for card in agent_cards:
        agents.append({"name": card.name, "description": card.description, "status": "🟢 Connected"})
    
    return mcp_servers, agents
        

mcp_servers, agents = asyncio.run(retrieve_all_tools())

st.title("💬 Simple Agentic AI Chat")
for server in mcp_servers:
    col1, col2, col3 = st.columns([2, 4, 2])  # column widths
    col1.write(f"**{server['name']}**")
    col2.write(server["url"])
    col3.write(server["status"])

for agent in agents:
    col1, col2, col3 = st.columns([2, 4, 2])
    col1.write(f"**{agent['name']}**")
    col2.write(agent["description"][:100] + "...")
    col3.write(agent["status"])
    
# Keep chat history in session_state
if "messages" not in st.session_state:
    st.session_state.messages = []

card = asyncio.run(retrieve_host_card(f"http://localhost:{config.HOST_AGENT_PORT}"))
host_connector = agent_connector.AgentConnector(card)

# Reset button
if st.button("Reset Chat", type="primary", use_container_width=True):
    if st.session_state:
        st.session_state.messages.clear()  # clears everything in session state

    
# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"], unsafe_allow_html=True)

# Chat input
if prompt := st.chat_input("Type your message...", key="prompt"):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)


    # bot reply
    response = asyncio.run(host_connector.send_task(prompt))
    print("Response 🚀🚀🚀 =>", response)
    st.session_state.messages.append({"role": "assistant", "content": response})
        
    with st.chat_message("assistant"):
        st.markdown(response)
    
            