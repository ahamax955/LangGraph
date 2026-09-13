from loguru import logger
from typing import TypedDict, Literal, Sequence
from langgraph.graph import StateGraph, START, END
from langchain.messages import HumanMessage
from langgraph.types import Send, Command
from langchain_deepseek import ChatDeepSeek
from dotenv import load_dotenv

load_dotenv(override=True)
CONTENT_TYPE = ["poem", "joke", "ci_poem"]
model = ChatDeepSeek(
    model="deepseek-v4-flash",
    extra_body={
        "thinking": {
            "type": "disabled"
        }
    }
)

# 1 定义状态
class OverAllState(TypedDict):
    topic: str
    content_type: Literal["poem", "joke"]
    content_Chinese: str
    poem: str
    joke: str


# 2 定义路由节点
def router(state: OverAllState) -> Command[Literal["poem_node", "joke_node", END]]:
    if state["content_type"] == "poem":
        return Command(
            update={
                "content_Chinese": "一首诗"
            },
            goto="poem_node"
        )
    elif state["content_type"] == "joke":
        return Command(
            update={
                "content_Chinese": "一个笑话"
            },
            goto="joke_node"
        )
    else:
        return Command(
            goto=END
        )

# 3 添加节点
def poem_node(state: OverAllState) -> OverAllState:
    poem = model.invoke(
        [
            HumanMessage(f"写一首关于 {state['topic']} 的 {state['content_Chinese']}")
        ]
    ).content
    return {
        "poem": poem
    }

def joke_node(state: OverAllState) -> OverAllState:
    joke = model.invoke(
        [
            HumanMessage(f"写一个关于 {state['topic']} 的 {state['content_Chinese']}")
        ]
    ).content
    return {
        "joke": joke
    }

# 3. 构建图
builder = StateGraph(state_schema=OverAllState)
builder.add_node("router",router)
builder.add_node("poem_node",poem_node)
builder.add_node("joke_node",joke_node)

builder.add_edge(START,"router")
builder.add_edge("poem_node",END)
builder.add_edge("joke_node",END)

graph = builder.compile()

res1 = graph.invoke({"topic": "莲花","content_type": "poem"})
print(res1)
print("="*50)
res2 = graph.invoke({"topic": "猫咪","content_type": "joke"})
print(res2)
res3 = graph.invoke({"topic": "猫咪","content_type": "xxx"})
print(res3)


# 6 图可视化
from IPython.display import Image
from openpyxl.drawing.image import PILImage
png_bytes = graph.get_graph().draw_mermaid_png()
png = Image(data=png_bytes)

with open("graph.png", "wb") as f:
    f.write(png_bytes)

PILImage.open("graph.png").show()







