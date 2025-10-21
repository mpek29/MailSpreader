import urllib
import yaml
import json

def linkedin_url_creator(yaml_file_industries, yaml_file_url="linkedin_url.yaml"):
    """Use LinkedinIn url to make a JSON of LinkedIn company profile URLs"""
    with open(yaml_file_industries, "r", encoding="utf-8") as f:
        config_industries = yaml.safe_load(f)

    mapping_file = "industries_ids.json"
    with open(mapping_file, "r", encoding="utf-8") as mf:
        mappings_list = json.load(mf)

    value_to_id = {item["value"]: item["id"] for item in mappings_list}
    list_industries = config_industries.get("list_industries", "")

    industry_ids = []
    for name in list_industries:
        id_val = value_to_id.get(name)
        if id_val is None:
            print(f"Warning: pas de mapping pour '{name}'")
        else:
            industry_ids.append(str(id_val))

    encoded_industry = urllib.parse.quote(json.dumps(industry_ids))

    url = (
        f"https://www.linkedin.com/search/results/companies/?"
        f"industryCompanyVertical={encoded_industry}"
        f"&origin=FACETED_SEARCH&sid=_ay"
    )

    with open(yaml_file_url, "w", encoding="utf-8") as fy:
        fy.write("base_search_url: " + json.dumps(url) + "\n")

def linkedin_list_urls_creator(yaml_file_industries, yaml_file_url="linkedin_url.yaml"):
    """Create a list of LinkedIn company search URLs, one for each industry"""

    # Load industries from the YAML file
    with open(yaml_file_industries, "r", encoding="utf-8") as f:
        config_industries = yaml.safe_load(f)

    # Load the industry ID mappings
    mapping_file = "industries_ids.json"
    with open(mapping_file, "r", encoding="utf-8") as mf:
        mappings_list = json.load(mf)

    value_to_id = {item["value"]: item["id"] for item in mappings_list}
    list_industries = config_industries.get("list_industries", [])

    urls = []
    for name in list_industries:
        id_val = value_to_id.get(name)
        if id_val is None:
            print(f"Warning: no mapping found for '{name}'")
            continue
        
        encoded_industry = urllib.parse.quote(json.dumps([str(id_val)]))
        url = (
            f"https://www.linkedin.com/search/results/companies/?"
            f"industryCompanyVertical={encoded_industry}"
            f"&origin=FACETED_SEARCH&sid=_ay"
        )
        urls.append(url)

    # Save the list of URLs to a YAML file
    with open(yaml_file_url, "w", encoding="utf-8") as fy:
        yaml.dump({"search_urls": urls}, fy, allow_unicode=True)