from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import MessagesState
from langchain_deepseek import ChatDeepSeek
from dotenv import load_dotenv
load_dotenv(override=True)

model = ChatDeepSeek(
    model="deepseek-v4-flash",
    extra_body={
        "thinking": {
            "type": "disabled"
        }
    }
)

# 定义状态
class OverAllState(MessagesState):
    username: str
    output: str

# 定义节点
def node_a(state: OverAllState) -> OverAllState:
    return {
        "messages": [HumanMessage("你好，我是"+ state["username"])]
    }


def llm_node(state: OverAllState) -> OverAllState:
    res = model.invoke(state["messages"])
    return {
        "messages": [res],
        "output": res.content
    }

builder = StateGraph(state_schema=OverAllState)
builder.add_node("node_a", node_a)
builder.add_node("llm_node", llm_node)

builder.add_edge(START, "node_a")
builder.add_edge("node_a", "llm_node")
builder.add_edge("llm_node", END)

graph = builder.compile()
result = graph.invoke({"username": "老王"})
print(result)

