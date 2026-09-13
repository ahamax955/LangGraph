from langgraph.graph import StateGraph,START,END
from typing import TypedDict, Annotated
from operator import add



# 1 定义状态
class OverAllState(TypedDict):
    # 日志类型还是list[str]  更新的方式不是覆盖而是追加
    logs: Annotated[list[str], add]
    cur_id: str

# 2 定义节点
def node_1(state: OverAllState) -> OverAllState:
    pre_id = state["cur_id"]
    return {
        "logs": ["node1 运行完毕。"],
        "cur_id": pre_id+", node_1",
    }

def node_2(state: OverAllState) -> OverAllState:
    pre_id = state["cur_id"]
    return {
        "logs": ["node2 运行完毕。"],
        "cur_id": pre_id+", node_2",
    }

# 3 定义边
#3.1创建图，获取建造者
builder = StateGraph(state_schema=OverAllState)

builder.add_edge(START, "node_1")
builder.add_sequence([node_1, node_2])
# builder.add_edge("node_2", END)


# 4 编译图
graph = builder.compile()

# 5 运行图
result = graph.invoke({"cur_id": "start"})
print(result)


# 6 图可视化
from IPython.display import Image
from openpyxl.drawing.image import PILImage
png_bytes = graph.get_graph().draw_mermaid_png()
png = Image(data=png_bytes)

with open("graph.png", "wb") as f:
    f.write(png_bytes)

PILImage.open("graph.png").show()