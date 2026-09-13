from typing import TypedDict, Annotated
from operator import add
from langgraph.constants import START, END
from langgraph.graph import StateGraph


# 1 定义状态
class OverAllState(TypedDict):
    logs: Annotated[list[str], add]
    cur_id: str

# 2 定义节点
def node_1(state: OverAllState) -> OverAllState:
    for k,v in state.items():
        print(k, v)
    return {
        "logs": ["node1运行完毕"]
    }

builder = StateGraph(state_schema=OverAllState)
builder.add_node("node_1", node_1)
builder.add_edge(START, "node_1")
builder.add_edge("node_1", END)

graph = builder.compile()
result = graph.invoke({"cur_id": "begin"})
print(result)