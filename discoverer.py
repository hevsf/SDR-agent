import os
import time
from duckduckgo_search import DDGS
from urllib.parse import urlparse

class LeadDiscoverer:
    def __init__(self):
        # Expanded blacklist to filter out middle-men and directories
        self.blacklist = [
            'clutch.co', 'yelp.com', 'linkedin.com', 'facebook.com', 
            'instagram.com', 'twitter.com', 'glassdoor.com', 'upwork.com',
            'expert.com', 'directory', 'wikipedia.org', 'crunchbase.com',
            'yellowpages.com', 'bbb.org', 'angis.com', 'houzz.com', 'thumbtack.com'
        ]

    def find_companies(self, niche_query, count=3):
        print(f"[*] Discoverer: Searching via Stable HTML for '{niche_query}'...")
        companies = []
        
        try:
            with DDGS() as ddgs:
                # Using the stable 'html' backend from version 6.1.0
                # We also explicitly set region to 'us-en'
                search_query = f"{niche_query} official website"
                
                # Fetch slightly more results than needed to account for the blacklist
                search_results = ddgs.text(
                    search_query, 
                    region='us-en', 
                    safesearch='off', 
                    backend='html', 
                    max_results=count + 5
                )
                
                if not search_results:
                    print("[!] No results returned from search engine.")
                    return []

                for r in search_results:
                    url = r.get('href')
                    if not url: continue
                    
                    domain = urlparse(url).netloc.lower()
                    
                    # 1. Skip if domain is in blacklist
                    if any(b in domain for b in self.blacklist):
                        continue
                        
                    # 2. Skip if we already have this URL
                    if url in [c['url'] for c in companies]:
                        continue

                    companies.append({
                        "name": r.get('title', 'Unknown'),
                        "url": url
                    })
                    
                    if len(companies) >= count:
                        break
                        
        except Exception as e:
            print(f"[!] Discoverer Search Error: {e}")
        
        print(f"[+] Discoverer: Found {len(companies)} potential targets.")
        return companies