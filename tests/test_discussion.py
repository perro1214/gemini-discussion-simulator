#!/usr/bin/env python3
"""
Test script for the Discussion System
"""

import asyncio
import os
import sys
import inspect

# Add the project root to the Python path
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

from src.discussion_system import DiscussionSystem


async def test_discussion():
    """Test the discussion system with a simple topic"""
    # Mock API key for testing (you should set a real one)
    api_key = os.getenv('GEMINI_API_KEY', 'test_key')
    
    if api_key == 'test_key':
        print("Warning: Using mock API key. Set GEMINI_API_KEY environment variable for real testing.")
        print("This test will demonstrate the system structure without making actual API calls.")
        return
    
    # Create discussion system
    system = DiscussionSystem(api_key)
    
    # Set a simple test topic
    test_topic = "Should AI be used in schools?"
    system.set_topic(test_topic)
    
    # Add test agents
    system.add_agent(
        name="Teacher Tom",
        role="Experienced Teacher",
        personality="Practical, focused on student learning outcomes"
    )
    
    system.add_agent(
        name="Tech Sarah",
        role="Ed-Tech Specialist",
        personality="Enthusiastic about technology integration"
    )
    
    system.add_agent(
        name="Parent Mike",
        role="Concerned Parent",
        personality="Worried about screen time and privacy"
    )
    
    try:
        print("Testing Discussion System")
        print(f"Topic: {test_topic}")
        print(f"Agents: {[agent.name for agent in system.agents]}")
        
        # Test with 2 rounds for quicker testing
        messages = await system.conduct_discussion(rounds=2)
        print(f"\nGenerated {len(messages)} messages")
        
        # Test summary generation
        summary = await system.summarize_discussion()
        print(f"\nSummary generated: {len(summary)} characters")
        
        # Test saving
        system.save_discussion("results/test_discussion.json")
        print("Discussion saved successfully")
        
        print("\n✅ All tests passed!")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")


if __name__ == "__main__":
    asyncio.run(test_discussion())