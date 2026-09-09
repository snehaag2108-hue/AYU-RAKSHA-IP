PRODUCT_TYPES={
    "medicine":"Ayurvedic medicine / therapeutic product",
    "food":"Food / wellness product",
    "cosmetic":"Cosmetic / personal-care product",
    "phytopharmaceutical":"Phytopharmaceutical-type product",
    "not_sure":"Product category requires further information"
}

def classify(product_type, description, ingredients):
    if product_type in PRODUCT_TYPES and product_type != "not_sure":
        label=PRODUCT_TYPES[product_type]; conf=0.90
    else:
        text=(description+" "+" ".join(ingredients)).lower()
        if any(x in text for x in ["cream","skin","cosmetic","lotion"]): label=PRODUCT_TYPES["cosmetic"]; conf=.68
        elif any(x in text for x in ["food","drink","nutrition","beverage"]): label=PRODUCT_TYPES["food"]; conf=.65
        elif any(x in text for x in ["treatment","therapeutic","medicine","dose"]): label=PRODUCT_TYPES["medicine"]; conf=.64
        else: label=PRODUCT_TYPES["not_sure"]; conf=.40
    return {"label":label,"confidence":round(conf,2),"needs_review":conf<.70}

def ip_strategy(novelty, description):
    n=set(x.lower() for x in novelty); result=[]
    result.append({"route":"Patent","status":"Investigate" if n & {"extraction","manufacturing process","new formulation","novel combination"} else "Needs novelty assessment","reason":"Potentially relevant novel technical features require formal patentability analysis."})
    result.append({"route":"Trademark","status":"Recommended for brand protection","reason":"Brand identifiers can be considered separately from technical protection."})
    result.append({"route":"Trade Secret","status":"Consider","reason":"Confidential manufacturing know-how may be protectable through secrecy controls."})
    result.append({"route":"Design","status":"Investigate if visual design is novel","reason":"Relevant where the product/container has protectable visual features."})
    return result

def abs_assessment(ingredients, source_context):
    bio=bool(ingredients)
    traditional=any(x in source_context.lower() for x in ["traditional","community","tribal","local knowledge"])
    return {"status":"Review Required" if bio else "No biological resource indicated","biological_resources_detected":bio,"traditional_community_context":traditional,"reason":"A biological-resource context should be reviewed against the applicable current rules and source evidence."}

def regulatory(product_type):
    return {"status":"Preliminary classification","checklist":[
        {"item":"Confirm product classification","status":"pending"},
        {"item":"Verify applicable manufacturing requirements","status":"pending"},
        {"item":"Review labelling and claims","status":"pending"},
        {"item":"Check safety/evidence documentation","status":"pending"}
    ],"note":"This prototype does not make a final regulatory determination."}

def international(markets):
    return {m:{"status":"Jurisdiction-specific review required","next_step":"Retrieve and validate current rules for this jurisdiction."} for m in markets}
