#!/usr/bin/env python3
"""
Mermaid Diagram Templates
Reusable templates for creating custom diagrams
"""

class DiagramTemplates:
    """Collection of reusable Mermaid diagram templates"""
    
    @staticmethod
    def flowchart_template(title: str, nodes: dict, connections: list) -> str:
        """
        Generate a flowchart from template
        
        Args:
            title: Diagram title
            nodes: Dict of {node_id: node_label}
            connections: List of tuples (from_node, to_node, label)
        """
        diagram = f"flowchart TD\n    %% {title}\n"
        
        # Add nodes
        for node_id, label in nodes.items():
            diagram += f"    {node_id}[{label}]\n"
        
        diagram += "\n"
        
        # Add connections
        for connection in connections:
            if len(connection) == 2:
                from_node, to_node = connection
                diagram += f"    {from_node} --> {to_node}\n"
            elif len(connection) == 3:
                from_node, to_node, label = connection
                diagram += f"    {from_node} -->|{label}| {to_node}\n"
        
        return diagram
    
    @staticmethod
    def sequence_template(title: str, participants: list, interactions: list) -> str:
        """
        Generate a sequence diagram from template
        
        Args:
            title: Diagram title
            participants: List of participant names
            interactions: List of tuples (from, to, message, type)
        """
        diagram = f"sequenceDiagram\n    %% {title}\n"
        
        # Add participants
        for participant in participants:
            diagram += f"    participant {participant}\n"
        
        diagram += "\n"
        
        # Add interactions
        for interaction in interactions:
            if len(interaction) == 3:
                from_p, to_p, message = interaction
                diagram += f"    {from_p}->>+{to_p}: {message}\n"
            elif len(interaction) == 4:
                from_p, to_p, message, arrow_type = interaction
                diagram += f"    {from_p}{arrow_type}{to_p}: {message}\n"
        
        return diagram
    
    @staticmethod
    def class_template(title: str, classes: dict) -> str:
        """
        Generate a class diagram from template
        
        Args:
            title: Diagram title
            classes: Dict of {class_name: {attributes: [], methods: [], relationships: []}}
        """
        diagram = f"classDiagram\n    %% {title}\n"
        
        for class_name, details in classes.items():
            diagram += f"    class {class_name} {{\n"
            
            # Add attributes
            for attr in details.get('attributes', []):
                diagram += f"        +{attr}\n"
            
            # Add methods
            for method in details.get('methods', []):
                diagram += f"        +{method}\n"
            
            diagram += "    }\n\n"
        
        # Add relationships
        for class_name, details in classes.items():
            for relationship in details.get('relationships', []):
                diagram += f"    {relationship}\n"
        
        return diagram
    
    @staticmethod
    def er_template(title: str, entities: dict, relationships: list) -> str:
        """
        Generate an ER diagram from template
        
        Args:
            title: Diagram title
            entities: Dict of {entity_name: [attributes]}
            relationships: List of relationship strings
        """
        diagram = f"erDiagram\n    %% {title}\n"
        
        for entity, attributes in entities.items():
            diagram += f"    {entity} {{\n"
            for attr in attributes:
                diagram += f"        {attr}\n"
            diagram += "    }\n\n"
        
        for relationship in relationships:
            diagram += f"    {relationship}\n"
        
        return diagram
    
    @staticmethod
    def state_template(title: str, states: list, transitions: list) -> str:
        """
        Generate a state diagram from template
        
        Args:
            title: Diagram title
            states: List of state names
            transitions: List of tuples (from_state, to_state, trigger)
        """
        diagram = f"stateDiagram-v2\n    %% {title}\n"
        
        diagram += "    [*] --> " + states[0] + "\n"
        
        for transition in transitions:
            if len(transition) == 2:
                from_state, to_state = transition
                diagram += f"    {from_state} --> {to_state}\n"
            elif len(transition) == 3:
                from_state, to_state, trigger = transition
                diagram += f"    {from_state} --> {to_state} : {trigger}\n"
        
        if states:
            diagram += f"    {states[-1]} --> [*]\n"
        
        return diagram
    
    @staticmethod
    def gantt_template(title: str, sections: dict) -> str:
        """
        Generate a Gantt chart from template
        
        Args:
            title: Chart title
            sections: Dict of {section_name: [(task_name, start_date, duration)]}
        """
        diagram = f"gantt\n    title {title}\n    dateFormat YYYY-MM-DD\n\n"
        
        for section_name, tasks in sections.items():
            diagram += f"    section {section_name}\n"
            for task_name, start_date, duration in tasks:
                diagram += f"    {task_name} : {start_date}, {duration}\n"
            diagram += "\n"
        
        return diagram
    
    @staticmethod
    def pie_template(title: str, data: dict) -> str:
        """
        Generate a pie chart from template
        
        Args:
            title: Chart title
            data: Dict of {label: value}
        """
        diagram = f"pie title {title}\n"
        
        for label, value in data.items():
            diagram += f'    "{label}" : {value}\n'
        
        return diagram

# Example usage functions
def create_custom_api_flow():
    """Example: Create a custom API flow diagram"""
    nodes = {
        "Client": "Client Application",
        "Gateway": "API Gateway",
        "Auth": "Authentication Service",
        "Business": "Business Logic",
        "Database": "Database"
    }
    
    connections = [
        ("Client", "Gateway", "HTTP Request"),
        ("Gateway", "Auth", "Validate Token"),
        ("Auth", "Gateway", "Token Valid"),
        ("Gateway", "Business", "Process Request"),
        ("Business", "Database", "Query Data"),
        ("Database", "Business", "Return Data"),
        ("Business", "Gateway", "Response"),
        ("Gateway", "Client", "HTTP Response")
    ]
    
    return DiagramTemplates.flowchart_template("Custom API Flow", nodes, connections)

def create_user_registration_sequence():
    """Example: Create a user registration sequence"""
    participants = ["User", "Frontend", "Backend", "Database", "EmailService"]
    
    interactions = [
        ("User", "Frontend", "Fill Registration Form"),
        ("Frontend", "Backend", "POST /register"),
        ("Backend", "Database", "Check if user exists"),
        ("Database", "Backend", "User not found"),
        ("Backend", "Database", "Create new user"),
        ("Database", "Backend", "User created"),
        ("Backend", "EmailService", "Send welcome email"),
        ("EmailService", "Backend", "Email sent"),
        ("Backend", "Frontend", "Registration success"),
        ("Frontend", "User", "Show success message")
    ]
    
    return DiagramTemplates.sequence_template("User Registration Flow", participants, interactions)

if __name__ == "__main__":
    # Example usage
    print("🎨 Mermaid Diagram Templates")
    print("=" * 40)
    
    print("\n📊 Custom API Flow:")
    print(create_custom_api_flow())
    
    print("\n📊 User Registration Sequence:")
    print(create_user_registration_sequence())