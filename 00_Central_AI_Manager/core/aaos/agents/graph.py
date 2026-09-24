"""
AAOS Multi-Agent Workflow Graph (LangGraph)
Orchestrates MasterAgent, ContentAgent, QAAgent, PublishAgent, VerifierNode, and RecoveryAgent.
"""

from typing import Dict, Any, Literal
from langgraph.graph import StateGraph, START, END

from core.aaos.agents.state import AAOSState
from core.aaos.agents.master_agent import MasterAgent
from core.aaos.agents.content_agent import ContentAgent
from core.aaos.agents.qa_agent import QAAgent
from core.aaos.agents.publish_agent import PublishAgent
from core.aaos.agents.recovery_agent import VerifierNode, RecoveryAgent

# ── Conditional Routers ───────────────────────────────────────────────────────

def route_after_qa(state: AAOSState) -> Literal["publish", "content", "recovery"]:
    qa = state.get("qa_results", {})
    if qa.get("passed", False):
        return "publish"
    if state.get("qa_retries", 0) < 2:
        return "content"
    return "recovery"

def route_after_publish(state: AAOSState) -> Literal["verifier", "recovery"]:
    pub = state.get("publish_result", {})
    if pub.get("success", False):
        return "verifier"
    return "recovery"

def route_after_verification(state: AAOSState) -> Literal["master_end", "recovery"]:
    verif = state.get("verification_result", {})
    if verif.get("verified", False):
        return "master_end"
    return "recovery"

def route_after_recovery(state: AAOSState) -> Literal["publish", "master_end"]:
    if state.get("recovery_attempts", 0) < 3:
        return "publish"
    return "master_end"

# ── Build Graph ───────────────────────────────────────────────────────────────

def create_aaos_graph():
    builder = StateGraph(AAOSState)

    # Add Nodes
    builder.add_node("master_start", MasterAgent.initialize)
    builder.add_node("content", ContentAgent.generate_content)
    builder.add_node("qa", QAAgent.audit)
    builder.add_node("publish", PublishAgent.publish)
    builder.add_node("verifier", VerifierNode.verify)
    builder.add_node("recovery", RecoveryAgent.recover)
    builder.add_node("master_end", MasterAgent.finalize)

    # Add Edges
    builder.add_edge(START, "master_start")
    builder.add_edge("master_start", "content")
    builder.add_edge("content", "qa")

    builder.add_conditional_edges(
        "qa",
        route_after_qa,
        {
            "publish": "publish",
            "content": "content",
            "recovery": "recovery"
        }
    )

    builder.add_conditional_edges(
        "publish",
        route_after_publish,
        {
            "verifier": "verifier",
            "recovery": "recovery"
        }
    )

    builder.add_conditional_edges(
        "verifier",
        route_after_verification,
        {
            "master_end": "master_end",
            "recovery": "recovery"
        }
    )

    builder.add_conditional_edges(
        "recovery",
        route_after_recovery,
        {
            "publish": "publish",
            "master_end": "master_end"
        }
    )

    builder.add_edge("master_end", END)

    return builder.compile()

aaos_workflow = create_aaos_graph()
