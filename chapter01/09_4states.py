from typing import TypedDict
from langgraph.graph import StateGraph, START, END

# 输入状态
class InputState(TypedDict):
    username: str

# 输出状态
class OutputState(TypedDict):
    graph_output: str

# 全局状态
class OverAllState(TypedDict):
    username: str
    graph_output: str
    nikename: str

# 私有状态
class PrivateState(TypedDict):
    greeting: str

# 第一个节点对接START => InputState
def node_1(state: InputState) -> OverAllState:
    # 向全局添加username
    return {
        "nikename": "Dear"+state["username"],
    }


def node_2(state: OverAllState) -> PrivateState:
    # 向全局添加username
    return {
        "greeting": "Hello, "+state["nikename"],
    }

def node_3(state: PrivateState) -> OutputState:
    return {
        "graph_output": state["greeting"],
    }

# 构建
builder = StateGraph(state_schema=OverAllState, input_schema=InputState, output_schema=OutputState)

# 添加节点的时候，加载私有状态
builder.add_node("node_1", node_1)
builder.add_node("node_2", node_2)
builder.add_node("node_3", node_3)

# 添加边
builder.add_edge(START, "node_1")
builder.add_edge("node_1", "node_2")
builder.add_edge("node_2", "node_3")
builder.add_edge("node_3", END)

graph = builder.compile()

result = graph.invoke({"username": "zhangsan"})

print(result)

