from groq import Groq
from AgentUtil import AgentLogger

class LLMProvider:
    """Abstraction layer for different LLM providers"""
    def __init__(self, provider: str, api_key: str, model: str, logger: AgentLogger):
        self.provider = provider
        self.api_key = api_key
        self.model = model
        self.logger = logger
        self.client = None
        
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the appropriate client based on provider"""
        if self.provider == "groq":
            self.client = Groq(api_key=self.api_key)
        elif self.provider == "ollama":
            # For Ollama, we'll use requests directly
            import requests
            self.base_url = "http://localhost:11434"
        elif self.provider == "openrouter":
            # OpenRouter uses OpenAI-compatible API
            from openai import OpenAI
            self.client = OpenAI(
                api_key=self.api_key,
                base_url="https://openrouter.ai/api/v1"
            )
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
    
    def generate(self, system_prompt: str, user_message: str, max_tokens: int = 1000) -> str:
        """Generate response from LLM"""
        try:
            if self.provider == "groq":
                return self._groq_generate(system_prompt, user_message, max_tokens)
            elif self.provider == "ollama":
                return self._ollama_generate(system_prompt, user_message, max_tokens)
            elif self.provider == "openrouter":
                return self._openrouter_generate(system_prompt, user_message, max_tokens)
        except Exception as e:
            self.logger.log('error', f"LLM generation error: {str(e)}")
            raise
    
    def _groq_generate(self, system_prompt: str, user_message: str, max_tokens: int) -> str:
        """Groq API call"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            max_tokens=max_tokens,
            temperature=0.7
        )
        return response.choices[0].message.content
    
    def _ollama_generate(self, system_prompt: str, user_message: str, max_tokens: int) -> str:
        """Ollama API call (local)"""
        import requests
        
        response = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": f"{system_prompt}\n\n{user_message}",
                "stream": False,
                "options": {
                    "num_predict": max_tokens
                }
            }
        )
        return response.json()["response"]
    
    def _openrouter_generate(self, system_prompt: str, user_message: str, max_tokens: int) -> str:
        """OpenRouter API call"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            max_tokens=max_tokens
        )
        return response.choices[0].message.content