from app.rules.engines import classify, ip_strategy, abs_assessment

def test_classify():
    r=classify("cosmetic","herbal skin cream",["turmeric"])
    assert r["label"]

def test_ip():
    r=ip_strategy(["extraction"],"new extraction process")
    assert any(x["route"]=="Patent" for x in r)

def test_abs():
    r=abs_assessment(["ashwagandha"],"traditional community")
    assert r["biological_resources_detected"] is True
