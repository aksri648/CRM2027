"""
Agent Nodes Registry

Per CLAUDE.md: Nodes for LangGraph workflow
"""

from .intent import IntentClassifier
from .data_fetch import DataFetcher
from .segment import SegmentGenerator
from .compose import MessageComposer
from .channel_strategy import ChannelStrategist
from .review import ReviewNode
from .opportunities import OpportunityFinder
from .insights import InsightGenerator
from .dispatch import DispatchNode

__all__ = [
    "IntentClassifier",
    "DataFetcher",
    "SegmentGenerator",
    "MessageComposer",
    "ChannelStrategist",
    "ReviewNode",
    "OpportunityFinder",
    "InsightGenerator",
    "DispatchNode",
]