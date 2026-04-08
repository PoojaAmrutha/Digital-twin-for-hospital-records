import os
import json
import re
from typing import List, Dict, Any
import google.generativeai as genai
from difflib import get_close_matches
from dotenv import load_dotenv

# Load environment variables from backend/.env
import os
from pathlib import Path
env_path = Path(__file__).parent / '.env'
print(f"🔍 DEBUG: Looking for .env at: {env_path.absolute()}")
print(f"🔍 DEBUG: File exists: {env_path.exists()}")
load_dotenv(dotenv_path=env_path)
print(f"🔍 DEBUG: API Key after load_dotenv: {os.getenv('GEMINI_API_KEY')}")

# Common Medicines Database
COMMON_MEDICINES = [
    "Paracetamol", "Dolo", "Calpol", "Crocin",
    "Amoxicillin", "Augmentin", "Moxikind",
    "Azithromycin", "Azithral", "Cefixime", "Taxim", "Zifi", "Cefpodoxime", "Cepodem", "Cefoprox",
    "Cetirizine", "Cetzine", "Okacet", "Levocetirizine", "Levocet",
    "Pantoprazole", "Pan", "Pantocid", "Omeprazole", "Omez",
    "Metformin", "Glycomet", "Atorvastatin", "Atorva",
    "Aspirin", "Ecosprin", "Ibuprofen", "Brufen", "Combiflam",
    "Diclofenac", "Voveran", "Montelukast", "Montek",
    "Telmisartan", "Telma", "Amlodipine", "Amlong",
    "Metoprolol", "Metolar", "Thyroxine", "Thyronorm",
    "Multivitamin", "Becosules", "Zincovit", "Ebastine", "Ebast", "Ebast-M"
]

# Words to ignore for medicine matching (False Positives)
IGNORE_WORDS = {"name", "date", "sex", "age", "registrar", "hospital", "clinic", "dr", "doctor", "patient", "tablet", "capsule", "syrup"}

