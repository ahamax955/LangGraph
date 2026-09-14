from loguru import logger
from typing import TypedDict, Literal, Sequence
from langgraph.graph import StateGraph, START, END
from langchain.messages import HumanMessage
from langgraph.types import Send
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
    poem: str
    ci_poem: str
    joke: str

# 私有状态
class workerState(TypedDict):
    content_type: Literal["poem", "joke", "ci_poem"]
    prompt: str

class inputState(TypedDict):
    topic: str

class outputState(TypedDict):
    poem: str
    ci_poem: str
    joke: str

# 2 定义节点
def worker_node(state: workerState) -> outputState:
    content_type = state["content_type"]
    prompt = state["prompt"]
    content = model.invoke(
        [
            HumanMessage(prompt)
        ]
    ).content
    return {
        content_type: content
    }

# 3 定义动态分支的路由
def router(state: inputState) -> Sequence[Send]:
    router_prompt = "写一个关于 {} 的 {}"
    english2Chinese = {
        "poem": "七言绝句",
        "joke": "笑话",
        "ci_poem": "中文词"
    }
    topic = state["topic"]
    return [
        Send(
            "worker_node",
            {
                "content_type": content_type,
                "prompt": router_prompt.format(topic, english2Chinese[content_type])
            }
        )
        for content_type in CONTENT_TYPE
    ]


#4. 构建图
builder = StateGraph(state_schema=OverAllState,input_schema=inputState,output_schema=outputState)

builder.add_node("worker_node", worker_node)

builder.add_conditional_edges(
    START,
    router,
    path_map=["worker_node"],
    )

builder.add_edge("worker_node",END)

graph = builder.compile()
res = graph.invoke({"topic": "莲花"})
print(res)


# 6 图可视化
from IPython.display import Image
from openpyxl.drawing.image import PILImage
png_bytes = graph.get_graph().draw_mermaid_png()
png = Image(data=png_bytes)

with open("graph.png", "wb") as f:
    f.write(png_bytes)

PILImage.open("graph.png").show()







