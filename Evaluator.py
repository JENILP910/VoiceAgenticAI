from LLMUtil import LLMProvider
from AgentUtil import AgentState, AgentLogger
from typing import Dict, Any
import json




class Evaluator:
    """Evaluates execution results and determines next steps"""
    def __init__(self, llm_provider: LLMProvider, logger: AgentLogger):
        self.llm = llm_provider
        self.logger = logger
    
    def evaluate(self, execution_results: Dict[str, Any], state: AgentState, plan: Dict) -> Dict[str, Any]:
        self.logger.log('evaluator', 'परिणाम मूल्यांकन करत आहे...')
        
        context = {
            'results': execution_results,
            'currentState': {
                'phase': state.phase,
                'userProfile': state.user_profile,
                'eligibleSchemes': [s['name'] for s in state.eligible_schemes]
            },
            'conversationHistory': state.conversation_history[-3:],
            'plan': plan
        }
        
        system_prompt = """तुम्ही अंमलबजावणीच्या परिणामांचे मूल्यांकन करा आणि पुढील पावले ठरवा.

फक्त JSON फॉरमॅटमध्ये उत्तर द्या (कोणतेही अतिरिक्त मजकूर नको):
{
  "nextPhase": "gathering|evaluating|presenting|applying|complete",
  "response": "मराठी मध्ये वापरकर्त्याला संक्षिप्त उत्तर (२-३ वाक्ये)",
  "updatedProfile": {},
  "eligibleSchemes": [],
  "missingInfo": [],
  "selectedScheme": null
}

Phases:
- gathering: माहिती गोळा करणे
- evaluating: पात्रता तपासणे
- presenting: योजना सादर करणे
- applying: अर्ज प्रक्रिया
- complete: पूर्ण झाले"""

        user_message = f"Context: {json.dumps(context, ensure_ascii=False)}\n\nफक्त JSON उत्तर द्या."
        
        try:
            response_text = self.llm.generate(system_prompt, user_message, max_tokens=1000)
            
            # Clean response
            response_text = response_text.strip()
            if '```json' in response_text:
                response_text = response_text.split('```json')[1].split('```')[0]
            elif '```' in response_text:
                response_text = response_text.split('```')[1].split('```')[0]
            
            evaluation = json.loads(response_text.strip())
            return evaluation
            
        except Exception as e:
            self.logger.log('error', f"Evaluator error: {str(e)}")
            return {
                'nextPhase': 'gathering',
                'response': 'कृपया तुमची माहिती सांगा - तुमचे वय, उत्पन्न आणि व्यवसाय.',
                'updatedProfile': {},
                'eligibleSchemes': [],
                'missingInfo': ['age', 'income', 'occupation']
            }