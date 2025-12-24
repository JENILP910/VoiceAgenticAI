"""
Marathi Voice-Based Government Schemes Agent
Using Open-Source LLMs (Groq, Ollama, or OpenRouter)
"""

import speech_recognition as sr
from gtts import gTTS
import pygame
import os
import tempfile
from typing import Optional

from AgentUtil import AgentLogger, AgentState
from MemoryManager import MemoryManager
from LLMUtil import LLMProvider
from Planner import Planner
from Executor import Executor
from Evaluator import Evaluator



class VoiceInterface:
    """Handles voice input and output"""
    def __init__(self, logger: AgentLogger):
        self.recognizer = sr.Recognizer()
        self.logger = logger
        pygame.mixer.init()
    
    def listen(self) -> Optional[str]:
        """Listen to user voice input in Marathi"""
        self.logger.log('input', 'ऐकत आहे...')
        
        with sr.Microphone() as source:
            print("\nबोला...")
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            
            try:
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                text = self.recognizer.recognize_google(audio, language='mr-IN')
                self.logger.log('input', f"वापरकर्ता: {text}")
                return text
                
            except sr.WaitTimeoutError:
                self.logger.log('error', 'काही ऐकू आले नाही')
                return None
            except sr.UnknownValueError:
                self.logger.log('error', 'समजले नाही')
                return None
            except Exception as e:
                self.logger.log('error', f"Listen error: {str(e)}")
                return None
    
    def speak(self, text: str):
        """Speak text in Marathi"""
        self.logger.log('output', f"एजंट: {text}")
        print(f"\n🔊 {text}")
        
        try:
            tts = gTTS(text=text, lang='mr', slow=False)
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
                temp_file = fp.name
                tts.save(temp_file)
            
            pygame.mixer.music.load(temp_file)
            pygame.mixer.music.play()
            
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            
            pygame.mixer.music.unload()
            os.unlink(temp_file)
            
        except Exception as e:
            self.logger.log('error', f"Speak error: {str(e)}")
            print(f"Text output: {text}")

class MarathiVoiceAgent:
    """Main agent orchestrator"""
    def __init__(self, provider: str, api_key: str, model: str):
        self.logger = AgentLogger()
        self.state = AgentState()
        
        # Initialize LLM provider
        self.llm_provider = LLMProvider(provider, api_key, model, self.logger)
        
        self.planner = Planner(self.llm_provider, self.logger)
        self.executor = Executor(self.llm_provider, self.logger)
        self.evaluator = Evaluator(self.llm_provider, self.logger)
        self.memory = MemoryManager(self.logger)
        self.voice = VoiceInterface(self.logger)
    
    def run(self):
        """Main agent loop"""
        print("\n" + "="*60)
        print("मराठी आवाज सहाय्यक - सरकारी योजना मार्गदर्शक")
        print(f"LLM: {self.llm_provider.provider} - {self.llm_provider.model}")
        print("="*60 + "\n")
        
        welcome_msg = "नमस्कार! मी तुम्हाला सरकारी योजनांसाठी मदत करू शकतो. काय मदत हवी आहे?"
        self.voice.speak(welcome_msg)
        
        while True:
            user_input = self.voice.listen()
            
            if user_input is None:
                continue
            
            if 'बंद' in user_input or 'थांब' in user_input:
                goodbye_msg = "धन्यवाद! शुभेच्छा!"
                self.voice.speak(goodbye_msg)
                break
            
            # Agentic Loop: Plan -> Execute -> Evaluate
            plan = self.planner.plan(user_input, self.state)
            execution_results = self.executor.execute(plan, self.state)
            evaluation = self.evaluator.evaluate(execution_results, self.state, plan)
            
            # Update state
            self.state.phase = evaluation.get('nextPhase', 'gathering')
            
            if 'updatedProfile' in evaluation and evaluation['updatedProfile']:
                # Check for contradictions
                contradictions = self.memory.detect_contradictions(
                    evaluation['updatedProfile'],
                    self.state.user_profile
                )
                
                if contradictions:
                    cont = contradictions[0]
                    evaluation['response'] = f"माफ करा, तुम्ही आधी {cont['oldValue']} सांगितले होते, आता {cont['newValue']} सांगत आहात. कोणती माहिती बरोबर आहे?"
                
                self.state.user_profile.update(evaluation['updatedProfile'])
            
            if 'eligibleSchemes' in evaluation:
                self.state.eligible_schemes = evaluation['eligibleSchemes']
            
            if 'selectedScheme' in evaluation:
                self.state.selected_scheme = evaluation['selectedScheme']
            
            # Update memory
            response = evaluation.get('response', 'समजले नाही. पुन्हा सांगा.')
            self.memory.update_memory(self.state, user_input, response)
            
            # Speak response
            self.voice.speak(response)
            
            print(f"\nस्थिती: {self.state.phase}")
            print(f"प्रोफाइल: {self.state.user_profile}")
            print(f"पात्र योजना: {len(self.state.eligible_schemes)}")

if __name__ == "__main__":
    """
    Supported providers:
    1. groq - Fast inference with Llama, Mixtral, Gemma models
    2. ollama - Local models (requires Ollama running locally)
    3. openrouter - Access to multiple open-source models
    """
    
    # Configuration
    PROVIDER = os.environ.get('LLM_PROVIDER', 'groq')  # groq, ollama, openrouter
    API_KEY = '' # Replace with your actual API key
    
    # Model selection based on provider
    MODEL_CONFIG = {
        'groq': 'llama-3.3-70b-versatile',  # Fast and capable
        # Other options: 'mixtral-8x7b-32768', 'gemma2-9b-it'
        'ollama': 'llama3.2',  # Must be installed locally
        'openrouter': 'meta-llama/llama-3.1-70b-instruct'
    }
    
    MODEL = os.environ.get('LLM_MODEL', MODEL_CONFIG.get(PROVIDER, 'llama-3.3-70b-versatile'))
    
    print(f"Initializing with {PROVIDER} provider using {MODEL} model...")
    
    agent = MarathiVoiceAgent(PROVIDER, API_KEY, MODEL)
    agent.run()