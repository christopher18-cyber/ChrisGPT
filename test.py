from langchain_core.messages import HumanMessage

from agent import get_agent

agent = get_agent("qwen/qwen3.8-27b")

config = {
    "configurable": {
        "thread_id":"test_thread_id"
    }
}

for message_chunk, metadata in agent.stream(
    {"messages":[HumanMessage(content="Tell me today's news of AI")]},
    config=config,
    stream_mode="messages"
):
    if message_chunk.content:
        print(message_chunk.content, end=" ", flush=True)