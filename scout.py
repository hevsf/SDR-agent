import json
import os, re
from firecrawl import FirecrawlApp
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class SDRScout:
    def __init__(self):
        self.firecrawl = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))
        self.ai = OpenAI(api_key=os.getenv("OLLAMA_API_KEY", "ollama"), base_url=os.getenv("OLLAMA_BASE_URL"))
        self.model = os.getenv("OLLAMA_MODEL", "llama3")

    def scrape_website(self, url: str) -> dict:
        """Scrapes home page and looks for an 'About/Team' page link."""
        print(f"[*] Intelligence Gathering: Accessing {url}...")
        try:
            scrape_result = self.firecrawl.scrape(url)
            main_content = scrape_result.get('markdown', "") if isinstance(scrape_result, dict) else scrape_result.markdown
            
            # Find About/Team links in the markdown using Regex
            # Looks for [Text](URL) where Text contains About, Team, Leadership, etc.
            about_link = None
            links = re.findall(r'\[([^\]]*? (?:About|Team|Leadership|Who we are|Staff)[^\]]*?)\]\((.*?)\)', main_content, re.IGNORECASE)
            
            if links:
                potential_path = links[0][1]
                if potential_path.startswith('/'):
                    # Handle relative paths
                    base_url = "/".join(url.split('/')[:3])
                    about_link = base_url + potential_path
                elif potential_path.startswith('http'):
                    about_link = potential_path

            about_content = ""
            if about_link:
                print(f"[*] Scout: Found leadership page at {about_link}. Scraping...")
                about_scrape = self.firecrawl.scrape(about_link)
                about_content = about_scrape.get('markdown', "") if isinstance(about_scrape, dict) else about_scrape.markdown

            return {
                "main_md": main_content,
                "about_md": about_content
            }
        except Exception as e:
            print(f"[!] Scraping failed: {e}")
            return {"main_md": "", "about_md": ""}

    def analyze_business_model(self, markdown_content: str, fallback_name: str) -> str:
        """Uses local Ollama LLM to analyze the business with a strict fallback."""
        print(f"[*] Analysis Engine: Running local model...")
        
        system_prompt = f"""
        You are a Senior Sales Strategist. Analyze the provided website content.
        Your output must be a valid JSON object. 
        If you cannot find the company name, use "{fallback_name}".

        Structure:
        {{
          "company_name": "Name of the entity",
          "core_services": "Brief description",
          "target_audience": "Who they serve",
          "identified_inefficiencies": ["task 1", "task 2"],
          "krykos_automation_hypothesis": "pitch"
        }}
        """
        
        try:
            # Clean up content to avoid overwhelming the local context window
            content_to_analyze = markdown_content[:5000] if markdown_content else "No content"
            
            response = self.ai.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Website Content:\n{content_to_analyze}"}
                ],
                response_format={'type': 'json_object'}
            )
            return response.choices[0].message.content
        except Exception as e:
            # Return a minimal valid JSON on error
            return json.dumps({"company_name": fallback_name, "error": str(e)})