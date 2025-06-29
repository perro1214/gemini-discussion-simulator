#!/usr/bin/env python3
"""
Agent classes for discussion system
"""

from dataclasses import dataclass

@dataclass
class Agent:
    """Discussion agent with role and personality"""
    name: str
    role: str
    personality: str
    
    def __str__(self):
        return f"{self.name} ({self.role}): {self.personality}"

@dataclass 
class Message:
    """Discussion message from an agent"""
    agent_name: str
    content: str
    timestamp: float