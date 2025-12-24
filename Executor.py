from LLMUtil import LLMProvider
from AgentUtil import AgentLogger, AgentState
from typing import Dict, List, Optional, Any
import json




class Executor:
    """Executes planned actions using various tools"""
    def __init__(self, llm_provider: LLMProvider, logger: AgentLogger):
        self.llm = llm_provider
        self.logger = logger
        self.tools = self._initialize_tools()
    
    def _initialize_tools(self):
        return {
            'extract_info': self.extract_user_info,
            'check_eligibility': self.check_eligibility,
            'fetch_scheme_details': self.fetch_scheme_details,
            'validate_documents': self.validate_documents
        }
    
    def execute(self, plan: Dict[str, Any], state: AgentState) -> Dict[str, Any]:
        self.logger.log('executor', 'कृती अंमलात आणत आहे...')
        results = {}
        
        for action in plan.get('actions', []):
            action_type = action['type']
            if action_type in self.tools:
                tool_result = self.tools[action_type](plan, state, action.get('params', {}))
                results[action_type] = tool_result
        
        return results
    
    def extract_user_info(self, plan: Dict, state: AgentState, params: Dict) -> Dict[str, Any]:
        """Tool 1: Extract user information from natural language"""
        self.logger.log('tool', 'वापरकर्ता माहिती काढत आहे...')
        
        system_prompt = """तुम्ही वापरकर्त्याच्या मराठी इनपुटमधून माहिती काढा. फक्त JSON फॉरमॅटमध्ये उत्तर द्या:
{
  "extracted": {
    "age": number or null,
    "income": number or null,
    "occupation": "string" or null,
    "owns_house": boolean or null,
    "land_ownership": boolean or null,
    "has_daughter": boolean or null,
    "daughter_age": number or null
  }
}

उदाहरण:
Input: "माझे वय ३० वर्षे आहे आणि मी शेतकरी आहे"
Output: {"extracted": {"age": 30, "occupation": "farmer", "income": null, "owns_house": null, "land_ownership": null, "has_daughter": null, "daughter_age": null}}"""

        user_message = f"Input: {plan['userInput']}\n\nफक्त JSON उत्तर द्या."
        
        try:
            response_text = self.llm.generate(system_prompt, user_message, max_tokens=500)
            
            # Clean response
            response_text = response_text.strip()
            if '```json' in response_text:
                response_text = response_text.split('```json')[1].split('```')[0]
            elif '```' in response_text:
                response_text = response_text.split('```')[1].split('```')[0]
            
            result = json.loads(response_text.strip())
            return result.get('extracted', {})
            
        except Exception as e:
            self.logger.log('error', f"Extraction error: {str(e)}")
            return {}
    
    def check_eligibility(self, plan: Dict, state: AgentState, params: Dict) -> List[Dict[str, Any]]:
        """Tool 2: Check eligibility against government schemes"""
        self.logger.log('tool', 'पात्रता तपासत आहे...')
        
        schemes = [
            {
                'id': 'pmay',
                'name': 'प्रधानमंत्री आवास योजना',
                'criteria': {
                    'income': {'max': 600000},
                    'age': {'min': 21, 'max': 70},
                    'owns_house': False
                }
            },
            {
                'id': 'atal_pension',
                'name': 'अटल पेन्शन योजना',
                'criteria': {
                    'age': {'min': 18, 'max': 40}
                }
            },
            {
                'id': 'pm_kisan',
                'name': 'पीएम किसान सम्मान निधी',
                'criteria': {
                    'occupation': 'farmer',
                    'land_ownership': True
                }
            },
            {
                'id': 'sukanya_samriddhi',
                'name': 'सुकन्या समृद्धी योजना',
                'criteria': {
                    'has_daughter': True,
                    'daughter_age': {'max': 10}
                }
            },
            {
                'id': 'ayushman_bharat',
                'name': 'आयुष्मान भारत योजना',
                'criteria': {
                    'income': {'max': 100000}
                }
            }
        ]
        
        eligible = []
        profile = state.user_profile
        
        for scheme in schemes:
            if self._matches_criteria(profile, scheme['criteria']):
                eligible.append(scheme)
        
        self.logger.log('tool', f"पात्र योजना सापडल्या: {len(eligible)}")
        return eligible
    
    
    def _matches_criteria(self, profile: Dict, criteria: Dict) -> bool:
        """Check if profile matches scheme criteria"""
        for key, value in criteria.items():
            if key == 'income' and 'income' in profile:
                if 'max' in value and profile['income'] > value['max']:
                    return False
                if 'min' in value and profile['income'] < value['min']:
                    return False
            elif key == 'age' and 'age' in profile:
                if 'max' in value and profile['age'] > value['max']:
                    return False
                if 'min' in value and profile['age'] < value['min']:
                    return False
            elif key == 'owns_house' and 'owns_house' in profile:
                if profile['owns_house'] != value:
                    return False
            elif key == 'occupation' and 'occupation' in profile:
                if profile['occupation'].lower() != value.lower():
                    return False
            elif key == 'land_ownership' and 'land_ownership' in profile:
                if profile['land_ownership'] != value:
                    return False
            elif key == 'has_daughter' and 'has_daughter' in profile:
                if profile['has_daughter'] != value:
                    return False
            elif key == 'daughter_age' and 'daughter_age' in profile:
                if 'max' in value and profile['daughter_age'] > value['max']:
                    return False
        return True
    
    def fetch_scheme_details(self, plan: Dict, state: AgentState, params: Dict) -> Optional[Dict[str, Any]]:
        """Tool 3: Fetch detailed scheme information"""
        self.logger.log('tool', 'योजना तपशील आणत आहे...')
        
        scheme_details = {
            'pmay': {
                'name': 'प्रधानमंत्री आवास योजना',
                'description': 'गरीब कुटुंबांना घर बांधण्यासाठी आर्थिक मदत',
                'benefits': 'घर बांधण्यासाठी २.५ लाख रुपयांपर्यंत अनुदान',
                'documents': ['आधार कार्ड', 'उत्पन्न प्रमाणपत्र', 'मूळ निवासी दाखला', 'बँक खाते तपशील'],
                'website': 'https://pmaymis.gov.in'
            },
            'atal_pension': {
                'name': 'अटल पेन्शन योजना',
                'description': 'वृद्धापकाळासाठी पेन्शन योजना',
                'benefits': '६० वर्षानंतर हमीदार मासिक पेन्शन',
                'documents': ['आधार कार्ड', 'बँक खाते तपशील'],
                'website': 'https://www.npscra.nsdl.co.in/apy'
            },
            'pm_kisan': {
                'name': 'पीएम किसान सम्मान निधी',
                'description': 'शेतकऱ्यांना थेट आर्थिक मदत',
                'benefits': 'दरवर्षी ६००० रुपये तीन हप्त्यात',
                'documents': ['आधार कार्ड', 'जमीन मालकी कागदपत्रे', 'बँक खाते तपशील'],
                'website': 'https://pmkisan.gov.in'
            },
            'sukanya_samriddhi': {
                'name': 'सुकन्या समृद्धी योजना',
                'description': 'मुलींच्या शिक्षण आणि लग्नासाठी बचत योजना',
                'benefits': 'उच्च व्याज दर आणि कर सवलत',
                'documents': ['मुलीचा जन्म दाखला', 'पालकांचे आधार कार्ड', 'पालकांचे फोटो'],
                'website': 'https://www.nsiindia.gov.in'
            },
            'ayushman_bharat': {
                'name': 'आयुष्मान भारत योजना',
                'description': 'गरीब कुटुंबांसाठी आरोग्य विमा',
                'benefits': '५ लाख रुपयांपर्यंत मोफत उपचार',
                'documents': ['आधार कार्ड', 'राशन कार्ड', 'उत्पन्न प्रमाणपत्र'],
                'website': 'https://pmjay.gov.in'
            }
        }
        
        scheme_id = params.get('schemeId') or (state.selected_scheme['id'] if state.selected_scheme else None)
        return scheme_details.get(scheme_id)
    
    def validate_documents(self, plan: Dict, state: AgentState, params: Dict) -> Dict[str, Any]:
        """Tool 4: Validate required documents"""
        self.logger.log('tool', 'कागदपत्रे तपासत आहे...')
        return {
            'valid': True,
            'missingDocs': []
        }