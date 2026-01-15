#!/usr/bin/env python3
"""
Simple Database Viewer for Talent Sync
Run: python db_viewer.py
"""

import sqlite3
import os
from tabulate import tabulate

DB_PATH = "instance/interview_agent.db"

def connect_db():
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found: {DB_PATH}")
        return None
    return sqlite3.connect(DB_PATH)

def show_tables():
    conn = connect_db()
    if not conn:
        return
    
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    print("📊 Available Tables:")
    for i, (table,) in enumerate(tables, 1):
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"{i}. {table} ({count} records)")
    
    conn.close()

def show_table_data(table_name):
    conn = connect_db()
    if not conn:
        return
    
    cursor = conn.cursor()
    try:
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 10")
        rows = cursor.fetchall()
        
        # Get column names
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [col[1] for col in cursor.fetchall()]
        
        if rows:
            print(f"\n📋 {table_name} (showing first 10 records):")
            print(tabulate(rows, headers=columns, tablefmt="grid"))
        else:
            print(f"\n📋 {table_name}: No data found")
            
    except sqlite3.Error as e:
        print(f"❌ Error: {e}")
    
    conn.close()

def main():
    print("🎯 Talent Sync Database Viewer")
    print("=" * 40)
    
    while True:
        print("\nOptions:")
        print("1. Show all tables")
        print("2. View table data")
        print("3. Run custom query")
        print("4. Exit")
        
        choice = input("\nEnter choice (1-4): ").strip()
        
        if choice == "1":
            show_tables()
        elif choice == "2":
            table_name = input("Enter table name: ").strip()
            show_table_data(table_name)
        elif choice == "3":
            query = input("Enter SQL query: ").strip()
            conn = connect_db()
            if conn:
                try:
                    cursor = conn.cursor()
                    cursor.execute(query)
                    results = cursor.fetchall()
                    print(f"\n📊 Query Results:")
                    for row in results:
                        print(row)
                except sqlite3.Error as e:
                    print(f"❌ Error: {e}")
                conn.close()
        elif choice == "4":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice")

if __name__ == "__main__":
    main()