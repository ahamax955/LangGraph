from loguru import logger
from typing import TypedDict, Literal, Sequence
from langgraph.graph import StateGraph, START, END
from langchain.messages import HumanMessage
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

class OverAllState(TypedDict):
    topic: str
    content_type: str
    poem: str
    joke: str
    ci: str

def node_a(state: OverAllState) -> OverAllState:
    poem = model.invoke([HumanMessage(f"写一首关于 {state['topic']} 的七言绝句")]).content

    return {
        "poem": poem
    }

def node_b(state: OverAllState) -> OverAllState:
    joke = model.invoke([HumanMessage(f"写一个关于 {state['topic']} 的笑话")]).content

    return {
        "joke": joke
    }


def node_defer(state: OverAllState) -> OverAllState:
    logger.info(
        f"任务节点全部完毕，诗 {'已生成' if state.get('poem') else '未生成'}，"
        f"笑话 {'已生成' if state.get('joke') else '未生成'}"
    )
    return {}

def router(state: OverAllState) -> Sequence[Literal["poem", "joke", "poem_ci"]]:
    if "诗" in state["content_type"]:
        return ["poem", "poem_ci"]
    return ["joke", "poem_ci"]

builder = StateGraph(state_schema=OverAllState)
builder.add_node("node_a", node_a)
builder.add_node("node_b", node_b)
builder.add_node("node_defer", node_defer, defer=True)

builder.add_edge(START, "node_a")
builder.add_edge(START, "node_b")
builder.add_edge(START, "node_defer")
builder.add_edge("node_a", END)
builder.add_edge("node_b", END)
builder.add_edge("node_defer", END)

graph = builder.compile()

res = graph.invoke({"topic" : "小猫"})
print(res)

# 6 图可视化
from IPython.display import Image
from openpyxl.drawing.image import PILImage
png_bytes = graph.get_graph().draw_mermaid_png()
png = Image(data=png_bytes)

with open("graph.png", "wb") as f:
    f.write(png_bytes)

PILImage.open("graph.png").show()