from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.types import RetryPolicy

from requests.exceptions import HTTPError
from loguru import logger

class EmptyState(TypedDict):
    pass

def node_a(state: EmptyState) -> EmptyState:
    logger.info(f"node a 运行")
    raise HTTPError("网络连接超时...")

builder = StateGraph(state_schema=EmptyState)

'''
RetryPolicy(max_attempts=3) 表示最大尝试次数，包括首次执行。

RetryPolicy(initial_interval=0.5)   表示首次失败后，等待 0.5s 再进行第一次重试。

RetryPolicy(
    initial_interval=0.5,
    backoff_factor=2.0
) 表示每次重试间隔为上一次间隔的 2 倍。0.5s -> 1.0s -> 2.0s -> 4.0s ...

RetryPolicy(
    initial_interval=1,
    backoff_factor=2,
    max_interval=5
) 等待时间大致为：1s -> 2s -> 4s -> 5s -> 5s ...

jitter=False    表示不添加随机延迟，每次重试间隔相同。
jitter=True 表示为重试间隔添加随机抖动（添加随机数，可正可负）。
在并发场景中，如果大量任务同时失败，并且按照固定间隔同时重试，可能导致服务在某个时间点被大量请求打爆。

retry_on 用于设置哪些异常需要触发重试。
它支持三种写法：
RetryPolicy(retry_on=HTTPError)     单个异常
RetryPolicy(
    retry_on=(HTTPError, ConnectionError)
)     多个异常
RetryPolicy(retry_on=Exception)     所有异常
写法三：自定义判断函数
def should_retry(exc: Exception) -> bool:
    return isinstance(exc, HTTPError)
RetryPolicy(retry_on=should_retry)

一般不会触发重试的错误类型：
    ValueError,
    TypeError,
    ArithmeticError,
    ImportError,
    LookupError,
    NameError,
    SyntaxError,
    RuntimeError,
    ReferenceError,
    StopIteration,
    StopAsyncIteration,
    OSError,

'''
builder.add_node(
    "node_a",
    node_a,
    retry_policy=RetryPolicy(
        max_attempts=3,
        jitter=False
    )
)
builder.add_edge(START, "node_a")
builder.add_edge("node_a", END)

graph = builder.compile()

try:
    graph.invoke({})
except HTTPError as e:
    logger.info("重试次数耗尽: {}", e)

from IPython.display import display
display(graph)