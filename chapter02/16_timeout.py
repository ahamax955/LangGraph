"""
from langgraph.types import TimeoutPolicy

builder.add_node(
    "call_model",
    call_model,
    timeout=TimeoutPolicy(run_timeout=60)
)

call_model 节点单次执行最多运行 60 秒。
如果超过 60 秒仍未完成，则触发超时。
超时后会抛出 NodeTimeoutError。
该异常会交给 RetryPolicy 判断是否需要重试。
如果重试次数耗尽，才会进入错误处理逻辑。

"""


"""
错误处理
错误处理机制用于在节点最终失败后，执行兜底逻辑。

builder.add_node(
    "call_api",
    call_api,
    retry_policy=RetryPolicy(max_attempts=3),
    error_handler=handle_api_error
)

call_api 执行失败。
RetryPolicy 判断是否重试。
最多尝试 3 次。
3 次仍然失败后，调用 handle_api_error。
handle_api_error 可以返回状态更新，也可以通过 Command 路由到其他节点。

API 调用失败后返回兜底结果。
远程服务失败后切换到备用服务。
多步骤业务流程中执行补偿逻辑。
不希望整个图因为单个节点失败而直接终止。
"""