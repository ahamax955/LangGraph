from langchain.messages import SystemMessage, HumanMessage, AIMessage
from langgraph.graph.message import add_messages

left = [
    SystemMessage(content="你是一个专业的翻译", id = "1"),
    HumanMessage(content="你好", id = "2"),
    AIMessage(content="你好，我是专业的翻译", id = "3")
]

right = [
    SystemMessage(content="你是一个专业的厨师", id="5"),
    HumanMessage(content="你是老王", id="2"),
    AIMessage(content="你好，我是专业的翻译", id="3"),
    SystemMessage(content="Sys最终", id = "2"),
    HumanMessage(content="Human最终", id = "3"),
    AIMessage(content="AI最终", id = "1")
]

# 结果只会根据id进行覆盖，即使是不同的prompt
merged = add_messages(left, right)
print(merged)