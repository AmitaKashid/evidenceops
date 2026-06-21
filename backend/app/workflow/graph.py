from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from app.workflow.nodes import WorkflowNodes
from app.workflow.state import WorkflowState


def build_workflow_graph(nodes: WorkflowNodes):
    """Build an explicit, inspectable state graph with bounded stages."""
    graph = StateGraph(WorkflowState)
    graph.add_node("build_contract", nodes.build_contract)
    graph.add_node("retrieve_evidence", nodes.retrieve_evidence)
    graph.add_node("analyze_pricing", nodes.analyze_pricing)
    graph.add_node("research", nodes.research)
    graph.add_node("draft_brief", nodes.draft_brief)
    graph.add_node("verify_brief", nodes.verify_brief)

    graph.add_edge(START, "build_contract")
    graph.add_edge("build_contract", "retrieve_evidence")
    graph.add_edge("retrieve_evidence", "analyze_pricing")
    graph.add_edge("analyze_pricing", "research")
    graph.add_edge("research", "draft_brief")
    graph.add_edge("draft_brief", "verify_brief")
    graph.add_edge("verify_brief", END)
    return graph.compile()
