"""
In-Memory Storage
State: 用户定义的状态类，用于节点间的信息传递，LangGraph 会将 State 转换为底层 Channel；运行时真正负责节点间通信的是 Channel
Channel: 节点从 Channel 读数据、向 Channel 写更新
checkpointer: 用于检查点的存储和恢复
checkpointMetadata: 与 Checkpoint 关联的元数据，如超步编号 step、父检查点 ID parents 等。
checkpointer: 检查点存储器
thread：不是OS中的线程，是指 LangGraph 中一条逻辑上的、可持久化的执行线，也可以理解为会话。
thread_id: 线程 ID
checkpoint_ns: 检查点命名空间，用于隔离不同线程之间的检查点存储
checkpoint_id: 检查点 ID， 可以定位到某个具体的检查点状态
StateSnapshot: 状态快照，用于存储节点状态的快照

持久化机制负责保存执行状态
可恢复执行利用这些状态快照，从任意点恢复执行
"""

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import MessagesState
from langgraph.checkpoint.memory import InMemorySaver
from langchain_deepseek import ChatDeepSeek
from langchain.messages import HumanMessage

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

class OverAllState(MessagesState):
    output: str

def llm_node(state: OverAllState) -> OverAllState:
    messages = state["messages"]
    res = model.invoke(messages)
    return {
        "messages": [res]
    }

def output_node(state: OverAllState) -> OverAllState:
    return {
        "output": state["messages"][-1].content
    }

builder = StateGraph(state_schema=OverAllState)
builder.add_node("llm_node", llm_node)
builder.add_node("output_node", output_node)
builder.add_edge(START, "llm_node")
builder.add_edge("llm_node", "output_node")
builder.add_edge("output_node", END)

# 定义并在编译时传递 Checkpointer
checkpointer = InMemorySaver()
graph = builder.compile(checkpointer=checkpointer)

# 定义配置对象
config = {"configurable": {"thread_id": "chapter_6_6-2-2"}}
# 调用时传递
graph.invoke({"messages": [HumanMessage("你好，我是老王")]}, config=config)
graph.invoke({"messages": [HumanMessage("从现在开始，你是小王")]}, config=config)
res = graph.invoke({"messages": [HumanMessage("我是谁？你是谁？")]}, config=config)
print(res["output"])

print('=' * 30, '-> 完整消息列表 <-', '=' * 30)
for msg in res["messages"]:
    msg.pretty_print()