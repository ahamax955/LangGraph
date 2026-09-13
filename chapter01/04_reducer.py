# left: 从开始位置合并到当前节点的位置的值
# right: 当前节点的值
# 返回值是合并后的值
def my_reducer(left: list[str], right: list[str]) -> list[str]:
    return left + right

# 1. node1 运行之后的值
left = ["start", "node1 运行完毕"]
right = ["start","node2 运行完毕"]

merge = my_reducer(left, right)
print(merge)