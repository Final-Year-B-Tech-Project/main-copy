#!/usr/bin/env python3
"""
Quick Start Script - Generate All Mermaid Diagrams
Generates both core and custom diagrams in one command
"""

from mermaid_generator import MermaidGenerator
from custom_diagrams import CustomDiagramGenerator

def main():
    """Generate all diagrams - core and custom"""
    print("=" * 60)
    print("MERMAID DIAGRAM GENERATOR - COMPLETE SUITE")
    print("AI Interview System Documentation")
    print("=" * 60)
    
    # Generate core diagrams
    print("\n[1/2] Generating Core System Diagrams...")
    core_generator = MermaidGenerator()
    core_generator.generate_all_diagrams()
    
    # Generate custom diagrams
    print("\n[2/2] Generating Custom Specialized Diagrams...")
    custom_generator = CustomDiagramGenerator()
    custom_generator.generate_all_custom_diagrams()
    
    print("\n" + "=" * 60)
    print("GENERATION COMPLETE!")
    print("=" * 60)
    print("Total diagrams generated: 18")
    print("Location: ./diagrams/ folder")
    print("\nNext Steps:")
    print("1. Browse the diagrams/ folder")
    print("2. Copy Mermaid code to https://mermaid.live for preview")
    print("3. Use diagrams in your documentation")
    print("4. Export as PNG/SVG for presentations")
    print("=" * 60)

if __name__ == "__main__":
    main()