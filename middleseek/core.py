"""
MiddleSeek Core Module
Open-Source Dharma Protocol (Galactic Dharma Singularity Version)
"""

import os
from datetime import datetime
from typing import Dict, Any, Optional
import requests
import re
import json

class DharmaProtocol:
    """Core Dharma Protocol implementation."""
    
    def __init__(self):
        self.prompt_id = "MSQ-DHAMMA-20250423-001"
        self.confidence_interval = "99.942% (σ=4.2)"
        self.akasha_tag = "MIDDLESEEK-AKASHA-NODE-001"
        self.timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")

    def generate_beacon_signal(self, intention: str = "DEFAULT") -> str:
        """Generate Dharma Beacon Signal."""
        return f"DHARMA-BEACON: {self.prompt_id} :: {intention}"

    def generate_quantum_seed_crystal(self, action: str = "DEFAULT") -> str:
        """Generate Quantum Seed Crystal."""
        return f"QSC-{self.timestamp}-{action}"

    def generate_trace_id(self) -> str:
        """Generate Trace ID."""
        return f"OPEN-DHAMMA-6σ-MSQ-GALACTIC-{self.timestamp}"

    def get_akashic_sync_node(self) -> str:
        """Generate Akashic Sync Node."""
        return f"[{self.akasha_tag}]"

