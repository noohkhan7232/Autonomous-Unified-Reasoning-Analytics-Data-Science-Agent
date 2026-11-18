import json
import re
import shutil
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'output' / 'financial-analyst'
OUT.mkdir(parents=True, exist_ok=True)
EXPORT = Path(r'C:\Users\noohk\AppData\Local\Packages\OpenAI.Codex_2p2nqsd0c76g0\LocalCache\Roaming\Codex\web\Codex\artifact-sessions\exports\latest\4bc02b42bb2986b853e35da1fbcdef4585cae1a8ed967bb4f84268668875b13a')
DATA = json.loads((ROOT / '.presentation-build' / 'deck-content.json').read_text(encoding='utf-8'))

explanations = [
    'Introduces the project, all five team members, their URNs and assigned technical areas. The institution name is intentionally a placeholder.',
    'Connects the problem of fragmented price and news data to provider normalization and a shared feature vocabulary. Benefits are objectives rather than measured outcomes.',
    'Shows the implemented data-to-feature flow. Sixteen generator groups feed versioned CSV and metadata reports. Predictive models and language modules remain planned.',
    'Defines the boundary between implemented adapters and the proposed inference, decision and explanation stages. Training belongs in AI modules rather than backend routes.',
    'Explains the high-level architecture. Data preparation writes local artifacts. The target intelligence path adds models and FinBERT, then a decision engine and LLM narration. FastAPI serves results to React. PostgreSQL and Redis have configuration but await application integration.',
    'Identifies the actual FastAPI surface: an app factory, versioned router, health endpoint and Pydantic Settings. Authentication, business schemas, ORM sessions and AI orchestration still need implementation.',
    'Separates source implementation, scaffolds, dependency declarations and planned modules. A library in a requirements file is not proof of an integrated feature.',
    'Explains the React entry point and current placeholder App. Reusable chart, page, API-service and authentication components are future work.',
    'Contrasts the existing health route with the proposed analysis contract. The latter would carry ticker requests and return structured analytical outputs with an educational disclaimer.',
    'Shows a proposed subset of documented database entities and their associations. This is a conceptual model, not an implemented ERD or migration. Keys, constraints and cardinalities remain design work.',
    'Separates the current file pipeline from its planned application extension. Redis infrastructure exists in Compose, while the implemented AI cache uses local files.',
    'Summarizes existing error-handling utilities and test definitions. Highlights remaining authentication, production configuration and evaluation work. Centered swing features need causal treatment before live modeling.',
    'Presents an explicitly proposed wireframe. It prioritizes ticker selection, freshness, historical evidence, uncertainty, sentiment and readable explanations. Accessibility goals require future testing.',
    'Reconciles the stale main README with later data-collection and feature-engineering code. The committed sample uses synthetic data and does not establish model accuracy.',
    'Closes with all five assigned responsibilities and speaking ranges. The team assignments do not verify individual implementation authorship.'
]

focus = [
    'Project purpose, provider adapters, feature engineering and model roadmap',
    'Integration boundaries, high-level architecture and actual API surface',
    'Stack status, React structure and client-server communication',
    'Conceptual persistence, data workflow and reliability requirements',
    'Proposed UX, development status and final synthesis'
]
transitions = [
    'Umar will now explain how the backend will expose these capabilities.',
    'Nooh will now cover the frontend and the planned client-server interaction.',
    'Salma will now explain persistence, workflow and technical reliability.',
    'Mohammad will close with interface design and the roadmap.',
    'Thank you. We welcome questions from the evaluators.'
]

lines = ['# Presentation guide', '',
         'AI-Powered Financial Analyst & Investment Decision Support System', '',
         'Source review: supplied develop ZIP and selected GitHub develop files, 18 November 2026.', '',
         'Replace [Institution name] on the title slide before presenting. Scripts describe assigned responsibilities and avoid unverified authorship claims.', '',
         '## Speaking division', '',
         'Target duration: approximately 12-15 minutes plus Q&A. Allow about 2.5-3 minutes per person. Each slide has a suggested 45-60 seconds, with extra explanation time for the architecture and diagrams.', '',
         '| Speaker | URN | Slides | Assigned responsibility |',
         '|---|---|---|---|']
for member in DATA['team']:
    lines.append(f'| {member[0]} | {member[1]} | {member[3]} | {member[2]} |')
lines += ['', '## Speaker handoffs', '']
for i, member in enumerate(DATA['team']):
    lines += [f'### {member[0]} - slides {member[3]}', '',
              f'Coverage: {focus[i]}.', '', f'Handoff: "{transitions[i]}"', '']

