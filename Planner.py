
from LLMUtil import LLMProvider
from AgentUtil import AgentLogger, AgentState
from typing import Dict, List, Any, Optional
import json


class Planner:
    """Plans actions based on user input and current state"""
    def __init__(self, llm_provider: LLMProvider, logger: AgentLogger):
        self.llm = llm_provider
        self.logger = logger
    
    def plan(self, user_input: str, state: AgentState) -> Dict[str, Any]:
        self.logger.log('planner', 'योजना बनवत आहे...')
        
        context = {
            'userInput': user_input,
            'currentPhase': state.phase,
            'userProfile': state.user_profile,
            'conversationHistory': state.conversation_history[-5:]
        }
        
        system_prompt = """तुम्ही एक सरकारी योजना सहाय्यक आहात. वापरकर्त्याच्या इनपुटचे विश्लेषण करा आणि कृती योजना तयार करा.

तुम्हाला फक्त JSON फॉरमॅटमध्ये उत्तर द्यावे (कोणतेही अतिरिक्त मजकूर नको):
{
  "intent": "user's intent",
  "actions": [{"type": "action_type", "params": {}}],
  "userInput": "original input"
}

Available actions:
- extract_info: वापरकर्त्याची माहिती काढा
- check_eligibility: योजनांसाठी पात्रता तपासा
- fetch_scheme_details: योजना तपशील आणा
- validate_documents: कागदपत्रे तपासा"""

        user_message = f"Context: {json.dumps(context, ensure_ascii=False)}\n\nफक्त JSON उत्तर द्या, कोणतेही स्पष्टीकरण नको."

        try:
            response_text = self.llm.generate(system_prompt, user_message, max_tokens=1000)
            
            # Clean the response
            response_text = response_text.strip()
            if '```json' in response_text:
                response_text = response_text.split('```json')[1].split('```')[0]
            elif '```' in response_text:
                response_text = response_text.split('```')[1].split('```')[0]
            
            plan = json.loads(response_text.strip())
            self.logger.log('planner', f"योजना: {plan.get('intent', 'unknown')}")
            return plan
            
        except Exception as e:
            self.logger.log('error', f"Planner error: {str(e)}")
            return {
                'intent': 'gather_info',
                'actions': [{'type': 'extract_info', 'params': {}}],
                'userInput': user_input
            }