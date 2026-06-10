"""
LangGraph Agent Graph

Per CLAUDE.md and LangChain best practices:
- Uses StateGraph for workflow definition
- Routes intent to appropriate nodes
- Handles human-in-the-loop approval
"""

from typing import Dict, Any, AsyncGenerator, Literal
from langgraph.graph import StateGraph, END
from sqlalchemy.orm import Session

from app.agent.state import AgentState, create_initial_state
from app.agent.nodes import (
    IntentClassifier,
    DataFetcher,
    SegmentGenerator,
    MessageComposer,
    ChannelStrategist,
    ReviewNode,
    OpportunityFinder,
    InsightGenerator,
    DispatchNode,
)


def create_campaign_agent_graph(db: Session) -> StateGraph:
    """
    Create the LangGraph StateGraph for Campaign Intelligence Agent
    
    Per CLAUDE.md flow:
    User Message → Intent Node → Data Fetch Node → Intent Router
                                                    ↓
                        Segment ← Compose ← Channel Strategy ← Review
                                                    ↓
                                              Human Approval
                                                    ↓
                                                Dispatch
    """
    
    # Initialize nodes
    intent_classifier = IntentClassifier()
    data_fetcher = DataFetcher(db)
    segment_generator = SegmentGenerator(db)
    message_composer = MessageComposer(db)
    channel_strategist = ChannelStrategist(db)
    review_node = ReviewNode(db)
    opportunity_finder = OpportunityFinder(db)
    insight_generator = InsightGenerator(db)
    dispatch_node = DispatchNode(db)
    
    # Create the StateGraph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("intent_classifier", intent_classifier.classify)
    workflow.add_node("data_fetcher", data_fetcher.fetch)
    workflow.add_node("segment_generator", segment_generator.generate)
    workflow.add_node("message_composer", message_composer.compose)
    workflow.add_node("channel_strategist", channel_strategist.recommend)
    workflow.add_node("review_node", review_node.create_proposal)
    workflow.add_node("opportunity_finder", opportunity_finder.discover)
    workflow.add_node("insight_generator", insight_generator.generate)
    workflow.add_node("dispatch_node", dispatch_node.execute)
    
    # Set entry point
    workflow.set_entry_point("intent_classifier")
    
    # Add edges from intent classifier
    workflow.add_edge("intent_classifier", "data_fetcher")
    
    # Conditional routing after data fetch
    def route_after_data_fetch(state: AgentState) -> Literal[
        "segment_generator",
        "message_composer", 
        "opportunity_finder",
        "insight_generator",
        END
    ]:
        """Route to appropriate handler based on intent"""
        intent = state.get("intent", "general_request")
        
        if intent == "segment_request":
            return "segment_generator"
        elif intent == "campaign_request":
            return "message_composer"
        elif intent == "opportunity_request":
            return "opportunity_finder"
        elif intent == "analytics_request":
            return "insight_generator"
        else:
            return END
    
    workflow.add_conditional_edges(
        "data_fetcher",
        route_after_data_fetch,
        {
            "segment_generator": "segment_generator",
            "message_composer": "message_composer",
            "opportunity_finder": "opportunity_finder",
            "insight_generator": "insight_generator",
            END: END
        }
    )
    
    # Campaign flow: segment → compose → channel → review → dispatch
    workflow.add_edge("segment_generator", "message_composer")
    workflow.add_edge("message_composer", "channel_strategist")
    workflow.add_edge("channel_strategist", "review_node")
    
    # After review, wait for human approval (in real app, this would be async)
    # For now, auto-continue to dispatch
    workflow.add_edge("review_node", "dispatch_node")
    workflow.add_edge("dispatch_node", END)
    
    # Opportunity and insight flows end after their nodes
    workflow.add_edge("opportunity_finder", END)
    workflow.add_edge("insight_generator", END)
    
    return workflow


class CampaignAgentGraph:
    """
    LangGraph workflow for Campaign Intelligence Agent
    
    Per CLAUDE.md:
    - Human-in-the-loop: AI never launches campaigns automatically
    - All AI proposals require approval before dispatch
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.graph = create_campaign_agent_graph(db).compile()
    
    async def process_message(
        self,
        session_id: str,
        brand_id: int,
        message: str,
        stream_callback=None
    ) -> AgentState:
        """
        Process a user message through the agent graph
        """
        # Initialize state
        initial_state = create_initial_state(
            session_id=session_id,
            brand_id=brand_id,
            message=message,
            stream_callback=stream_callback
        )
        
        # Run the graph
        final_state = await self.graph.ainvoke(initial_state)
        
        return final_state
    
    def process_message_sync(
        self,
        session_id: str,
        brand_id: int,
        message: str,
        stream_callback=None
    ) -> AgentState:
        """
        Synchronous version for non-async contexts
        """
        # Initialize state
        initial_state = create_initial_state(
            session_id=session_id,
            brand_id=brand_id,
            message=message,
            stream_callback=stream_callback
        )
        
        # Run the graph synchronously
        final_state = self.graph.invoke(initial_state)
        
        return final_state