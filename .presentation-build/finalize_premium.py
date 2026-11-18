import copy
import hashlib
import io
import json
import posixpath
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET
from xml.sax.saxutils import escape

from openpyxl import Workbook, load_workbook
from pypdf import PdfReader
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from reportlab.lib.utils import ImageReader

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / '.presentation-build'
OUT = ROOT / 'output' / 'financial-analyst' / 'premium'
OUT.mkdir(parents=True, exist_ok=True)
EXPORT = Path(r'C:\Users\noohk\AppData\Local\Packages\OpenAI.Codex_2p2nqsd0c76g0\LocalCache\Roaming\Codex\web\Codex\artifact-sessions\exports\latest\4bc02b42bb2986b853e35da1fbcdef4585cae1a8ed967bb4f84268668875b13a')
DATA = json.loads((BUILD / 'premium-content.json').read_text(encoding='utf-8'))
BASE = 'https://github.com/shdbfrz/AI-Powered-Financial-Analyst/blob/develop/'
STEM = 'AI_Financial_Analyst_Premium'
NS = {'p':'http://schemas.openxmlformats.org/presentationml/2006/main',
      'a':'http://schemas.openxmlformats.org/drawingml/2006/main',
      'c':'http://schemas.openxmlformats.org/drawingml/2006/chart',
      'r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
REL = 'http://schemas.openxmlformats.org/package/2006/relationships'
CT = 'http://schemas.openxmlformats.org/package/2006/content-types'
for key, value in NS.items():
    ET.register_namespace(key, value)

# Materialize the literal repository sample values as an editable embedded workbook.
# This is a new snapshot, not a replacement for an existing source workbook.
wb = Workbook()
ws = wb.active
ws.title = 'Sample'
ws.append(['Sample row', 'Close', 'SMA5'])
for row, close, sma in zip(DATA['chart']['rows'], DATA['chart']['close'], DATA['chart']['sma5']):
    ws.append([row, close, sma])
ws.freeze_panes = 'A2'
ws.column_dimensions['A'].width = 18
ws.column_dimensions['B'].width = 22
ws.column_dimensions['C'].width = 22
source_ws = wb.create_sheet('Source')
source_ws.append(['Data status', 'Synthetic OHLCV. No real ticker or forecasting output.'])
source_ws.append(['Source file', BASE + 'docs/sprint2_sample_output/features_preview_first25rows.csv'])
source_ws.append(['Displayed rows', 'Sample rows 5-25. First 4 rows lack a complete SMA5 window.'])
buf = io.BytesIO()
wb.save(buf)
workbook_bytes = buf.getvalue()

with zipfile.ZipFile(EXPORT / (STEM + '.pptx')) as z:
    parts = {name:z.read(name) for name in z.namelist()}
chart_path = next(name for name in parts if re.fullmatch(r'ppt/(?:slides/)?charts/chart\d+\.xml', name))
chart = ET.fromstring(parts[chart_path])
for index, series in enumerate(chart.findall('.//c:ser', NS)):
    col = 'BC'[index]
    tx = series.find('c:tx', NS)
    label = tx.find('c:v', NS).text
    tx.clear()
    ref = ET.SubElement(tx, '{'+NS['c']+'}strRef')
    ET.SubElement(ref, '{'+NS['c']+'}f').text = f"'Sample'!${col}$1"
    cache = ET.SubElement(ref, '{'+NS['c']+'}strCache')
    ET.SubElement(cache, '{'+NS['c']+'}ptCount', {'val':'1'})
    ET.SubElement(ET.SubElement(cache, '{'+NS['c']+'}pt', {'idx':'0'}), '{'+NS['c']+'}v').text = label
    for tag, cell_col in [('cat','A'), ('val',col)]:
        node = series.find('c:'+tag, NS)
        literal = node.find('c:numLit', NS)
        assert literal is not None
        literal.tag = '{'+NS['c']+'}numCache'
        node.remove(literal)
        nr = ET.SubElement(node, '{'+NS['c']+'}numRef')
        ET.SubElement(nr, '{'+NS['c']+'}f').text = f"'Sample'!${cell_col}$2:${cell_col}$22"
        nr.append(literal)
external = ET.SubElement(chart, '{'+NS['c']+'}externalData', {'{'+NS['r']+'}id':'rIdSampleWorkbook'})
ET.SubElement(external, '{'+NS['c']+'}autoUpdate', {'val':'0'})
parts[chart_path] = ET.tostring(chart, encoding='utf-8', xml_declaration=True)
embedded_path = 'ppt/embeddings/financial-sample.xlsx'
parts[embedded_path] = workbook_bytes
rels_path = posixpath.join(posixpath.dirname(chart_path), '_rels', posixpath.basename(chart_path)+'.rels')
rels = ET.Element('{'+REL+'}Relationships')
ET.SubElement(rels, '{'+REL+'}Relationship', {'Id':'rIdSampleWorkbook',
    'Type':NS['r']+'/package', 'Target':posixpath.relpath(embedded_path, posixpath.dirname(chart_path))})
parts[rels_path] = ET.tostring(rels, encoding='utf-8', xml_declaration=True)
content_types = ET.fromstring(parts['[Content_Types].xml'])
if not any(x.get('Extension')=='xlsx' for x in content_types):
    ET.SubElement(content_types, '{'+CT+'}Default', {'Extension':'xlsx', 'ContentType':'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'})
parts['[Content_Types].xml'] = ET.tostring(content_types, encoding='utf-8', xml_declaration=True)

# Manual advancement remains enabled. A short fade supplies restrained slide transitions.
slide_paths = sorted([n for n in parts if re.fullmatch(r'ppt/slides/slide\d+\.xml', n)], key=lambda n:int(re.search(r'slide(\d+)',n).group(1)))
for name in slide_paths:
    slide = ET.fromstring(parts[name])
    for existing in slide.findall('p:transition', NS):
        slide.remove(existing)
    transition = ET.Element('{'+NS['p']+'}transition', {'spd':'fast', 'advClick':'1'})
    ET.SubElement(transition, '{'+NS['p']+'}fade')
    position = next((i for i, child in enumerate(slide) if child.tag in ('{'+NS['p']+'}timing', '{'+NS['p']+'}extLst')),len(slide))
    slide.insert(position, transition)
    parts[name] = ET.tostring(slide, encoding='utf-8', xml_declaration=True)
final_pptx = OUT / (STEM+'.pptx')
with zipfile.ZipFile(final_pptx, 'w', zipfile.ZIP_DEFLATED) as z:
    for name, value in parts.items():
        z.writestr(name, value)

# PDF companion preserves the reviewed 16:9 appearance. Native objects live in the PPTX.
c = canvas.Canvas(str(OUT / (STEM+'.pdf')), pagesize=(960,540))
c.setTitle('AI-Powered Financial Analyst - Premium Project Presentation')
for number in range(1,19):
    c.drawImage(ImageReader(str(EXPORT / f'slide-{number}.png')),0,0,width=960,height=540)
    c.showPage()
c.save()

handoffs = [
    'Umar will now explain the system boundaries and serving layer.',
    'Nooh will now discuss the frontend, sample visualization and full workflow.',
    'Salma will now explain persistence, implementation status and the roadmap.',
    'Mohammad will now explain the proposed user experience and team handoffs.',
    'Thank you. We welcome questions from the evaluators.'
]
coverage = ['Introduction, problem, proposed solution and AI/data architecture',
            'Layered architecture, technology stack, API communication and security',
            'Frontend architecture, repository sample chart and complete workflow',
            'Conceptual database, implementation status and future delivery scope',
            'User journey, conceptual dashboard, team contribution diagram and Q&A']
prompt = 'Create a premium technology conference presentation illustration, widescreen 16:9. Deep midnight navy background (#07152B). Entire LEFT 48% is very quiet almost solid navy negative space for editable title to be added later, no text. On RIGHT half: exquisite architectural visualization of financial data intelligence, a small set of translucent glass data layers and precise interconnected luminous nodes flowing through a central faceted analytical core. Royal blue, cyan, restrained teal and violet accents, sophisticated studio 3D lighting, crisp purposeful composition, premium enterprise AI research aesthetic. Thin elegant cyan connections between layers, depth, subtle light refraction. No words, no letters, no numbers, no logos, no currency symbols, no fake UI, no actual financial charts, no robots, no human figures, no stock-photo look. Keep far bottom quiet for small author line. The illustration is conceptual art, not a technical architecture diagram. Avoid busy neon cyberpunk effects.'

md = ['# Presentation guide', '', 'AI-Powered Financial Analyst & Investment Decision Support System', '',
      '18 slides. Suggested duration: 13-16 minutes plus Q&A. Replace [Institution name] on the cover before presenting.', '',
      '## Five speaking sections', '', '| Speaker | URN | Slides | Assigned area |', '|---|---|---|---|']
for member in DATA['team']:
    md.append(f'| {member[0]} | {member[1]} | {member[3]} | {member[2]} |')
md += ['']
for i, member in enumerate(DATA['team']):
    md += [f'### {member[0]}', '', f'Coverage: {coverage[i]}.', '', 'Suggested time: approximately 2.5-3.5 minutes.', '', f'Handoff: "{handoffs[i]}"', '']
for i, slide in enumerate(DATA['slides']):
    member = DATA['team'][slide['owner']]
    md += [f'## Slide {i+1}: {slide["title"]}', '', f'Speaker: {member[0]}', '',
           '**Technical explanation:** '+slide['explanation'], '', '**Suggested script:**', '', slide['script'], '', '**Sources:**', '']
    md += [f'- [{s}]({BASE+s})' for s in slide['sources']]
    md += ['']
md += ['## Source and visual provenance', '',
       'Primary evidence: supplied AI-Powered-Financial-Analyst-develop.zip and selected connected GitHub develop files. Source review: 18 November 2026.', '',
       'Implementation means source present. Live providers, CI and deployment were not executed as part of this presentation review.', '',
       'The chart uses synthetic SAMPLE close and SMA5 values from the committed preview, rows 5-25. Its embedded workbook is a new literal snapshot of those source values.', '',
       'The dashboard is a conceptual editable mockup. The repository contains only the frontend scaffold.', '',
       'Cover asset: built-in ImageGen. Saved project path: '+str(BUILD / 'premium-assets' / 'analytics-hero.png'), '',
       'Final image prompt:', '', prompt, '']
(OUT / 'Presentation_Guide.md').write_text('\n'.join(md), encoding='utf-8')

# Printable guide with two slides per page, plus a speaking map and provenance appendix.
pdfmetrics.registerFont(TTFont('GuideArial',r'C:\Windows\Fonts\arial.ttf'))
pdfmetrics.registerFont(TTFont('GuideArialBold',r'C:\Windows\Fonts\arialbd.ttf'))
pdfmetrics.registerFontFamily('GuideArial', normal='GuideArial', bold='GuideArialBold')
navy = colors.HexColor('#172C48')
blue = colors.HexColor('#3869E8')
teal = colors.HexColor('#0D9F96')
body = ParagraphStyle('Body',fontName='GuideArial',fontSize=10.2,leading=14,spaceAfter=8,textColor=navy)
small = ParagraphStyle('Small',parent=body,fontSize=8.5,leading=11,textColor=colors.HexColor('#667B96'))
heading = ParagraphStyle('Heading',parent=body,fontName='GuideArialBold',fontSize=15,leading=19,spaceBefore=8,spaceAfter=9,textColor=blue)
title = ParagraphStyle('Title',parent=heading,fontSize=25,leading=31,textColor=navy,spaceAfter=15)
speaker = ParagraphStyle('Speaker',parent=small,fontName='GuideArialBold',textColor=teal)
def para(text, style=body):
    return Paragraph(escape(text).replace('\n','<br/>'),style)
def page_footer(cv,doc):
    cv.setFillColor(colors.HexColor('#667B96'))
    cv.setFont('GuideArial',8)
    cv.drawString(43,28,'AI-Powered Financial Analyst | Presentation guide')
    cv.drawRightString(A4[0]-43,28,str(doc.page))
story = [para('Presentation guide',title),para('AI-Powered Financial Analyst & Investment Decision Support System',heading),
         para('18 slides / five speaking sections / approximately 13-16 minutes plus Q&A'),
         para('Before presenting: replace [Institution name] on the cover. Slides distinguish code present, scaffolds and planned services. The financial chart uses synthetic repository data.'),Spacer(1,12)]
rows = [[para('Speaker',small),para('URN',small),para('Slides',small),para('Assigned area',small)]]
for member in DATA['team']:
    rows.append([para(member[0],small),para(member[1],small),para(member[3],small),para(member[2],small)])
table = Table(rows,colWidths=[123,111,48,125],hAlign='LEFT')
table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#E8F2FC')),('VALIGN',(0,0),(-1,-1),'TOP'),('BOTTOMPADDING',(0,0),(-1,-1),9),('TOPPADDING',(0,0),(-1,-1),7),('LINEBELOW',(0,0),(-1,-1),0.4,colors.HexColor('#D6E2F2'))]))
story += [table,Spacer(1,12)]
for i,member in enumerate(DATA['team']):
    story += [para(member[0]+' - slides '+member[3],speaker),para(coverage[i]+'. '+handoffs[i],body)]
story.append(PageBreak())
for i,slide in enumerate(DATA['slides']):
    member = DATA['team'][slide['owner']]
    block = [para(f'Slide {i+1}: {slide["title"]}',heading),para('Speaker: '+member[0],speaker),
             Paragraph('<b>Technical explanation:</b> '+escape(slide['explanation']),body),
             Paragraph('<b>Suggested script:</b> '+escape(slide['script']),body),
             para('Source files: '+', '.join(slide['sources']),small),Spacer(1,13)]
    story.append(KeepTogether(block))
    if i % 2 == 1 and i != 17:
        story.append(PageBreak())
story += [PageBreak(),para('Source and design notes',title),
          para('Primary evidence: the supplied develop ZIP and selected connected GitHub files. Repository links also appear in slide speaker notes and the editable Markdown guide.'),
          para('Status caveats: Yahoo Finance and NewsAPI collection code is present. Alpha Vantage is interface-only. Models, FinBERT, the LLM layer, database application integration and dashboard remain planned or scaffolded. No model accuracy, successful CI run, live-provider validation or deployment result is claimed.'),
          para('Financial chart: synthetic SAMPLE data, rows 5-25, close and SMA5. The PowerPoint contains an editable chart and an embedded literal data snapshot.'),
          para('Dashboard: editable conceptual mockup. It is not a screenshot or proof of implemented functionality.'),
          para('Cover artwork: generated using the built-in ImageGen tool. Project asset path: '+str(BUILD/'premium-assets'/'analytics-hero.png'),small),
          para('Final image prompt',heading),para(prompt,small)]
SimpleDocTemplate(str(OUT/'Presentation_Guide.pdf'),pagesize=A4,rightMargin=43,leftMargin=43,topMargin=42,bottomMargin=43,title='AI Financial Analyst - Presentation Guide').build(story,onFirstPage=page_footer,onLaterPages=page_footer)

# Final integrity checks: slide count, editable evidence, identities, relationships and sample lineage.
with zipfile.ZipFile(final_pptx) as z:
    names=set(z.namelist())
    notes=[n for n in names if re.fullmatch(r'ppt/notesSlides/notesSlide\d+\.xml',n)]
    assert len(slide_paths)==18 and len(notes)==18
    assert all(ET.fromstring(z.read(n)).find('p:transition/p:fade',NS) is not None for n in slide_paths)
    all_text='\n'.join(' '.join(ET.fromstring(z.read(n)).itertext()) for n in slide_paths)
    for member in DATA['team']:
        assert member[0] in all_text and member[1] in all_text
    assert len(ET.fromstring(z.read('ppt/slides/slide6.xml')).findall('.//a:tbl',NS))==1
    assert len(ET.fromstring(z.read('ppt/slides/slide10.xml')).findall('.//c:chart',NS))==1
    chart=ET.fromstring(z.read(chart_path))
    for idx,series in enumerate(chart.findall('.//c:ser',NS)):
        actual=[float(x.text) for x in series.findall('c:val/c:numRef/c:numCache/c:pt/c:v',NS)]
        expected=DATA['chart']['close' if idx==0 else 'sma5']
        assert len(actual)==len(expected)==21
        assert all(abs(a-b)<1e-10 for a,b in zip(actual,expected))
    embedded=load_workbook(io.BytesIO(z.read(embedded_path)),data_only=True)
    for i,(row,close,sma) in enumerate(zip(DATA['chart']['rows'],DATA['chart']['close'],DATA['chart']['sma5']),2):
        assert embedded['Sample'].cell(i,1).value==row
        assert abs(embedded['Sample'].cell(i,2).value-close)<1e-10
        assert abs(embedded['Sample'].cell(i,3).value-sma)<1e-10
    for name in names:
        if name.endswith('.xml') or name.endswith('.rels'):
            xml=ET.fromstring(z.read(name))
            if name.endswith('.rels'):
                parent='' if name=='_rels/.rels' else posixpath.dirname(posixpath.dirname(name))
                for rel in xml:
                    if rel.get('TargetMode')=='External':
                        continue
                    target=rel.get('Target')
                    resolved=target.lstrip('/') if target.startswith('/') else posixpath.normpath(posixpath.join(parent,target))
                    assert resolved in names,(name,resolved)
    media=[z.read(n) for n in names if n.startswith('ppt/media/')]
    hero=(BUILD/'premium-assets'/'analytics-hero.png').read_bytes()
    assert any(hashlib.sha256(m).digest()==hashlib.sha256(hero).digest() for m in media)
    connectors=sum(len(ET.fromstring(z.read(n)).findall('.//p:cxnSp',NS)) for n in slide_paths)
assert len(PdfReader(OUT/(STEM+'.pdf')).pages)==18
report={'slides':18,'speaker_notes':18,'editable_chart':True,'embedded_workbook':True,'editable_table':True,'connectors':connectors,'fade_transitions':18,'identity_checks':'passed','chart_values_match_source':True,'guide_pages':len(PdfReader(OUT/'Presentation_Guide.pdf').pages)}
(BUILD/'premium-validation.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report))
for file in OUT.iterdir():
    print(file)
