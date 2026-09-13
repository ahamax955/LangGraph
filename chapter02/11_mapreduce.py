from operator import add

from loguru import logger
from typing import TypedDict, Literal, Sequence, Annotated
from langgraph.graph import StateGraph, START, END
from langchain.messages import HumanMessage
from langgraph.types import Send, Command
from langchain_deepseek import ChatDeepSeek
from dotenv import load_dotenv

class OverAllState(TypedDict):
    input_value: list[str]
    entries: Annotated[list[tuple[str,str]], add]
    