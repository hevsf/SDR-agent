import json
from scout import SDRScout

def main():
    print("--- KRYKOS SDR SCOUT v1.0 ---")
    
    # Initialize the Scout
    scout = SDRScout()
    
    # Target URL for the test
    target_url = "https://docs.firecrawl.dev/introduction"
    
    # Step 1: Gather information from the website
    raw_content = scout.scrape_website(target_url)
    
    if not raw_content or "Error" in raw_content:
        print("[!] Failed to retrieve website content.")
        return

    # Step 2: Deep Analysis
    analysis_raw = scout.analyze_business_model(raw_content)
    
    # Step 3: Present Findings
    try:
        profile = json.loads(analysis_raw)
        print("\n[+] STRATEGIC PROSPECT PROFILE CREATED:")
        print(json.dumps(profile, indent=2))
        
        # Save for future use in the SDR pipeline
        with open("prospect_profile.json", "w") as f:
            json.dump(profile, f, indent=2)
            
    except Exception as e:
        print(f"[!] Analysis failed: {e}")

if __name__ == "__main__":
    main()