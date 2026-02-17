import os, json, time
from duckduckgo_search import DDGS
from openai import OpenAI

class IdentityHunter:
    def __init__(self):
        self.ai = OpenAI(api_key=os.getenv("OLLAMA_API_KEY", "ollama"), base_url=os.getenv("OLLAMA_BASE_URL"))
        self.model = os.getenv("OLLAMA_MODEL", "llama3")

    def find_decision_maker(self, company_name, site_context):
        """Uses site text to find a name, then searches the web to find socials."""
        print(f"[*] Identity Hunter: Looking for names inside {company_name}'s website...")
        
        # Step 1: Extract names from the 'About/Team' text
        extract_prompt = f"""
        Analyze this website text from {company_name}. Find the Full Name and Title of the Founder, CEO, or Owner.
        Text: {site_context[:5000]}
        Return JSON: {{"name": "Name or null", "title": "Title or null"}}
        """
        
        name_on_site = "null"
        try:
            res = self.ai.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": extract_prompt}],
                response_format={'type': 'json_object'}
            )
            data = json.loads(res.choices[0].message.content)
            name_on_site = data.get("name")
        except: pass

        # Step 2: Search the web with the name (if found) or the company
        if name_on_site and name_on_site != "null":
            print(f"[*] Hunter: Verifying socials for {name_on_site}...")
            query = f'"{name_on_site}" {company_name} LinkedIn X'
        else:
            print(f"[*] Hunter: No name on site. Searching web for {company_name} leadership...")
            query = f"{company_name} Founder CEO owner LinkedIn -NHL -Sports -Hockey" # Added negative filters!

        # Step 3: Use DDGS with HTML backend to get links
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, region='us-en', backend='html', max_results=5))
                search_text = "\n".join([f"{r['href']} - {r['body']}" for r in results])
                
                final_prompt = f"""
                Identify the Founder/CEO LinkedIn and X.com URLs. 
                Company: {company_name}
                Context: {search_text}
                Return JSON: {{"full_name": "Name", "linkedin_url": "URL", "x_url": "URL"}}
                """
                res = self.ai.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": final_prompt}],
                    response_format={'type': 'json_object'}
                )
                return json.loads(res.choices[0].message.content)
        except Exception as e:
            return {"error": str(e)}