import streamlit as st
from collections import deque
from typing import Dict, List, Tuple, Set, Any
import graphviz

# --- 1. Graph Definition and Utility ---

# The directed graph from LabReport_BSD2513_#1.jpg
LAB1_GRAPH = {
    'A': ['D', 'B'],
    'B': ['C', 'E', 'G'],
    'C': ['A'],
    'D': ['C'],
    'E': ['H'],
    'F': [],
    'G': ['F'],
    'H': ['G', 'F']
}

ALL_NODES = sorted(LAB1_GRAPH.keys())

# --- FIXED NODE POSITIONS (based on the original image) ---
# We use Graphviz 'neato' engine and specify (x, y) coordinates for a consistent layout.
NODE_POSITIONS = {
    'A': '3, 4',
    'B': '5, 3',
    'C': '3, 2',
    'D': '1, 3',
    'E': '7, 4',
    'F': '9, 2',
    'G': '7, 2',
    'H': '9, 4',
}


def get_all_nodes(graph: Dict[str, List[str]]) -> List[str]:
    # Extracts all unique nodes from the graph.
    nodes = set(graph.keys())
    for neighbors in graph.values():
        nodes.update(neighbors)
    return sorted(nodes)


# --- 2. Traversal Algorithms (BFS and DFS) ---

def breadth_first_search(
        graph: Dict[str, List[str]],
        start_node: str,
) -> Tuple[List[str], List[Dict[str, Any]]]:

    expanded_order: List[str] = []
    trace: List[Dict[str, Any]] = []
    queue: deque[str] = deque([start_node])
    visited: Set[str] = {start_node}

    while queue:
        node = queue.popleft()
        expanded_order.append(node)
        trace.append({
            "expanded": node,
            "frontier": list(queue),
            "visited": list(visited),
            "process_path": " → ".join(expanded_order)
        })
        neighbors = sorted(graph.get(node, []))
        for neighbor in neighbors:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    return expanded_order, trace


def depth_first_search(
        graph: Dict[str, List[str]],
        start_node: str,
) -> Tuple[List[str], List[Dict[str, Any]]]:

    expanded_order: List[str] = []
    trace: List[Dict[str, Any]] = []
    stack: List[str] = [start_node]
    visited: Set[str] = {start_node}

    while stack:
        node = stack.pop()
        expanded_order.append(node)
        trace.append({
            "expanded": node,
            "frontier": stack[::-1],
            "visited": list(visited),
            "process_path": " → ".join(expanded_order)
        })
        neighbors = sorted(graph.get(node, []), reverse=True)
        for neighbor in neighbors:
            if neighbor not in visited:
                visited.add(neighbor)
                stack.append(neighbor)
    return expanded_order, trace


# --- 3. Streamlit UI and Visualization ---

st.set_page_config(
    page_title="Graph Traversal (BFS & DFS)",
    page_icon="🗺️",
    layout="wide"
)

st.title("🗺️ Graph Traversal: BFS and DFS")
st.caption("Implementation for Lab Report 1: Search Algorithms (Question 2)")

st.subheader("Graph Structure")
st.image("LabReport_BSD2513_#1.jpg", caption="Original Graph Image")


# Graphviz function with fixed positions
def to_graphviz(graph: Dict[str, List[str]], expanded_order: List[str]) -> graphviz.Digraph:
    # Build DOT source with fixed positions and highlighting the expanded path.
    dot = graphviz.Digraph(comment='Graph Traversal', engine='neato')  # Use 'neato' engine for fixed positions

    # 1. Define Nodes with Fixed Positions and Highlighting
    expanded_set = set(expanded_order)
    for node in get_all_nodes(graph):
        color = '#d32f2f' if node == expanded_order[-1] else ('#4285f4' if node in expanded_set else 'gray')
        fontcolor = 'white' if node == expanded_order[-1] else 'black'

        # Apply fixed position from the dictionary
        pos_attr = f"{NODE_POSITIONS.get(node, '0,0')}!"  # '!' fixes the position

        dot.node(
            node,
            node,
            style='filled',
            fillcolor=color,
            fontcolor=fontcolor,
            pos=pos_attr,
            width='0.5',
            height='0.5',
        )

    # 2. Define Edges
    for u, neighbors in graph.items():
        for v in neighbors:
            dot.edge(u, v, color='#4285f4')

    return dot


# --- Sidebar for Controls ---
with st.sidebar:
    st.header("Traversal Controls")

    # Node selection
    start_node = st.selectbox(
        "Select Start Node",
        ALL_NODES,
        index=ALL_NODES.index('A') if 'A' in ALL_NODES else 0
    )

    # Algorithm selection
    algorithm = st.radio(
        "Select Search Algorithm",
        ["Breadth-First Search (BFS)", "Depth-First Search (DFS)"],
        index=0
    )

    run_btn = st.button("Run Traversal", type="primary")

st.divider()

# --- Main Content Area ---
if run_btn and start_node:
    if algorithm == "Breadth-First Search (BFS)":
        expanded_path, trace_data = breadth_first_search(LAB1_GRAPH, start_node)
        st.subheader("Breadth-First Search (BFS) Results")
        st.markdown(
            "**Rule:** Uses a **Queue** (FIFO - First-In, First-Out). **Tie-breaking:** Alphabetical."
        )
    else:  # DFS
        expanded_path, trace_data = depth_first_search(LAB1_GRAPH, start_node)
        st.subheader("Depth-First Search (DFS) Results")
        st.markdown(
            "**Rule:** Uses a **Stack** (LIFO - Last-In, First-Out). **Tie-breaking:** Alphabetical."
        )

    # 1. Output the Traversal Path and Process Path
    col_path, col_trace = st.columns(2)

    with col_path:
        st.markdown("### Traversal Path (Expanded Order)")
        st.code(" → ".join(expanded_path))

    with col_trace:
        st.markdown("### Process Path (Trace Table)")
        process_data = [
            {"Step": i + 1, "Expanded Node": step['expanded'], "Process Path": step['process_path']}
            for i, step in enumerate(trace_data)
        ]
        st.dataframe(process_data, use_container_width=True, hide_index=True)

    # 2. Step-by-Step Trace (Frontier/Queue/Stack)
    st.markdown("### Step-by-Step Frontier Trace")
    with st.expander("Show detailed step-by-step trace"):
        for i, snap in enumerate(trace_data, start=1):
            frontier_label = "Queue" if algorithm == "Breadth-First Search (BFS)" else "Stack (LIFO)"
            st.code(
                f"Step {i}: Expanded Node: {snap['expanded']}\n"
                f"   {frontier_label}: {', '.join(snap['frontier'])}\n"
            )

    # 3. Graph Visualization
    st.markdown("### Traversal Visualization")
    st.graphviz_chart(to_graphviz(LAB1_GRAPH, expanded_path))

else:
    st.info("Select a starting node and click 'Run Traversal' to see the path and trace.")
