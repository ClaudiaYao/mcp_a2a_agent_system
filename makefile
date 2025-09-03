run-all:
	uv run python3 -m mcp_server.math_mcp_server & echo $$! > math_server.pid
	sleep 3
	uv run python3 -m agents.post_design_agent & echo $$! > post_design_agent.pid
	sleep 3
	uv run python3 -m agents.host_agent & echo $$! > host_agent.pid
	sleep 3
	streamlit run app/chat_ai.py & echo $$! > chat_ui.pid

stop-all:
	-kill $$(cat math_server.pid) || true
	-kill $$(cat post_design_agent.pid) || true
	-kill $$(cat host_agent.pid) || true
	-kill $$(cat chat_ui.pid) || true
	rm -f *.pid


kill-all:
	-pkill -f "python3 -m mcp_server.math_mcp_server"
	-pkill -f "python3 -m agents.post_design_agent"
	-pkill -f "python3 -m agents.host_agent"
	-pkill -f "streamlit run app/chat_ai.py"

