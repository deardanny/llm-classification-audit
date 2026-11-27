"""Build the public English report from the released methods text and figures."""
from pathlib import Path
from html import escape
import re
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,Image,KeepTogether
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
# Embed fonts; use ReportLab's bundled Vera family for portable rendering.
import reportlab
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
font_dir=Path(reportlab.__file__).resolve().parent/'fonts'
for name,file in [('Times-Roman','Vera.ttf'),('Helvetica','Vera.ttf'),('Helvetica-Bold','VeraBd.ttf'),('Courier','Vera.ttf')]:
    pdfmetrics.registerFont(TTFont(name,str(font_dir/file)))
pdfmetrics.registerFontFamily('Times-Roman',normal='Times-Roman',bold='Helvetica-Bold',italic='Times-Roman',boldItalic='Helvetica-Bold')
pdfmetrics.registerFontFamily('Helvetica',normal='Helvetica',bold='Helvetica-Bold',italic='Helvetica',boldItalic='Helvetica-Bold')
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'reports';OUT.mkdir(exist_ok=True)
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='BodyResearch',fontName='Times-Roman',fontSize=9.5,leading=13.6,spaceAfter=8,textColor=colors.HexColor('#222222')))
styles.add(ParagraphStyle(name='TitleResearch',fontName='Times-Roman',fontSize=25,leading=28,spaceAfter=15))
styles.add(ParagraphStyle(name='SectionResearch',fontName='Helvetica-Bold',fontSize=11.2,leading=15,spaceBefore=16,spaceAfter=8,keepWithNext=True))
styles.add(ParagraphStyle(name='TableResearch',fontName='Helvetica',fontSize=8,leading=10.5))
styles.add(ParagraphStyle(name='CaptionResearch',fontName='Helvetica',fontSize=8,leading=11,textColor=colors.HexColor('#555555'),spaceAfter=10))
def fmt(s):
    s=escape(s);s=re.sub(r'\*\*(.*?)\*\*',r'<b>\1</b>',s);s=re.sub(r'`([^`]+)`',r'<font name="Courier" size="8">\1</font>',s)
    return s
story=[];text=(ROOT/'docs/decision-review.md').read_text();blocks=text.strip().split('\n\n')
for block in blocks:
    if block.startswith('# '):story.append(Paragraph(fmt(block[2:]),styles['TitleResearch']))
    elif block.startswith('## '):story.append(Paragraph(fmt(block[3:]),styles['SectionResearch']))
    elif block.startswith('|'):
        rows=[]
        for line in block.splitlines():
            cells=[x.strip() for x in line.strip('|').split('|')]
            if all(re.fullmatch(r'[-: ]+',x) for x in cells):continue
            rows.append([Paragraph(fmt(c),styles['TableResearch']) for c in cells])
        widths=[190]+[(475-190)/(len(rows[0])-1)]*(len(rows[0])-1) if len(rows[0])==4 else [65,110,95,110,95]
        table=Table(rows,colWidths=widths,repeatRows=1,hAlign='LEFT')
        table.setStyle(TableStyle([('LINEABOVE',(0,0),(-1,0),.6,colors.black),('LINEBELOW',(0,0),(-1,0),.5,colors.black),('LINEBELOW',(0,-1),(-1,-1),.5,colors.black),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),4),('RIGHTPADDING',(0,0),(-1,-1),6),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7)]))
        story.append(KeepTogether([Spacer(1,5),table,Spacer(1,11)]))
    elif block.startswith('!['):
        match=re.search(r'\]\(([^)]+)\)',block);img=(ROOT/'docs'/match.group(1)).resolve();story.append(Image(str(img),width=475,height=475*3.45/9));story.append(Paragraph('Figure 1. Decision-aware review against a model-derived endpoint. Lower is better. Shading describes random-order variation, not uncertainty about ground truth.',styles['CaptionResearch']))
    elif re.match(r'^\d+\.',block):
        for line in block.splitlines():story.append(Paragraph(fmt(line),styles['BodyResearch']))
    else:story.append(Paragraph(fmt(block.replace('\n',' ')),styles['BodyResearch']))
def footer(canvas,doc):
    canvas.saveState();canvas.setStrokeColor(colors.HexColor('#bbbbbb'));canvas.setLineWidth(.4);canvas.line(60,49,535,49)
    canvas.setFont('Helvetica',7.5);canvas.setFillColor(colors.HexColor('#666666'));canvas.drawString(60,37,'D. Jang  /  Company A [Confidential]  /  Public research report')
    canvas.drawRightString(535,37,str(doc.page));canvas.restoreState()
SimpleDocTemplate(str(OUT/'research-report.pdf'),pagesize=A4,rightMargin=60,leftMargin=60,topMargin=53,bottomMargin=64,title='Auditing the decisions behind LLM summaries',author='Daniel (Heedong) Jang',subject='Aggregate findings, evidence gates and decision-aware review; public anonymized edition').build(story,onFirstPage=footer,onLaterPages=footer)
print('Built public research report.')
