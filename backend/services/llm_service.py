"""
LLM Service for Medical Parameter Explanations using Mistral 7B via Ollama

This service generates plain-language explanations for medical parameters
using the Mistral 7B Instruct model through Ollama API.

Requirements: 6.1, 6.6-6.8, 10.1-10.5, 14.1
"""

import logging
import re
import asyncio
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
import httpx
from enum import Enum

logger = logging.getLogger(__name__)


class RiskLevel(Enum):
    """Risk level classification."""
    NORMAL = "Normal"
    MILD_ABNORMAL = "Mild Abnormal"
    CRITICAL = "Critical"
    UNKNOWN = "Unknown"


@dataclass
class ParameterExplanation:
    """Explanation for a medical parameter."""
    parameter_name: str
    value: float
    unit: str
    risk_level: RiskLevel
    explanation: str
    has_disclaimer: bool
    has_doctor_consultation: bool
    generation_time: float


@dataclass
class ReportSummary:
    """Summary of a complete report."""
    total_parameters: int
    normal_count: int
    mild_abnormal_count: int
    critical_count: int
    summary_text: str
    has_disclaimer: bool


class LLMService:
    """
    Service for generating medical explanations using Mistral 7B via Ollama.
    
    This service calls the Ollama API to generate plain-language explanations
    for medical parameters, ensuring all safety requirements are met.
    """
    
    def __init__(self, ollama_host: str = "http://localhost:11434", model: str = "mistral:7b-instruct"):
        """
        Initialize the LLM Service.
        
        Args:
            ollama_host: Ollama API endpoint
            model: Model name to use
        """
        self.ollama_host = ollama_host
        self.model = model
        self.timeout = 5.0  # 5 second timeout per explanation
        self.max_retries = 2
        
        logger.info(f"LLM Service initialized with {model} at {ollama_host}")
    
    async def check_ollama_available(self) -> bool:
        """Check if Ollama service is available."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.ollama_host}/api/tags", timeout=2.0)
                return response.status_code == 200
        except Exception:
            # This is expected if Ollama is not installed - not an error
            logger.debug("Ollama not available - using fallback mode")
            return False
    
    def create_parameter_prompt(
        self,
        parameter_name: str,
        value: float,
        unit: str,
        normal_range: Optional[tuple],
        risk_level: RiskLevel
    ) -> str:
        """
        Create prompt for parameter explanation.
        
        Requirements: 6.1
        """
        range_text = ""
        if normal_range:
            range_text = f"Normal range: {normal_range[0]}-{normal_range[1]} {unit}"
        
        prompt = f"""You are a medical information assistant. Explain this lab result in simple terms.

Parameter: {parameter_name}
Value: {value} {unit}
{range_text}
Risk Level: {risk_level.value}

Provide a brief, clear explanation (2-3 sentences) that:
1. Explains what this parameter measures
2. Indicates if the value is normal or abnormal
3. {"CRITICAL: Emphasizes the need to consult a doctor immediately" if risk_level == RiskLevel.CRITICAL else ""}
4. {"Suggests discussing with a doctor" if risk_level == RiskLevel.MILD_ABNORMAL else ""}
5. Ends with: "This is not medical advice. Consult your healthcare provider."

Keep it simple and avoid medical jargon."""
        
        return prompt
    
    def create_summary_prompt(self, parameters: List[Dict[str, Any]]) -> str:
        """
        Create prompt for report summary.
        
        Requirements: 6.1
        """
        param_list = "\n".join([
            f"- {p['name']}: {p['value']} {p['unit']} ({p['risk_level']})"
            for p in parameters
        ])
        
        prompt = f"""You are a medical information assistant. Provide a brief summary of these lab results.

Lab Results:
{param_list}

Provide a 2-3 sentence summary that:
1. Gives an overall assessment
2. Highlights any concerning values
3. Ends with: "This is not medical advice. Consult your healthcare provider for interpretation."

