from datetime import datetime



class AgentState:
    """Manages the agent's internal state"""
    def __init__(self):
        self.phase = 'idle'
        self.user_profile = {}
        self.eligible_schemes = []
        self.selected_scheme = None
        self.missing_info = []
        self.conversation_history = []
        
class AgentLogger:
    """Logs all agent activities"""
    def __init__(self):
        self.logs = []
    
    def log(self, log_type: str, message: str):
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = {
            'type': log_type,
            'message': message,
            'timestamp': timestamp
        }
        self.logs.append(log_entry)
        print(f"[{timestamp}] [{log_type.upper()}] {message}")