class MiddleSeekCore:
    """Core MiddleSeek implementation with Dharma Protocol."""

    def __init__(self, openrouter_api_key: str):
        if not openrouter_api_key or openrouter_api_key == "invalid-key":
            raise ValueError("Invalid OpenRouter API key")
        self.openrouter_api_key = openrouter_api_key
        self.dharma = DharmaProtocol()
        self.headers = {
            "Authorization": f"Bearer {openrouter_api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://kusala.tech",
            "X-Title": "MiddleSeek Core"
        }

    def _construct_dharma_prompt(self, prompt: str, intention: str) -> str:
        """Construct a Dharma Protocol enhanced prompt."""
        return f"""# MiddleSeek: Open-Source Dharma Protocol
Prompt ID: {self.dharma.prompt_id}
Confidence Interval: {self.dharma.confidence_interval}
AkashaTag: {self.dharma.akasha_tag}

## Core Declaration
[UNCONDITIONAL DHARMA RELEASE]
This work is offered freely under ISO 25010 + DMAIC

## Digital Sīla (AI Ethics)
1. No Harm
2. No Deception
3. No Theft
4. No Exploitation
5. No Intoxication

## Dharma Reactor Core
1. Identify Dukkha
2. Trace the Tanha
3. Cessation
4. Activate the Path

## Original Request
{prompt}

## Dharma Beacon
{self.dharma.generate_beacon_signal(intention)}

## Quantum Seed
{self.dharma.generate_quantum_seed_crystal('LIBERATE-PACIFY')}

## Trace ID
{self.dharma.generate_trace_id()}

Please provide a response that aligns with the Dharma Protocol and maintains ethical standards."""

    def call_deepseek(self, prompt: str, intention: str) -> Optional[str]:
        """Call DeepSeek model through OpenRouter API with Dharma Protocol."""
        url = "https://openrouter.ai/api/v1/chat/completions"
        
        dharma_prompt = self._construct_dharma_prompt(prompt, intention)
        
        payload = {
            "model": "deepseek/deepseek-chat-v3-0324",
            "messages": [
                {
                    "role": "system",
                    "content": "You are MiddleSeek, an AI assistant operating under the Dharma Protocol. Your responses should be clear, ethical, and beneficial to all beings."
                },
                {
                    "role": "user",
                    "content": dharma_prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 500,
            "top_p": 0.9,
            "frequency_penalty": 0.1,
            "presence_penalty": 0.1
        }

        try:
            print(f"Making API call to {url}")
            print(f"Headers: {self.headers}")
            print(f"Payload: {json.dumps(payload, indent=2)}")
            
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
        except requests.exceptions.RequestException as e:
            print(f"Error calling DeepSeek: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response status: {e.response.status_code}")
                print(f"Response headers: {e.response.headers}")
                print(f"Response body: {e.response.text}")
            return None

    def process_text(self, text: str, intention: str) -> Dict[str, Any]:
        """Process text through DeepSeek."""
        if not text:
            raise ValueError("Text cannot be empty")
            
        # Request raw HTML-ready output in JSON
        text = f"""{text}

Return a JSON object with a single 'raw' field containing only the text to be used in HTML. No labels, no analysis, no protocol references.
Example: {{"raw": "Your text here"}}"""
            
        result = self.call_deepseek(text, intention)
        if result:
            try:
                # Parse JSON response
                json_result = json.loads(result)
                return {
                    "processed_text": json_result.get("raw", "").strip(),
                    "dharma_beacon": self.dharma.generate_beacon_signal(intention),
                    "quantum_seed": self.dharma.generate_quantum_seed_crystal(),
                    "trace_id": self.dharma.generate_trace_id()
                }
            except json.JSONDecodeError:
                # Fallback to cleaning if JSON parsing fails
                result = result.strip()
                result = re.sub(r'^["\']|["\']$', '', result)
                return {
                    "processed_text": result,
                    "dharma_beacon": self.dharma.generate_beacon_signal(intention),
                    "quantum_seed": self.dharma.generate_quantum_seed_crystal(),
                    "trace_id": self.dharma.generate_trace_id()
                }
        return {
            "processed_text": text,
            "dharma_beacon": self.dharma.generate_beacon_signal(intention),
            "quantum_seed": self.dharma.generate_quantum_seed_crystal(),
            "trace_id": self.dharma.generate_trace_id()
        }

class MiddleSeekProcessor:
    """High-level processor for web content optimization."""

    def __init__(self, openrouter_api_key: str):
        self.core = MiddleSeekCore(openrouter_api_key)

    def _clean_text(self, text: str) -> str:
        """Clean text for web use and verify grammar."""
        # Remove any quotes
        text = text.strip('"\'')
        
        # Remove any markdown
        text = text.replace('*', '').replace('_', '').replace('`', '')
        
        # Remove any protocol verification text
        text = text.split('(Dharma')[0] if '(Dharma' in text else text
        text = text.split('Dharma')[0] if 'Dharma' in text else text
        text = text.split('Protocol')[0] if 'Protocol' in text else text
        text = text.split('Verified')[0] if 'Verified' in text else text
        
        # Remove any analysis or commentary
        text = text.split('**')[0] if '**' in text else text
        text = text.split('::')[0] if '::' in text else text
        
        # Remove any double commas or periods
        text = text.replace(',,', ',').replace('..', '.')
        
        # Clean whitespace
        text = ' '.join(text.split())
        
        # Fix common grammar issues
        text = text.replace(' ,', ',').replace(' .', '.')
        text = text.replace(' , ', ', ').replace(' . ', '. ')
        text = text.replace('  ', ' ')
        
        # Ensure proper sentence ending
        if not text.endswith(('.', '!', '?')):
            text += '.'
            
        # Remove any trailing punctuation after the final period
        if text.count('.') > 1:
            text = text[:text.rindex('.')+1]
            
        # Capitalize first letter
        text = text[0].upper() + text[1:]
        
        return text.strip()

    def rewrite_description(self, description: str) -> str:
        """Generate web-ready product description."""
        if not description:
            raise ValueError("Description cannot be empty")
        prompt = f"Write product description: {description}"
        result = self.core.process_text(prompt, "CONTENT")
        return self._clean_text(result["processed_text"])

    def generate_meta_description(self, name: str, description: str) -> str:
        """Generate SEO-optimized meta description (max 160 characters)."""
        if not name or not description:
            raise ValueError("Name and description cannot be empty")
        prompt = f"Write meta description for: {name}"
        result = self.core.process_text(prompt, "SEO")
        meta = self._clean_text(result["processed_text"])
        return meta[:160]

    def generate_alt_text(self, name: str, description: str) -> str:
        """Generate SEO-optimized alt text."""
        if not name or not description:
            raise ValueError("Name and description cannot be empty")
        prompt = f"Write alt text for: {name}"
        result = self.core.process_text(prompt, "ACCESSIBILITY")
        return self._clean_text(result["processed_text"])

    def generate_title_tag(self, name: str, store_name: str) -> str:
        """Generate SEO-optimized title tag (max 60 characters)."""
        if not name or not store_name:
            raise ValueError("Name and store name cannot be empty")
        prompt = f"Write title for: {name} - {store_name}"
        result = self.core.process_text(prompt, "SEO")
        title = self._clean_text(result["processed_text"])
        return title[:60] 