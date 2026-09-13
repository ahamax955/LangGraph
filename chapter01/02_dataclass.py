from langgraph.graph import StateGraph,START,END
from typing import Annotated
from dataclasses import dataclass
from operator import add

from openpyxl.drawing.image import PILImage


# 1 定义状态
@dataclass
class OverAllState:
    # 日志类型还是list[str]  更新的方式不是覆盖而是追加
    logs: Annotated[list[str], add]
    cur_id: str

# 2 定义节点
def node_1(state: OverAllState) -> OverAllState:
    pre_id = state.cur_id
    return OverAllState(logs=state.logs+["node1 运行完毕"], cur_id=pre_id+",node1")

def node_2(state: OverAllState) -> OverAllState:
    pre_id = state.cur_id
    return {
        "logs": ["node2 运行完毕。"],
        "cur_id": pre_id+", node_2"
    }

# 3 定义边
#3.1创建图，获取建造者
builder = StateGraph(state_schema=OverAllState)
#3.2添加节点
builder.add_node(node_1)
builder.add_node(node_2)
#3.3添加边
builder.add_edge(START, "node_1")
builder.add_edge("node_1", "node_2")
builder.add_edge("node_2", END)

# 4 编译图
graph = builder.compile()

# 5 运行图
result = graph.invoke({"cur_id": "start"})
print(result)


# 6 图可视化
from IPython.display import Image
png_bytes = graph.get_graph().draw_mermaid_png()
png = Image(data=png_bytes)

with open("graph.png", "wb") as f:
    f.write(png_bytes)

PILImage.open("graph.png").show()