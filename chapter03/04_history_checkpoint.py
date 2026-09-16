"""
配置检查点存储器后，会把同一个 thread_id 下的执行过程保存为一组检查点。
graph.get_state_history(config)：查看指定会话的完整历史检查点。
graph.get_state(config)：查看指定会话的最新检查点

get_state_history() 返回的是一个历史检查点迭代器。将其转换为列表后，可以看到一组 StateSnapshot 对象。

StateSnapshot
├── values          → 当前完整 State
├── next            → 元组，该检查点"待执行"的节点名
├── config
│   └── configurable
│       ├── thread_id      → 会话 ID
│       └── checkpoint_id  → 检查点唯一 ID
├── metadata
│   ├── source      → input / loop / update
│   └── step        → -1, 0, 1, 2...
├── created_at      → 时间
├── parent_config   → 上一个检查点
├── tasks[]         → 本步执行的任务
│   ├── name        → 节点名
│   └── result      → 节点返回值
└── interrupts[]    → 中断信息


检查点 = 一张任务卡
┌─────────────────────────────────────┐
│ values: 进来时的状态                 │
│                                     │
│ next:   【计划】本步要跑谁            │
│                                     │
│ tasks:  【执行】谁跑完了 + 返回值     │
│   ├─ node_poem → {poem: ...}        │
│   └─ node_joke → {joke: ...}        │
└─────────────────────────────────────┘
        ↓
   合并 tasks.result 到 values
        ↓
   成为下一个检查点的 values

也就是
checkpoint["id"] 会在保存主检查点前由 create_checkpoint() 推进为新的 ID
然后用这个 ID 写入主检查点（假设当前超步为 S1）。下一轮（超步为 S2）计算循环中，任务执行完毕后的中间结果会用相同的 ID 写入。
因此，下一轮（超步为 S2）任务的计算结果绑定到了“当前超步（超步为 S1）的主检查点”。
"""


from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langchain.messages import HumanMessage
from langchain_deepseek import ChatDeepSeek

from loguru import logger
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
    poem: str
    joke: str
    final_output: str

class InputState(TypedDict):
    topic: str

class OutputState(TypedDict):
    final_output: str

def node_poem(state: InputState) -> OverAllState:
    logger.info(f"node_poem 已执行")
    topic = state["topic"]
    poem = model.invoke([HumanMessage(f"写一首关于 {topic} 的七言绝句")]).content

    return {
        "poem": poem
    }

def node_joke(state: InputState) -> OverAllState:
    logger.info(f"node_joke 已执行")
    topic = state["topic"]
    joke = model.invoke([HumanMessage(f"写一个关于 {topic} 的笑话")]).content

    return {
        "joke": joke
    }

def node_output(state: OverAllState) -> OutputState:
    logger.info("node_output 已执行")
    topic = state["topic"]
    poem = state["poem"]
    joke = state["joke"]
    final_output = f"关于 {topic} 的七言绝句：\n{poem}\n笑话：\n{joke}"

    return {
        "final_output": final_output
    }

builder = StateGraph(state_schema=OverAllState, input_schema=InputState, output_schema=OutputState)
builder.add_node("node_poem", node_poem)
builder.add_node("node_joke", node_joke)
builder.add_node("node_output", node_output)
builder.add_edge(START, "node_poem")
builder.add_edge(START, "node_joke")
builder.add_edge("node_poem", "node_output")
builder.add_edge("node_joke", "node_output")
builder.add_edge("node_output", END)

checkpointer = InMemorySaver()
config = {"configurable": {"thread_id": "123"}}
graph = builder.compile(checkpointer=checkpointer)
res = graph.invoke({"topic": "猫咪"}, config=config)

print('=' * 30, '-> 运行结果 <-', '=' * 30)
print("res: {}", res)

print('=' * 30, '-> 历史检查点列表 <-', '=' * 30)
history_checkpoints = list(graph.get_state_history(config=config))
print(history_checkpoints)

print('=' * 30, '-> 根据 checkpoint_id 获取历史检查点 <-', '=' * 30)
checkpoint_id = history_checkpoints[3].config["configurable"]["checkpoint_id"]
print(f"当前checkpoint_id: {checkpoint_id}")
target_config = {
    "configurable": {
        "thread_id": config["configurable"]["thread_id"],
        "checkpoint_id": checkpoint_id
    }
}
snapshot = graph.get_state(config=target_config)
print(snapshot)


"""
# 获取最新检查点
latest_checkpoint = graph.get_state(config=config)
print(latest_checkpoint)

# 获取全部检查点
history_checkpoints = list(graph.get_state_history(config=config))
print(history_checkpoints)

# 如果希望查看某个历史检查点，可以在 configurable 中额外传入 checkpoint_id：1f1b122d-df44-67b7-8001-2d07ff6c6e6a
target_config = {
    "configurable": {
        "thread_id": "123",
        "checkpoint_id": "某个历史 checkpoint_id"
    }
}

snapshot = graph.get_state(config=target_config)
print(snapshot)
"""


# 6 图可视化
from IPython.display import Image
from openpyxl.drawing.image import PILImage
png_bytes = graph.get_graph().draw_mermaid_png()
png = Image(data=png_bytes)

with open("graph.png", "wb") as f:
    f.write(png_bytes)

PILImage.open("graph.png").show()