"""
LLM Service module for Groq API integration
"""
import os
from typing import Dict, Optional
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
import json
import re


class LLMService:
    def __init__(self, api_key: Optional[str] = None, temperature: float = 0):
        """Initialize Groq LLM service"""
        self.api_key = api_key or os.getenv('GROQ_API')
        self.temperature = temperature
        
        if not self.api_key:
            raise ValueError("GROQ_API key not found in environment variables or parameters")
        
        self.llm = ChatGroq(
            api_key=self.api_key,
            model="llama-3.3-70b-versatile",
            temperature=temperature
        )
        
    def generate_outbreak_forecast(self, district_data: Dict) -> Dict:
        """
        Generate outbreak forecast using LLM
        
        Args:
            district_data: Dictionary containing malaria data from database
            
        Returns:
            Forecast data in JSON format
        """
        if not district_data or 'years' not in district_data or len(district_data['years']) == 0:
            return {
                "status": "no_outbreak_observed",
                "message": "No outbreak detected in this district. Maintain awareness of a healthy lifestyle.",
                "forecast": None
            }
        
        # Prepare the prompt for LLM
        prompt = self._prepare_prompt(district_data)
        
        try:
            # Call Groq LLM
            response = self.llm.invoke([HumanMessage(content=prompt)])
            response_text = response.content
            
            # Parse the response
            forecast_data = self._parse_response(response_text, district_data)
            return forecast_data
            
        except Exception as e:
            print(f"Error calling Groq LLM: {str(e)}")
            return {
                "status": "error",
                "message": f"Error generating forecast: {str(e)}",
                "forecast": None
            }
    
    def generate_response(self, prompt: str) -> str:
        """
        Generate a generic response from LLM for custom prompts
        
        Args:
            prompt: Custom prompt text
            
        Returns:
            Response text from LLM
        """
        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            return response.content
        except Exception as e:
            print(f"Error calling Groq LLM: {str(e)}")
            return f"Error generating response: {str(e)}"
    
    def _prepare_prompt(self, district_data: Dict) -> str:
        """Prepare prompt for LLM"""
        state = district_data.get('state', 'Unknown')
        district = district_data.get('district', 'Unknown')
        
        # Get the latest year data
        latest_data = district_data['years'][0] if district_data['years'] else {}
        
        prompt = f"""
Analyze the following malaria data for {district}, {state} and provide a forecast:

District: {district}
State: {state}
Latest Data:
- Total Cases Examined: {latest_data.get('cases_examined', 0)}
- Total Cases Detected: {latest_data.get('cases_detected', 0)}
- Male Cases Detected: {latest_data.get('male_case_detected', 0)}
- Female Cases Detected: {latest_data.get('female_case_detected', 0)}
- Year: {latest_data.get('year', 'Unknown')}

Historical Data (last 3-4 years):
"""
        
        for year_data in district_data['years'][:4]:
            prompt += f"\nYear {year_data['year']}: {year_data['cases_detected']} cases detected (Male: {year_data['male_case_detected']}, Female: {year_data['female_case_detected']})"
        
        prompt += """

Based on this data, provide a malaria outbreak forecast in JSON format with the following structure:
{
    "outbreak_status": "high_risk" | "moderate_risk" | "low_risk",
    "disease_name": "Malaria",
    "forecast_by_gender": {
        "male": <number>,
        "female": <number>
    },
    "forecast_by_age_group": {
        "children_0_5": <number>,
        "youth_5_18": <number>,
        "adults_18_60": <number>,
        "elderly_60_plus": <number>
    },
    "total_expected_cases": <number>,
    "confidence_level": 0-1,
    "recommendations": "<health awareness message>"
}

IMPORTANT: Return ONLY valid JSON, no additional text. The total_expected_cases should be based on the trend analysis.
"""
        return prompt
    
    def _parse_response(self, response_text: str, district_data: Dict) -> Dict:
        """Parse LLM response"""
        try:
            # Try to extract JSON from response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            
            if json_match:
                json_str = json_match.group(0)
                forecast_json = json.loads(json_str)
                
                return {
                    "status": "outbreak_detected",
                    "district": district_data.get('district'),
                    "state": district_data.get('state'),
                    "forecast": forecast_json
                }
            else:
                # If no JSON found, create a default forecast
                latest_data = district_data['years'][0] if district_data['years'] else {}
                detected = latest_data.get('cases_detected', 0)
                
                return {
                    "status": "outbreak_detected" if detected > 0 else "no_outbreak_observed",
                    "district": district_data.get('district'),
                    "state": district_data.get('state'),
                    "forecast": {
                        "outbreak_status": "high_risk" if detected > 100 else "moderate_risk" if detected > 20 else "low_risk",
                        "disease_name": "Malaria",
                        "total_expected_cases": int(detected * 1.1),  # 10% increase projection
                        "forecast_by_gender": {
                            "male": int(latest_data.get('male_case_detected', 0) * 1.1),
                            "female": int(latest_data.get('female_case_detected', 0) * 1.1)
                        },
                        "forecast_by_age_group": {
                            "children_0_5": int(detected * 0.15 * 1.1),
                            "youth_5_18": int(detected * 0.20 * 1.1),
                            "adults_18_60": int(detected * 0.50 * 1.1),
                            "elderly_60_plus": int(detected * 0.15 * 1.1)
                        },
                        "confidence_level": 0.75,
                        "recommendations": "Maintain awareness of a healthy lifestyle. Use mosquito nets, ensure proper sanitation, and seek medical attention if symptoms appear."
                    }
                }
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {str(e)}")
            return {
                "status": "error",
                "message": "Error parsing forecast response",
                "forecast": None
            }