class LLMService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model = None
        self.vision_model = None
        self._setup_model()

    def _setup_model(self):
        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-pro-latest')
                self.vision_model = genai.GenerativeModel('gemini-flash-latest')
                print("✅ LLM Service: Gemini API Configured (Text & Vision)")
            except Exception as e:
                print(f"⚠️ LLM Service: Failed to configure Gemini: {e}")
        else:
            print("ℹ️  LLM Service: No API Key found. Using rule-based fallback.")

    def mask_phi(self, text: str) -> str:
        """
        Step 3 & 4: PHI Detection and Masking using Regex/NER
        """
        masked_text = text
        
        # Mask Phone Numbers (10 digits)
        masked_text = re.sub(r'\b\d{10}\b', '[PHONE-MASKED]', masked_text)
        
        # Mask Dates (Simple patterns)
        masked_text = re.sub(r'\d{1,2}[-/]\d{1,2}[-/]\d{2,4}', '[DATE-MASKED]', masked_text)
        
        # Mask Names (Heuristic: "Name" followed by words)
        # Matches "Name" or "Pt Name" followed by newline or colon, then captures the next line/words
        masked_text = re.sub(r'(?i)(name|patient)\s*[:\-\n.]+\s*([a-zA-Z\s]+)', r'\1: [NAME-MASKED]', masked_text)
        
        # Mask Age/Sex
        masked_text = re.sub(r'(?i)(age|sex)\s*[:\-\n.]+\s*(\w+)', r'\1: [MASKED]', masked_text)
        
        return masked_text

    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract clinical entities from text using LLM (primary) or Rules (fallback)
        """
        if not text:
            return []

        # Try LLM first
        if self.model:
            try:
                prompt = f"""
                You are a medical AI. Extract clinical entities from the text below.
                Return ONLY a valid JSON array of objects. 
                Each object must have: "type" (one of: diagnosis, symptom, medication), "value" (the text), and "confidence" (0.0 to 1.0).
                
                Text: "{text}"
                
                Example Output:
                [
                    {{"type": "symptom", "value": "chest pain", "confidence": 0.95}},
                    {{"type": "diagnosis", "value": "Asthma", "confidence": 0.9}}
                ]
                """
                
                response = self.model.generate_content(prompt)
                
                # Parse JSON from response
                json_str = response.text
                # Cleanup markdown code blocks if present
                if "```json" in json_str:
                    json_str = json_str.split("```json")[1].split("```")[0]
                elif "```" in json_str:
                    json_str = json_str.split("```")[1].split("```")[0]
                    
                entities = json.loads(json_str.strip())
                return entities
                
            except Exception as e:
                print(f"⚠️ LLM Error: {e}. Falling back to rules.")
        
        # Fallback to Rule-based
        return self._rule_based_extraction(text)

    def analyze_image(self, image_data: bytes) -> str:
        """
        Analyze medical image (prescription) using Gemini Vision
        """
        if self.vision_model and self.api_key:
            try:
                # Prepare image for Gemini
                import PIL.Image
                import io
                image = PIL.Image.open(io.BytesIO(image_data))
                
                prompt = """
                Analyze this medical prescription image accurately and professionally.
                
                Provide the results in a clean, easy-to-read list format (Avoid Markdown Tables):
                1. PATIENT INFORMATION: (Name, Weight, Vitals if visible)
                2. DOCTOR SPECIALTY: (e.g., ENT Specialist)
                3. PRESCRIBED MEDICATIONS: 
                   List each medication clearly:
                   - [Medicine Name]: [Dosage], [Instructions], [Duration]
                4. DIAGNOSIS: (Implied or stated condition)
                
                Rules:
                - Use plain bullet points and bold headers.
                - DO NOT use Markdown Tables (|---|).
                - DO NOT use horizontal lines (---).
                - Keep it simple, clear, and professional.
                """
                
                response = self.vision_model.generate_content([prompt, image])
                return response.text
            except Exception as e:
                error_msg = str(e)
                print(f"⚠️ Vision AI Error: {error_msg}")
                if "429" in error_msg:
                    return "❌ AI Quota Exceeded: The free tier has a limit. Please wait a minute or check your Google AI Studio quota."
                if "404" in error_msg:
                    return f"❌ AI Model Error: The vision model could not be found. (Error: {error_msg})"
                import traceback
                traceback.print_exc()
                return f"❌ AI Analysis Error: {error_msg}"
        
        # Fallback: Local OCR (EasyOCR) - No API Key required
        try:
            print("ℹ️ Attempting Local OCR with EasyOCR...")
            import easyocr
            import numpy as np
            from PIL import Image
            import io
            
            # Initialize reader (will download model once)
            reader = easyocr.Reader(['en'], gpu=False)
            
            # Convert bytes to image array
            image = Image.open(io.BytesIO(image_data))
            image_np = np.array(image)
            
            # Read text
            results = reader.readtext(image_np, detail=0)
            extracted_text = "\n".join(results)
            
            # Post-Process: Find Medicines and Context
            params_section = []
            
            lines = extracted_text.split('\n')
            for line in lines:
                # Clean line for matching but keep original for display (context)
                cleaned_line_tokens = re.sub(r'[^a-zA-Z\s]', ' ', line).split()
                
                line_meds = []
                for word in cleaned_line_tokens:
                    if len(word) < 4 or word.lower() in IGNORE_WORDS: continue
                    matches = get_close_matches(word, COMMON_MEDICINES, n=1, cutoff=0.45)
                    if matches:
                        line_meds.append(matches[0])
                
                # If this line has a medicine, add it to output
                if line_meds:
                    # Deduplicate meds in this line
                    line_meds = list(set(line_meds))
                    med_names = ", ".join(line_meds)
                    
                    # Try to clean up the line to show meaningful context (dosage)
                    # We keep numbers and simple chars
                    context = re.sub(r'[^a-zA-Z0-9\s\-\.\/]', '', line).strip()
                    params_section.append(f"• {med_names}  (Context: {context})")

            final_output = "No medicines detected. Please try a clearer image."
            if params_section:
                final_output = "💊 DETECTED PRESCRIPTION (Tablets & Dosage):\n\n" + "\n\n".join(params_section)
                final_output += "\n\n(Note: Context text shows the raw OCR line for dosage verification)"
            
            return final_output
        except Exception as e:
            print(f"⚠️ Local OCR Error: {e}")
            pass

        # Final Fallback Simulation if everything fails
        return None

    def analyze_prescription(self, image_data: bytes) -> Dict[str, Any]:
        """
        Analyze medical prescription image and return structured data
        """
        if self.vision_model and self.api_key:
            try:
                # Prepare image for Gemini
                import PIL.Image
                import io
                image = PIL.Image.open(io.BytesIO(image_data))
                
                prompt = """
                Analyze this medical prescription image and extract the following details in valid JSON format.
                
                Required JSON Structure:
                {
                    "patient_name": "Name or null",
                    "doctor_name": "Name or null",
                    "diagnosis": "Condition or null",
                    "medications": [
                        {
                            "name": "Medicine Name",
                            "dosage": "e.g. 500mg",
                            "frequency": "e.g. twice daily",
                            "duration": "e.g. 5 days",
                            "instructions": "e.g. after food"
                        }
                    ],
                    "advice": "Any other instructions or advice"
                }
                
                Rules:
                - Return ONLY the JSON object.
                - Do not include markdown formatting like ```json ... ```.
                - If a field is not visible, use null.
                """
                
                response = self.vision_model.generate_content([prompt, image])
                txt = response.text.strip()
                
                # Cleanup markdown code blocks if present
                if "```json" in txt:
                    txt = txt.split("```json")[1].split("```")[0]
                elif "```" in txt:
                    txt = txt.split("```")[1].split("```")[0]
                
                return json.loads(txt)
            except Exception as e:
                print(f"⚠️ Vision AI Structured Error: {e}")
                pass # Fallback to simulation
        
        # Fallback Simulation
        return {
            "patient_name": "Unknown Patient",
            "doctor_name": "Unknown Doctor",
            "diagnosis": "Viral Infection (Simulated)",
            "medications": [
                {
                    "name": "Amoxicillin",
                    "dosage": "500mg",
                    "frequency": "Every 8 hours",
                    "duration": "5 days",
                    "instructions": "Take after food"
                },
                {
                    "name": "Paracetamol",
                    "dosage": "650mg",
                    "frequency": "SOS",
                    "duration": "3 days",
                    "instructions": "For fever > 100F"
                }
            ],
            "advice": "Drink plenty of water and rest."
        }

    def _rule_based_extraction(self, text: str) -> List[Dict[str, Any]]:
        """Fallback extraction using Regex/Keywords"""
        entities = []
        text_lower = text.lower()
        
        # Common Symptoms
        symptoms = ['fever', 'headache', 'pain', 'cough', 'fatigue', 'nausea', 'dizzy', 'anxiety']
        for s in symptoms:
            if s in text_lower:
                entities.append({"type": "symptom", "value": s, "confidence": 0.7})
                
        # Common Diagnoses
        diagnoses = ['diabetes', 'hypertension', 'asthma', 'cancer', 'flu', 'covid', 'arthritis']
        for d in diagnoses:
            if d in text_lower:
                entities.append({"type": "diagnosis", "value": d.capitalize(), "confidence": 0.8})
                
        # Common Meds
        meds = ['aspirin', 'metformin', 'lisinopril', 'ibuprofen', 'insulin', 'antibiotics']
        for m in meds:
            if m in text_lower:
                entities.append({"type": "medication", "value": m.capitalize(), "confidence": 0.8})
                
        return entities

    def normalize_terms(self, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Normalize terms (Mock)"""
        return entities
        
    def resolve_ambiguity(self, text: str) -> str:
        """Resolve ambiguity (Mock)"""
        return text

# Singleton instance
llm_service = LLMService()