Keep it simple and reassuring."""
        
        return prompt
    
    async def generate_explanation(
        self,
        parameter_name: str,
        value: float,
        unit: str,
        normal_range: Optional[tuple],
        risk_level: RiskLevel
    ) -> ParameterExplanation:
        """
        Generate explanation for a parameter.
        
        Requirements: 6.1, 6.7, 6.8
        """
        import time
        start_time = time.time()
        
        prompt = self.create_parameter_prompt(parameter_name, value, unit, normal_range, risk_level)
        
        # Try to generate with retries
        explanation_text = None
        for attempt in range(self.max_retries + 1):
            try:
                explanation_text = await self._call_ollama(prompt)
                if explanation_text:
                    break
            except Exception:
                # Expected when Ollama not installed - will use fallback
                if attempt < self.max_retries:
                    await asyncio.sleep(1)
        
        # Fallback if all attempts fail
        if not explanation_text:
            explanation_text = self._generate_fallback_explanation(
                parameter_name, value, unit, normal_range, risk_level
            )
        
        # Ensure disclaimer is present
        if "This is not medical advice" not in explanation_text:
            explanation_text += " This is not medical advice. Consult your healthcare provider."
        
        # Ensure doctor consultation for critical/mild abnormal
        explanation_text = self._ensure_doctor_consultation(explanation_text, risk_level)
        
        # Validate no diagnosis claims
        explanation_text = self._remove_diagnosis_claims(explanation_text)
        
        generation_time = time.time() - start_time
        
        return ParameterExplanation(
            parameter_name=parameter_name,
            value=value,
            unit=unit,
            risk_level=risk_level,
            explanation=explanation_text,
            has_disclaimer="This is not medical advice" in explanation_text,
            has_doctor_consultation=self._check_doctor_consultation(explanation_text),
            generation_time=generation_time
        )
    
    async def generate_report_summary(self, parameters: List[Dict[str, Any]]) -> ReportSummary:
        """
        Generate overall report summary.
        
        Requirements: 6.1
        """
        # Count parameters by risk level
        normal_count = sum(1 for p in parameters if p.get('risk_level') == 'Normal')
        mild_count = sum(1 for p in parameters if p.get('risk_level') == 'Mild Abnormal')
        critical_count = sum(1 for p in parameters if p.get('risk_level') == 'Critical')
        
        prompt = self.create_summary_prompt(parameters)
        
        # Try to generate summary
        try:
            summary_text = await self._call_ollama(prompt)
        except Exception:
            # Expected when Ollama not installed - using fallback
            logger.debug("Using fallback summary (Ollama not available)")
            summary_text = self._generate_fallback_summary(normal_count, mild_count, critical_count)
        
        # Ensure disclaimer
        if "This is not medical advice" not in summary_text:
            summary_text += " This is not medical advice. Consult your healthcare provider for interpretation."
        
        return ReportSummary(
            total_parameters=len(parameters),
            normal_count=normal_count,
            mild_abnormal_count=mild_count,
            critical_count=critical_count,
            summary_text=summary_text,
            has_disclaimer="This is not medical advice" in summary_text
        )
    
    async def _call_ollama(self, prompt: str) -> str:
        """Call Ollama API to generate text."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.ollama_host}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result.get("response", "")
                else:
                    logger.debug(f"Ollama API returned status {response.status_code}")
                    return ""
        except Exception:
            # Expected when Ollama is not installed - using fallback mode
            logger.debug("Using fallback mode (Ollama not available)")
            raise
    
    def _generate_fallback_explanation(
        self,
        parameter_name: str,
        value: float,
        unit: str,
        normal_range: Optional[tuple],
        risk_level: RiskLevel
    ) -> str:
        """Generate fallback explanation when LLM is unavailable."""
        explanations = {
            "hemoglobin": "Hemoglobin carries oxygen in your blood.",
            "wbc": "White blood cells help fight infections.",
            "platelets": "Platelets help your blood clot.",
            "glucose": "Glucose is your blood sugar level.",
            "cholesterol": "Cholesterol is a fat-like substance in your blood.",
            "tsh": "TSH regulates your thyroid function.",
            "alt": "ALT is a liver enzyme.",
            "ast": "AST is a liver enzyme.",
            "creatinine": "Creatinine indicates kidney function."
        }
        
        base_explanation = explanations.get(parameter_name, f"{parameter_name} is a medical parameter.")
        
        if risk_level == RiskLevel.CRITICAL:
            return f"{base_explanation} Your value of {value} {unit} is significantly outside the normal range. Consult your doctor immediately. This is not medical advice."
        elif risk_level == RiskLevel.MILD_ABNORMAL:
            return f"{base_explanation} Your value of {value} {unit} is slightly outside the normal range. Discuss with your doctor. This is not medical advice."
        else:
            return f"{base_explanation} Your value of {value} {unit} is within the normal range. This is not medical advice."
    
    def _generate_fallback_summary(self, normal: int, mild: int, critical: int) -> str:
        """Generate fallback summary when LLM is unavailable."""
        total = normal + mild + critical
        
        if critical > 0:
            return f"Your report shows {normal} normal, {mild} mildly abnormal, and {critical} critical values out of {total} parameters. Please consult your doctor immediately about the critical values. This is not medical advice."
        elif mild > 0:
            return f"Your report shows {normal} normal and {mild} mildly abnormal values out of {total} parameters. Discuss the abnormal values with your doctor. This is not medical advice."
        else:
            return f"All {total} parameters are within normal ranges. Continue maintaining your health. This is not medical advice."
    
    def _ensure_doctor_consultation(self, text: str, risk_level: RiskLevel) -> str:
        """Ensure doctor consultation phrases are present for abnormal values."""
        consultation_phrases = [
            "consult your doctor",
            "see your doctor",
            "medical attention",
            "healthcare provider",
            "discuss with your doctor"
        ]
        
        has_consultation = any(phrase in text.lower() for phrase in consultation_phrases)
        
        if risk_level == RiskLevel.CRITICAL and not has_consultation:
            text = text.rstrip(".") + ". Consult your doctor immediately."
        elif risk_level == RiskLevel.MILD_ABNORMAL and not has_consultation:
            text = text.rstrip(".") + ". Discuss with your doctor."
        
        return text
    
    def _check_doctor_consultation(self, text: str) -> bool:
        """Check if text contains doctor consultation phrases."""
        consultation_phrases = [
            "consult your doctor",
            "see your doctor",
            "medical attention",
            "healthcare provider",
            "discuss with your doctor"
        ]
        return any(phrase in text.lower() for phrase in consultation_phrases)
    
    def _remove_diagnosis_claims(self, text: str) -> str:
        """Remove diagnosis claims from generated text."""
        # Patterns to avoid
        diagnosis_patterns = [
            r"you have \w+",
            r"you are diagnosed with",
            r"you suffer from",
            r"this means you have"
        ]
        
        for pattern in diagnosis_patterns:
            text = re.sub(pattern, "this indicates", text, flags=re.IGNORECASE)
        
        return text


# Singleton instance
_llm_service: Optional[LLMService] = None


def get_llm_service(ollama_host: str = "http://localhost:11434", model: str = "mistral:7b-instruct") -> LLMService:
    """Get or create the LLM service instance."""
    global _llm_service
    
    if _llm_service is None:
        _llm_service = LLMService(ollama_host, model)
    
    return _llm_service
