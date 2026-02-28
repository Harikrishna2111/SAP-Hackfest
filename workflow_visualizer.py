"""
Workflow Visualizer for n8n-style visualization
Creates visual representations of the Verilog verification workflow
"""

import json
from typing import List, Dict, Optional
import plotly.graph_objects as go
import plotly.express as px


class WorkflowVisualizer:
    """Creates workflow visualizations"""
    
    # Define workflow nodes
    WORKFLOW_NODES = [
        {
            "id": "analyze",
            "label": "Analyze Design",
            "description": "Analyzes design image and code structure",
            "icon": "🔍",
            "color": "#667eea"
        },
        {
            "id": "identify",
            "label": "Identify Issues",
            "description": "Identifies mismatches and errors",
            "icon": "🔎",
            "color": "#764ba2"
        },
        {
            "id": "fix",
            "label": "Fix Issues",
            "description": "Applies fixes to the code",
            "icon": "🔧",
            "color": "#f093fb"
        },
        {
            "id": "verify",
            "label": "Verify Fixes",
            "description": "Validates applied fixes",
            "icon": "✅",
            "color": "#4facfe"
        },
        {
            "id": "report",
            "label": "Generate Report",
            "description": "Creates comprehensive report",
            "icon": "📊",
            "color": "#11998e"
        }
    ]
    
    @staticmethod
    def create_workflow_diagram(current_step: Optional[str] = None, completed_steps: List[str] = None) -> go.Figure:
        """Create an interactive workflow diagram"""
        if completed_steps is None:
            completed_steps = []
        
        # Define node positions (x, y coordinates)
        x_positions = [i for i in range(len(WorkflowVisualizer.WORKFLOW_NODES))]
        y_positions = [0] * len(WorkflowVisualizer.WORKFLOW_NODES)
        
        # Prepare node data
        node_labels = []
        node_colors = []
        node_sizes = []
        
        for node in WorkflowVisualizer.WORKFLOW_NODES:
            node_labels.append(node['label'])
            
            if node['id'] == current_step:
                node_colors.append("#00d4ff")  # Active color
                node_sizes.append(40)
            elif node['id'] in completed_steps:
                node_colors.append("#11998e")  # Completed color
                node_sizes.append(35)
            else:
                node_colors.append("#e0e0e0")  # Pending color
                node_sizes.append(30)
        
        # Create edges between nodes
        edge_x = []
        edge_y = []
        
        for i in range(len(x_positions) - 1):
            edge_x.append(x_positions[i])
            edge_x.append(x_positions[i + 1])
            edge_x.append(None)
            edge_y.append(y_positions[i])
            edge_y.append(y_positions[i + 1])
            edge_y.append(None)
        
        # Create figure
        fig = go.Figure()
        
        # Add edges
        fig.add_trace(go.Scatter(
            x=edge_x, y=edge_y,
            mode='lines',
            line=dict(width=2, color='#cccccc'),
            hoverinfo='none',
            showlegend=False
        ))
        
        # Add nodes
        fig.add_trace(go.Scatter(
            x=x_positions,
            y=y_positions,
            mode='markers+text',
            marker=dict(
                size=node_sizes,
                color=node_colors,
                line=dict(width=2, color='white')
            ),
            text=node_labels,
            textposition="bottom center",
            hoverinfo='text',
            hovertext=[f"{node['label']}<br>{node['description']}" 
                      for node in WorkflowVisualizer.WORKFLOW_NODES],
            showlegend=False
        ))
        
        # Update layout
        fig.update_layout(
            title="Verification Workflow",
            showlegend=False,
            hovermode='closest',
            margin=dict(b=20, l=5, r=5, t=40),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor='rgba(240,240,240,0.5)',
            height=300
        )
        
        return fig
    
    @staticmethod
    def create_issues_timeline(issues: List[Dict]) -> go.Figure:
        """Create a timeline of issues by severity"""
        
        severity_map = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        
        issues_by_severity = {}
        for severity in ["critical", "high", "medium", "low"]:
            issues_by_severity[severity] = len([i for i in issues if i.get('severity') == severity])
        
        colors = {
            "critical": "#eb3349",
            "high": "#ff9500",
            "medium": "#fdd835",
            "low": "#4caf50"
        }
        
        fig = go.Figure(data=[
            go.Bar(
                y=list(issues_by_severity.keys()),
                x=list(issues_by_severity.values()),
                orientation='h',
                marker=dict(color=[colors.get(k, '#999999') for k in issues_by_severity.keys()]),
                text=list(issues_by_severity.values()),
                textposition='auto',
            )
        ])
        
        fig.update_layout(
            title="Issues by Severity",
            xaxis_title="Count",
            yaxis_title="Severity",
            height=300,
            margin=dict(l=50, r=20, t=40, b=20)
        )
        
        return fig
    
    @staticmethod
    def create_iteration_stats(num_iterations: int, num_issues: int, num_fixes: int) -> go.Figure:
        """Create iteration statistics visualization"""
        
        categories = ["Iterations", "Issues Found", "Fixes Applied"]
        values = [num_iterations, num_issues, num_fixes]
        colors = ["#667eea", "#f093fb", "#11998e"]
        
        fig = go.Figure(data=[
            go.Bar(
                x=categories,
                y=values,
                marker=dict(color=colors),
                text=values,
                textposition='auto',
            )
        ])
        
        fig.update_layout(
            title="Verification Statistics",
            yaxis_title="Count",
            height=300,
            margin=dict(l=50, r=20, t=40, b=20),
            showlegend=False
        )
        
        return fig
    
    @staticmethod
    def export_workflow_json(state: Dict) -> str:
        """Export workflow execution as JSON"""
        
        workflow_data = {
            "timestamp": str(state.get('timestamp', '')),
            "status": state.get('status', 'unknown'),
            "iterations": state.get('iteration', 0),
            "max_iterations": state.get('max_iterations', 0),
            "issues_found": len(state.get('issues_found', [])),
            "fixes_applied": len(state.get('fixes_applied', [])),
            "issues": state.get('issues_found', []),
            "fixes": state.get('fixes_applied', []),
            "analysis_history_length": len(state.get('analysis_history', []))
        }
        
        return json.dumps(workflow_data, indent=2)


def create_execution_log_display(log_entries: List[Dict]):
    """Create a visual execution log"""
    
    log_html = "<div style='background: #f5f5f5; padding: 15px; border-radius: 8px;'>"
    
    for entry in log_entries:
        timestamp = entry.get('timestamp', '')
        step = entry.get('step', '')
        status = entry.get('status', '')
        details = entry.get('details', '')
        
        status_icon = {
            "success": "✅",
            "error": "❌",
            "running": "⏳",
            "pending": "⏱️"
        }.get(status, "ℹ️")
        
        log_html += f"""
        <div style='margin-bottom: 10px; padding: 10px; background: white; border-radius: 4px;'>
            <span style='color: #999;'>[{timestamp}]</span>
            <span style='margin-left: 10px;'>{status_icon} <strong>{step}</strong></span>
            <div style='margin-left: 20px; color: #666; font-size: 0.9em;'>{details}</div>
        </div>
        """
    
    log_html += "</div>"
    
    return log_html