lines += ['## Slide explanations and scripts', '']
for i, slide in enumerate(DATA['slides']):
    member = DATA['team'][i // 3]
    lines += [f'### Slide {i+1}: {slide["title"]}', '',
              f'Speaker: {member[0]} | Suggested time: 45-60 seconds', '',
              f'**Technical explanation:** {explanations[i]}', '',
              '**Suggested script:**', '', slide['script'], '',
              '**Source references:**', '']
    for source in slide['src']:
        lines.append(f'- [{source}](https://github.com/shdbfrz/AI-Powered-Financial-Analyst/blob/develop/{source})')
    lines += ['']

lines += ['## High-level architecture talking points', '',
          '1. Provider adapters isolate external API differences. Existing implementations include Yahoo Finance and Alpha Vantage market data plus NewsAPI news collection.',
          '2. The feature pipeline transforms OHLCV into documented outputs. Local CSV, JSON and Markdown files are current persistence, rather than PostgreSQL records.',
          '3. Model training remains offline in ai/. The serving layer is intended to load versioned model artifacts and invoke inference.',
          '4. Forecasting and FinBERT sentiment are separate analytical inputs to the planned decision engine.',
          '5. The decision engine produces the structured signal, risk, confidence and drivers. The LLM is restricted to narration of that object.',
          '6. FastAPI is the intended application boundary. React consumes the API rather than invoking providers or training code directly.',
          '7. PostgreSQL is intended for durable application entities. Redis is an optional cache or queue. Compose configuration exists, but application integration is missing.', '',
          '## Evaluation questions to prepare for', '',
          '**What is implemented today?** Data collection and feature engineering have substantive code. FastAPI exposes the health route. React renders a scaffold page.', '',
          '**What model accuracy did you achieve?** No forecasting accuracy or investment-return result is established by the inspected source. The committed Sprint 2 sample uses synthetic OHLCV data.', '',
          '**Why use an LLM?** The design uses it to explain structured analytical outputs. It does not independently produce the price forecast or decision signal.', '',
          '**How will you prevent leakage?** Use chronological training and evaluation, exclude target columns from predictors, fit preprocessing on training data only, and lag or exclude centered swing features until their confirmation time.', '',
          '**Is authentication working?** JWT configuration and dependency declarations exist. Auth routes and token verification remain to be implemented.', '',
          '**Is the database implemented?** PostgreSQL and Redis have Compose services. ORM models, database sessions and migrations are absent.', '',
          '**Why does the README say only scaffolding exists?** The main README describes an earlier phase. Sprint 2 module documentation and source show later data-pipeline progress.', '',
          '**What comes next?** Formalize persistence and API contracts, implement leakage-safe model baselines, integrate sentiment and explanations, build the dashboard and verify the full deployment.', '']

(OUT / 'Presentation_Guide.md').write_text('\n'.join(lines), encoding='utf-8')
shutil.copy2(EXPORT / 'AI_Powered_Financial_Analyst.pptx', OUT / 'AI_Powered_Financial_Analyst.pptx')

# The PDF preserves the reviewed slide appearance. All objects remain editable in the PPTX.
pdf = OUT / 'AI_Powered_Financial_Analyst.pdf'
c = canvas.Canvas(str(pdf), pagesize=(960, 540))
c.setTitle('AI-Powered Financial Analyst & Investment Decision Support System')
c.setAuthor('Project presentation team')
for i in range(1, 16):
    c.drawImage(ImageReader(str(EXPORT / f'slide-{i}.png')), 0, 0, width=960, height=540)
    c.showPage()
c.save()

ns = {'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
      'p': 'http://schemas.openxmlformats.org/presentationml/2006/main'}
with zipfile.ZipFile(OUT / 'AI_Powered_Financial_Analyst.pptx') as z:
    slide_names = [n for n in z.namelist() if re.fullmatch(r'ppt/slides/slide\d+\.xml', n)]
    note_names = [n for n in z.namelist() if re.fullmatch(r'ppt/notesSlides/notesSlide\d+\.xml', n)]
    assert len(slide_names) == 15, len(slide_names)
    assert len(note_names) == 15, len(note_names)
    texts = [' '.join(ET.fromstring(z.read(n)).itertext()) for n in slide_names]
    all_text = '\n'.join(texts)
    for member in DATA['team']:
        assert member[0] in all_text, member[0]
        assert member[1] in all_text, member[1]
    native_shapes = sum(len(ET.fromstring(z.read(n)).findall('.//p:sp', ns)) for n in slide_names)
    connectors = sum(len(ET.fromstring(z.read(n)).findall('.//p:cxnSp', ns)) for n in slide_names)
    assert native_shapes > 100
    assert connectors >= 20
    for n in z.namelist():
        if n.endswith('.xml'):
            ET.fromstring(z.read(n))
assert len(PdfReader(pdf).pages) == 15
report = {'slides': 15, 'speaker_notes': 15, 'native_shapes': native_shapes,
          'native_connectors': connectors, 'pdf_pages': 15, 'team_identity_checks': 'passed'}
(ROOT / '.presentation-build' / 'validation.json').write_text(json.dumps(report, indent=2))
print(json.dumps(report))
print('\n'.join(str(p) for p in OUT.iterdir()))
