#!/usr/bin/env python3
"""
Quick Generator - Essential Diagrams Only
Block Diagrams + Flowcharts + Methodology
"""

from focused_diagrams import FocusedDiagramGenerator

def main():
    print("QUICK DIAGRAM GENERATOR")
    print("Block Diagrams | Flowcharts | Methodology")
    print("=" * 40)
    
    generator = FocusedDiagramGenerator()
    
    # Generate only the most essential diagrams
    essential = [
        ("System Block Diagram", generator.generate_system_block_diagram),
        ("AI Interview Flowchart", generator.generate_ai_interview_flowchart),
        ("Project Methodology", generator.generate_methodology_diagram),
        ("Data Flow", generator.generate_data_flow_diagram)
    ]
    
    for name, func in essential:
        print(f"Creating {name}...")
        func()
    
    print("=" * 40)
    print("DONE! 4 essential diagrams created.")
    print("Check: focused_diagrams/ folder")

if __name__ == "__main__":
    main()