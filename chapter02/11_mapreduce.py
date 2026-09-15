from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.types import Send
from _collections_abc import Sequence
from operator import add

from loguru import logger

class OverAllState(TypedDict):
    input_value: list[str]
    entries: Annotated[list[tuple[str,str]], add]
    word_count: dict[str,int]

def router_map(state:OverAllState) -> Sequence[Send]:
    input_values = state["input_value"]

    tasks = []
    for input_value in input_values:
        tasks.append(
            Send(
                "mapper_node",
                {"input_value": input_value}
            )
        )
    return tasks

class MaperInputState(TypedDict):
    input_value: str

def mapper_node(state:MaperInputState) -> OverAllState:
    input_value = state["input_value"]
    words = input_value.split(" ")
    entries = []
    for word in words:
        entries.append((word, 1))

    return {
        "entries": entries
    }

def reducer_node(state:OverAllState) -> OverAllState:
    entries = state["entries"]
    logger.info(f"entries: {entries}")

    shuffle_dict = {}

    for k,v in entries:
        if k not in shuffle_dict:
            shuffle_dict[k] = [v]
        else:
            shuffle_dict[k].append(v)

    logger.info("reducer shuffle entries: {}", shuffle_dict)
    reduce_dict = {}
    for k,v in shuffle_dict.items():
        reduce_dict[k] = sum(v)

    return {
        "word_count": reduce_dict
    }

builder = StateGraph(state_schema=OverAllState)
builder.add_node("mapper_node", mapper_node)
builder.add_node("reducer_node", reducer_node)
builder.add_conditional_edges(START, router_map, path_map=["mapper_node"])
builder.add_edge("mapper_node", "reducer_node")
builder.add_edge("reducer_node", END)

graph = builder.compile()

word_count = graph.invoke(
    {
        "input_value": [
            "hello world",
            "hello Atguigu",
            "hello LLM"
        ]
    }
)

print(word_count)

# 6 图可视化
from IPython.display import Image
from openpyxl.drawing.image import PILImage
png_bytes = graph.get_graph().draw_mermaid_png()
png = Image(data=png_bytes)

with open("graph.png", "wb") as f:
    f.write(png_bytes)

PILImage.open("graph.png").show()




    