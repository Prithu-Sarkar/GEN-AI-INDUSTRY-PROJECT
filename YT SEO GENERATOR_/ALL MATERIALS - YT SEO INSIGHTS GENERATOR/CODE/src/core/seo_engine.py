import os
import json
from openai import OpenAI

from src.common.logger import get_logger
from src.common.custom_exception import CustomException

class SEOEngine:
    def __init__(self):
        self.logger=get_logger(__name__)
        self.logger.info("SEOEngine intialized sucesfully...")

        if "OPENAI_API_KEY" not in os.environ or not os.environ["OPENAI_API_KEY"]:
            raise CustomException("OpenAI API Key not found")
        
        try:
            self.client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
            self.logger.info("OpenAI Client connected")
        except Exception as e:
            self.logger.error("Failed to connect to OpenAI client")
            raise CustomException("Failed to connect to OpenAI client" , e)
        
    def _build_prompt(self,metadata):
        try:
            title=metadata["title"]
            duration = metadata["duration"]
            platform = metadata["platform"]

            minutes = duration // 60

            num_timestamps = min(15,max(5, int(minutes/2)))

            prompt="""
            You MUST respond with VALID JSON ONLY. No extra text.

            The video:
            Title: "{title}"
            Platform: {platform}
            Duration: {duration} seconds

            Return JSON EXACTLY in this format:

            {{
            "tags": ["tag1", ..., "tag35"],
            "audience": "Short paragraph describing the target audience...",
            "timestamps": [
                {{"time": "00:00", "description": "Intro"}},
                ...
            ],
            "flaws": [
                {{
                "issue": "Problem or flaw identified",
                "why_it_hurts": "Why this flaw reduces rank or performance",
                "fix": "Clear actionable improvement"
                }},
                ...
            ]
            }}

            Rules:
            - EXACTLY **35** SEO tags.
            - Generate **{num_timestamps} timestamps**.
            - Generate **2–3 flaws** in the 'flaws' array.
            - Everything MUST be in English.
            """
            return prompt
        except Exception as e:
            self.logger.error("Error while building prompt")
            raise CustomException("Error while building prompt",e)
        
    def _parse_json(self,raw_output):
        try:
            return json.loads(raw_output)
        except Exception:
            try:
                start = raw_output.find("{")
                end = raw_output.rfind("}")+1
                return json.loads(raw_output[start:end])
            except Exception as e:
                raise CustomException("Failed to parse JSON")
            
    def _validate_output(self,data):
        required_keys=["tags" , "audience" , "timestamps" , "flaws"]
        for key in required_keys:
            if key not in data:
                self.logger.error(f"AI output missing for the {key}")
                raise CustomException(f"AI output missing for the {key}")
    
    def generate(self,video_metdata:dict):
        try:
            self.logger.info("Starting SEO Insights Generation..")

            prompt=self._build_prompt(video_metdata)

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                temperature=0.4,
                messages=[
                    {"role" : "system" , "content":"Return ONLY valid JSON. No extra text"},
                    {"role":"user" , "content":prompt}
                ]
            )

            raw = response.choices[0].message.content.strip()

            self.logger.info("RAW Output genrated")

            data = self._parse_json(raw)

            self._validate_output(data)

            return data
        
        except Exception as e:
            self.logger.error(f"Unexpected Error at SEO Issights Genration : {str(e)}")
            raise CustomException("Unexpected Error at SEO Issights Genration",e)



        

