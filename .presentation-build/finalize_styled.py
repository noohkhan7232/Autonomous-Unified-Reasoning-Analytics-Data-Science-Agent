from pathlib import Path
from xml.etree import ElementTree as ET
import json
import re
import shutil
import zipfile
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from pypdf import PdfReader

root = Path(__file__).resolve().parent.parent
out = root / 'output' / 'financial-analyst'
source = Path(r'C:\Users\noohk\AppData\Local\Packages\OpenAI.Codex_2p2nqsd0c76g0\LocalCache\Roaming\Codex\web\Codex\artifact-sessions\exports\latest\4bc02b42bb2986b853e35da1fbcdef4585cae1a8ed967bb4f84268668875b13a')
stem = 'AI_Powered_Financial_Analyst_Styled'
shutil.copy2(source / (stem + '.pptx'), out / (stem + '.pptx'))
c = canvas.Canvas(str(out / (stem + '.pdf')), pagesize=(960,540))
c.setTitle('AI-Powered Financial Analyst - Project Presentation')
for number in range(1,16):
    c.drawImage(ImageReader(str(source / f'slide-{number}.png')), 0, 0, width=960, height=540)
    c.showPage()
c.save()
ns = {'a':'http://schemas.openxmlformats.org/drawingml/2006/main', 'p':'http://schemas.openxmlformats.org/presentationml/2006/main'}
with zipfile.ZipFile(out / (stem + '.pptx')) as z:
    slides = [n for n in z.namelist() if re.fullmatch(r'ppt/slides/slide\d+\.xml', n)]
    notes = [n for n in z.namelist() if re.fullmatch(r'ppt/notesSlides/notesSlide\d+\.xml', n)]
    assert len(slides) == len(notes) == 15
    text = '\n'.join(' '.join(ET.fromstring(z.read(n)).itertext()) for n in slides)
    data = json.loads((root / '.presentation-build' / 'deck-content.json').read_text(encoding='utf-8'))
    for person in data['team']:
        assert person[0] in text
        assert person[1] in text
    table_slide = ET.fromstring(z.read('ppt/slides/slide7.xml'))
    assert len(table_slide.findall('.//a:tbl', ns)) == 1
    for n in z.namelist():
        if n.endswith('.xml'):
            ET.fromstring(z.read(n))
    connectors = sum(len(ET.fromstring(z.read(n)).findall('.//p:cxnSp',ns)) for n in slides)
    assert connectors >= 20
assert len(PdfReader(out / (stem + '.pdf')).pages) == 15
print(json.dumps({'slides':15, 'notes':15, 'editable_table':True, 'connectors':connectors, 'identity_checks':'passed'}))
print(out / (stem + '.pptx'))
print(out / (stem + '.pdf'))
