from app.rag.retriever import rag
from app.rules.engines import classify, ip_strategy, abs_assessment, regulatory, international

class AnalysisOrchestrator:
    def run(self, innovation):
        query=f"{innovation.name} {innovation.description} {' '.join(innovation.ingredients)} {' '.join(innovation.novelty)}"
        evidence=rag.search(query, top_k=5)
        classification=classify(innovation.product_type, innovation.description, innovation.ingredients)
        ip=ip_strategy(innovation.novelty, innovation.description)
        tk=self.tk_check(query, evidence)
        abs_a=abs_assessment(innovation.ingredients, innovation.source_context)
        reg=regulatory(innovation.product_type)
        intl=international(innovation.target_markets)
        risks=self.risk(tk, abs_a, classification, reg, intl)
        roadmap=self.roadmap(risks, ip, abs_a, reg)
        confidence=self.confidence(evidence, classification)
        return {"classification":classification,"ip_strategy":ip,"tk_assessment":tk,"abs_assessment":abs_a,"regulatory":reg,"international":intl,"risks":risks,"roadmap":roadmap,"confidence":confidence,"evidence":evidence}

    def tk_check(self, query, evidence):
        matches=[e for e in evidence if any(k in e.get("text","").lower() for k in ["traditional knowledge","classical","traditional use","ayurveda"])]
        if matches:
            top=max(x.get("relevance_score",0) for x in matches)
            risk=min(95,round(45+top*50))
            return {"status":"Potential overlap detected","risk_score":risk,"matches":[{"source":m.get("title"),"similarity":round(m.get("relevance_score",0),3)} for m in matches[:3]],"note":"Potential similarity is not a legal conclusion; validate against authoritative records."}
        return {"status":"No strong demo-source match found","risk_score":25,"matches":[],"note":"Absence of a match in this demo knowledge base does not establish novelty or freedom to operate."}

    def risk(self, tk, abs_a, classification, reg, intl):
        tk_r=tk["risk_score"]
        abs_r=70 if abs_a["biological_resources_detected"] else 15
        reg_r=55 if reg["status"]=="Preliminary classification" else 30
        intl_r=50 if len(intl)>1 else 25
        patent_r=60 if classification["needs_review"] else 35
        overall=round(.30*tk_r+.20*abs_r+.20*reg_r+.15*intl_r+.15*patent_r)
        return {"overall":overall,"severity":"High" if overall>=70 else "Medium" if overall>=45 else "Low","categories":{"traditional_knowledge":tk_r,"abs":abs_r,"regulatory":reg_r,"international":intl_r,"patent_uncertainty":patent_r}}

    def roadmap(self, risks, ip, abs_a, reg):
        tasks=[]
        tasks.append({"priority":"High","task":"Review traditional-knowledge evidence","status":"pending"})
        tasks.append({"priority":"High" if abs_a["biological_resources_detected"] else "Medium","task":"Assess biodiversity / ABS requirements","status":"pending"})
        tasks.append({"priority":"Medium","task":"Review IP protection strategy","status":"pending"})
        tasks.append({"priority":"Medium","task":"Complete regulatory classification and documentation checklist","status":"pending"})
        tasks.append({"priority":"Upcoming","task":"Run target-market jurisdiction review","status":"pending"})
        return tasks

    def confidence(self, evidence, classification):
        evidence_score=max([e.get("relevance_score",0) for e in evidence], default=0)
        score=0.55+min(.35,evidence_score*.35)
        if classification["needs_review"]: score-=.10
        score=max(0,min(.95,score))
        level="High" if score>=.80 else "Moderate" if score>=.60 else "Low"
        return {"score":round(score,2),"level":level,"reason":"Based on retrieval relevance, classification confidence and presence of supporting records in the configured knowledge base.","abstain":score<.60}
