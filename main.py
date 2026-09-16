from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.postgres import PostgresSaver

DB_URI = "postgresql://postgres:postgres@81.70.31.254:5432/langgraph"

class State(TypedDict):
    messages: list

def chatbot(state: State):
    return {"messages": state["messages"] + ["AI回复"]}

builder = StateGraph(State)
builder.add_node("chatbot", chatbot)
builder.add_edge(START, "chatbot")
builder.add_edge("chatbot", END)

with PostgresSaver.from_conn_string(DB_URI) as checkpointer:
    checkpointer.setup()  # 幂等，第一次建表
    graph = builder.compile(checkpointer=checkpointer)

    config = {"configurable": {"thread_id": "user-001"}}
    result = graph.invoke({"messages": ["我是老王"]}, config=config)
    print(result)