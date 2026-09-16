from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import MessagesState
from langgraph.checkpoint.postgres import PostgresSaver
from langchain_deepseek import ChatDeepSeek
from langchain.messages import HumanMessage


"""
数据库在服务器端
./pg.sh status    # 看状态
./pg.sh psql      # 进数据库
./pg.sh start     # 每次要用
链接数据库： 
DB_URL = "postgresql://postgres:postgres@81.70.31.254:5432/langgraph"


执行的时候，durability="async" # sync / exit代表不同的缓存模式
res=graph.invoke(
    {"messages": [HumanMessage("你好")]},
    config=config,
    durability="async" # sync / exit
)
不同缓存模式的写入时机区别：
exit：以整个图为单位，只有当整个图 正常结束、异常退出、被中断
sync：以每个节点为单位，每个节点执行完成后，就会写入数据库
async：默认模式，以每个节点为单位，每个节点执行完成后，就会写入数据库，但是不会阻塞主程序的执行
"""

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
DB_URL = "postgresql://postgres:postgres@81.70.31.254:5432/langgraph"
with PostgresSaver.from_conn_string(DB_URL) as checkpointer:
    # 示例中为了方便演示直接调用 setup()
    # 实际项目中通常建议把数据库初始化/迁移作为独立步骤处理
    checkpointer.setup()
    graph = builder.compile(checkpointer=checkpointer)

    # 定义配置对象
    config = {"configurable": {"thread_id": "chapter_6_6.2.4"}}
    # 调用时传递
    res = graph.invoke({"messages": [HumanMessage("我是谁，要了什么")]}, config=config, durability="async")
    print(res["output"])

    print('=' * 30, '-> 完整消息列表 <-', '=' * 30)
    for msg in res["messages"]:
        msg.pretty_print()