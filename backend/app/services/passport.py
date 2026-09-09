from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from pathlib import Path
from app.core.config import settings

def readiness(analysis):
    r=analysis.risks or {}
    overall=r.get("overall",50)
    return max(5,min(95,100-overall))

def make_passport(innovation, analysis):
    return {"innovation_id":innovation.id,"innovation_name":innovation.name,"readiness":readiness(analysis),"summary":{
        "classification":analysis.classification,"ip_strategy":analysis.ip_strategy,"traditional_knowledge":analysis.tk_assessment,
        "abs":analysis.abs_assessment,"regulatory":analysis.regulatory,"international":analysis.international,
        "risks":analysis.risks,"roadmap":analysis.roadmap,"confidence":analysis.confidence}}

def generate_pdf(innovation, analysis):
    Path(settings.report_dir).mkdir(parents=True,exist_ok=True)
    path=Path(settings.report_dir)/f"ayu_ip_passport_{innovation.id}.pdf"
    styles=getSampleStyleSheet(); doc=SimpleDocTemplate(str(path),pagesize=A4,rightMargin=45,leftMargin=45,topMargin=45,bottomMargin=45)
    story=[Paragraph("AYU-IP PASSPORT",styles["Title"]),Paragraph(f"Innovation: {innovation.name}",styles["Heading2"]),Spacer(1,12)]
    p=make_passport(innovation,analysis)
    story.append(Paragraph(f"Readiness: {p['readiness']}%",styles["Heading2"]))
    for k,v in p["summary"].items():
        story.append(Paragraph(f"<b>{k.replace('_',' ').title()}</b>",styles["Heading3"]))
        story.append(Paragraph(str(v).replace("<","&lt;").replace(">","&gt;"),styles["BodyText"]))
        story.append(Spacer(1,6))
    story.append(Paragraph("Decision-support prototype. Validate all high-impact conclusions against current authoritative sources and qualified professionals.",styles["BodyText"]))
    doc.build(story)
    return str(path)
