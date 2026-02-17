import json
import time
import re
from discoverer import LeadDiscoverer
from scout import SDRScout
from identity import IdentityHunter


def apply_strict_privacy_mask(profile, target_index):
    """
    Completely anonymizes the profile. 
    Replaces real names with 'Target-ID' and redacts them from text blocks.
    """
    # 1. Generate a generic ID (Target-A, Target-B...)
    generic_id = f"Target-{chr(65 + target_index)}"
    real_name = profile.get('company_name', '')
    
    masked = profile.copy()
    
    # 2. Complete redact Name and URL
    masked['company_name'] = generic_id
    masked['source_url'] = "https://[REDACTED].com/"

    # 3. Deep Redaction: Find real_name inside ALL text fields and replace it
    if real_name and len(real_name) > 2:
        # Create a case-insensitive regex for the company name
        # We also catch common variations (like "Socialfly" vs "Socialfly NY")
        name_parts = real_name.split()
        main_name = name_parts[0] if name_parts else real_name
        
        pattern = re.compile(re.escape(main_name), re.IGNORECASE)

        for key, value in masked.items():
            if isinstance(value, str):
                masked[key] = pattern.sub(generic_id, value)
            elif isinstance(value, list):
                masked[key] = [pattern.sub(generic_id, item) if isinstance(item, str) else item for item in value]

    return masked



def main():
    print("--- KRYKOS AUTOMATED LEAD HUNTER v2.0 ---")
    
    # 1. Ask the user what to hunt
    niche = input("> What niche/location are we hunting today? (e.g. Marketing Agencies in Austin): ")
    
    discoverer = LeadDiscoverer()
    scout = SDRScout()
    hunter = IdentityHunter()
    
    # 2. Find the leads
    leads = discoverer.find_companies(niche, count=3) # Let's start with 3 for testing
    
    final_campaign = []

    for i, lead in enumerate(leads):
        print(f"\n" + "="*60)
        print(f"[*] Pipeline Step 1/3: Scraping {lead['url']}...")
        
        # 3. Analyze the business
        site_data = scout.scrape_website(lead['url'])
        if not site_data["main_md"]:
            continue
            
        # Pass lead['name'] as a fallback to the analyzer
        analysis_raw = scout.analyze_business_model(site_data["main_md"], lead['name'])
        
        try:
            profile = json.loads(analysis_raw)
            
            # SAFE ACCESS using .get() to avoid KeyError
            company_name = profile.get('company_name') or lead['name']
            profile['company_name'] = company_name # Ensure it exists for later steps
            profile['source_url'] = lead['url']
            
            # 4. Find the human
            print(f"[*] Pipeline Step 2/3: Hunting socials for {company_name}...")
            combined_site_text = site_data["main_md"] + "\n" + site_data["about_md"]
            person_data = hunter.find_decision_maker(company_name, combined_site_text)
            
            full_prospect = {
                "business": profile,
                "decision_maker": person_data
            }
            
            # 5. Mask and Show
            masked = apply_strict_privacy_mask(profile, i) # Mask only the business part for display
            print("\n[+] DISCOVERED PROSPECT (MASKED):")
            print(json.dumps(masked, indent=2))
            
            final_campaign.append(full_prospect)
            
        except Exception as e:
            print(f"[!] Pipeline failed for {lead['url']}: {e}")
            
        time.sleep(2) # Be nice to the web

    # 6. Save the unmasked data for your private use
    with open("campaign_results.json", "w") as f:
        json.dump(final_campaign, f, indent=2)
    print(f"\n🏁 Hunting complete. {len(final_campaign)} full profiles saved to campaign_results.json")

if __name__ == "__main__":
    main()