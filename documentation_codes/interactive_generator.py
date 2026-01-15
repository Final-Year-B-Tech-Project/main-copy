#!/usr/bin/env python3
"""
Interactive Mermaid Diagram Generator
Provides a CLI interface for generating specific diagrams
"""

import sys
from mermaid_generator import MermaidGenerator

class InteractiveMermaidGenerator:
    """Interactive CLI for Mermaid diagram generation"""
    
    def __init__(self):
        self.generator = MermaidGenerator()
        self.menu_options = {
            '1': ('System Architecture', self.generator.generate_system_architecture),
            '2': ('User Flow Diagram', self.generator.generate_user_flow),
            '3': ('Database Schema', self.generator.generate_database_schema),
            '4': ('API Endpoints', self.generator.generate_api_endpoints),
            '5': ('Interview Process', self.generator.generate_interview_process),
            '6': ('Deployment Architecture', self.generator.generate_deployment_diagram),
            '7': ('Application States', self.generator.generate_state_diagram),
            '8': ('Class Diagram', self.generator.generate_class_diagram),
            '9': ('Component Architecture', self.generator.generate_component_diagram),
            '10': ('Project Timeline', self.generator.generate_timeline_diagram),
            '11': ('Git Workflow', self.generator.generate_gitflow_diagram),
            '12': ('Generate All Diagrams', self.generator.generate_all_diagrams),
            '0': ('Exit', self.exit_program)
        }
    
    def display_menu(self):
        """Display the interactive menu"""
        print("\n" + "="*60)
        print("🎨 MERMAID DIAGRAM GENERATOR - AI INTERVIEW SYSTEM")
        print("="*60)
        print("Select a diagram type to generate:")
        print()
        
        for key, (name, _) in self.menu_options.items():
            if key == '0':
                print(f"  {key}. {name}")
            elif key == '12':
                print(f" {key}. 🚀 {name}")
            else:
                print(f"  {key}. 📊 {name}")
        
        print("="*60)
    
    def get_user_choice(self):
        """Get user's menu choice"""
        while True:
            choice = input("\nEnter your choice (0-12): ").strip()
            if choice in self.menu_options:
                return choice
            print("❌ Invalid choice. Please enter a number between 0-12.")
    
    def execute_choice(self, choice):
        """Execute the selected menu option"""
        name, function = self.menu_options[choice]
        
        if choice == '0':
            function()
            return False
        
        print(f"\n🔄 Generating {name}...")
        try:
            function()
            print(f"✅ {name} generated successfully!")
            
            if choice != '12':  # Don't ask for another if generating all
                another = input("\n🔄 Generate another diagram? (y/n): ").strip().lower()
                return another in ['y', 'yes']
            return True
            
        except Exception as e:
            print(f"❌ Error generating {name}: {str(e)}")
            return True
    
    def exit_program(self):
        """Exit the program gracefully"""
        print("\n👋 Thank you for using Mermaid Diagram Generator!")
        print("📁 Check the 'diagrams' folder for your generated files.")
        sys.exit(0)
    
    def run(self):
        """Run the interactive generator"""
        print("🚀 Welcome to the Interactive Mermaid Diagram Generator!")
        
        while True:
            self.display_menu()
            choice = self.get_user_choice()
            
            if not self.execute_choice(choice):
                break

if __name__ == "__main__":
    app = InteractiveMermaidGenerator()
    app.run()