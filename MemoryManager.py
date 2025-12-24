from AgentUtil import AgentLogger, AgentState
from datetime import datetime
from typing import Dict, List, Any





class MemoryManager:
    """Manages conversation memory and detects contradictions"""
    def __init__(self, logger: AgentLogger):
        self.logger = logger
    
    def update_memory(self, state: AgentState, user_input: str, agent_response: str):
        """Update conversation history"""
        state.conversation_history.append({
            'role': 'user',
            'content': user_input,
            'timestamp': datetime.now().isoformat()
        })
        state.conversation_history.append({
            'role': 'agent',
            'content': agent_response,
            'timestamp': datetime.now().isoformat()
        })
    
    def detect_contradictions(self, new_info: Dict, existing_profile: Dict) -> List[Dict[str, Any]]:
        """Detect contradictions in user information"""
        contradictions = []
        
        for key, value in new_info.items():
            if key in existing_profile and existing_profile[key] != value:
                contradictions.append({
                    'field': key,
                    'oldValue': existing_profile[key],
                    'newValue': value
                })
                self.logger.log('memory', f"विरोधाभास आढळला: {key}")
        
        return contradictions
