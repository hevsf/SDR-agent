import os
from firecrawl import FirecrawlApp
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class SDRScout:
    def __init__(self):
        # Initialize Firecrawl for high-quality web scraping
        self.firecrawl = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))
        
        # Initialize DeepSeek API 
        self.ai = OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"), 
            base_url="https://api.deepseek.com"
        )

    def scrape_website(self, url: str) -> str:
        """
        Extracts content from the target URL and converts it to clean Markdown.
        """
        print(f"[*] Intelligence Gathering: Accessing {url}...")
        try:
            # We add a try-except specifically for the API call to see the error
            scrape_result = self.firecrawl.scrape_url(url, params={'formats': ['markdown']})
            
            if scrape_result is None:
                return "Error: Firecrawl returned None. Check your API key and balance."
            
            return scrape_result.get('markdown', "")
            
        except Exception as e:
            # This will now tell us if it's a 401 (Unauthorized) or 402 (Payment Required)
            error_msg = f"Error during scraping: {str(e)}"
            print(f"[!] {error_msg}")
            return error_msg

    def analyze_business_model(self, markdown_content: str) -> str:
        #Uses DeepSeek to analyze the business and identify automation opportunities.
        print("[*] Analysis Engine: Identifying business pain points...")
        
        system_prompt = """
        You are a Senior Sales Strategist. Analyze the provided website content to build a prospect profile.
        Focus on identifying high-friction manual processes that can be automated with AI.
        
        Your output must be a valid JSON object with the following structure:
        {
          "company_name": "Name of the entity",
          "core_services": "Brief description of what they sell",
          "target_audience": "Who are their customers?",
          "identified_inefficiencies": ["List of manual tasks like lead gen, support, scheduling"],
          "krykos_automation_hypothesis": "A specific pitch on how an AI Agent can save them 10+ hours/week"
        }
        
        Keep descriptions concise and professional. Use English only.
        """
        
        try:
            response = self.ai.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Website Content:\n{markdown_content[:8000]}"}
                ],
                response_format={'type': 'json_object'}
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error during analysis: {str(e)}"