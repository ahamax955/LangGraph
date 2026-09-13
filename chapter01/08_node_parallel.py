from time import sleep
from typing import TypedDict, Annotated
from operator import add
from langgraph.constants import START, END
from langgraph.graph import StateGraph
from langgraph.types import Overwrite
from openpyxl.drawing.image import PILImage


# 1 定义状态，追加合并
class OverAllState(TypedDict):
    logs: Annotated[list[str], add]
    # 如果出现并行节点，同时更新状态，往下游传递节点的时候，必须要有reducer函数
    cur_id: Annotated[str, add]

# 2 定义节点
def node_1(state: OverAllState) -> OverAllState:
    for k,v in state.items():
        print(k, v)
    return {
        "logs": ["node1运行完毕"],
        "cur_id": "node1<UNK>",
    }

def node_2(state: OverAllState) -> OverAllState:
    for k,v in state.items():
        print(k, v)
    return {
        "logs": ["node2运行完毕"],
        "cur_id": "node2<UNK>",
    }

def node_3(state: OverAllState) -> OverAllState:
    sleep(1)
    for k,v in state.items():
        print(k, v)
    return {
        "logs": ["node3运行完毕"],
        "cur_id": "node3<UNK>",
    }

def node_4(state: OverAllState) -> OverAllState:
    sleep(2)
    for k,v in state.items():
        print(k, v)
    return {
        "logs": Overwrite(["node4运行完毕"]),
        "cur_id": "node4<UNK>",
    }

builder = StateGraph(state_schema=OverAllState)
builder.add_node("node_1", node_1)
builder.add_node("node_2", node_2)
builder.add_node("node_3", node_3)
builder.add_node("node_4", node_4)
builder.add_edge(START, "node_1")
builder.add_edge("node_1", "node_2")
builder.add_edge("node_1", "node_3")
builder.add_edge("node_2", "node_4")
builder.add_edge("node_3", "node_4")
builder.add_edge("node_4", END)

graph = builder.compile()
result = graph.invoke({"cur_id": "start"})
print(result)


# 6 图可视化
from IPython.display import Image
png_bytes = graph.get_graph().draw_mermaid_png()
png = Image(data=png_bytes)

with open("graph.png", "wb") as f:
    f.write(png_bytes)

PILImage.open("graph.png").show()