"""Read-only DOCX/PPTX inventory. Standard library only; no rendering or OCR.

Examples:
  python inspect_ooxml.py draft.docx --output doc-report.json
  python inspect_ooxml.py figures.pptx --include-text --output ppt-report.json

Reports inspect object presence, not technical correctness or visual editability.
Text is omitted unless --include-text is explicitly requested.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
from xml.etree import ElementTree as ET
from zipfile import ZipFile, BadZipFile

NS = {
    'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
    'm': 'http://schemas.openxmlformats.org/officeDocument/2006/math',
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
    'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
    'pr': 'http://schemas.openxmlformats.org/package/2006/relationships',
}

def tag(prefix, name):
    return '{' + NS[prefix] + '}' + name

def local(name):
    return name.rsplit('}', 1)[-1]

def attributes(node):
    return {local(k): v for k, v in node.attrib.items()} if node is not None else {}

def props(node):
    """Preserve raw OOXML units and named attributes, without guessing defaults."""
    return {local(c.tag): attributes(c) for c in node} if node is not None else {}

def digest(data):
    return hashlib.sha256(data).hexdigest()

def media(z, prefix):
    return [{'part': n, 'bytes': z.getinfo(n).file_size, 'sha256': digest(z.read(n))}
            for n in sorted(z.namelist()) if n.startswith(prefix) and not n.endswith('/')]

def docx_report(z, include_text):
    root = ET.fromstring(z.read('word/document.xml'))
    paragraphs = root.findall('.//w:body//w:p', NS)
    records = []
    explicit_numbers, drawing_headings = [], []
    for i, p in enumerate(paragraphs):
        text = ''.join(t.text or '' for t in p.findall('.//w:t', NS))
        style = p.find('w:pPr/w:pStyle', NS)
        record = {
            'index': i,
            'style_id': style.get(tag('w','val')) if style is not None else None,
            'text_characters': len(text),
            'omml_objects': len(p.findall('.//m:oMath', NS)),
            'drawing_objects': len(p.findall('.//w:drawing', NS)),
            'direct_paragraph_properties': props(p.find('w:pPr', NS)),
            'direct_run_properties': [props(n) for n in p.findall('w:r/w:rPr', NS)],
        }
        if include_text:
            record['text'] = text
        if re.match(r'^\s*\[\d{4,}\]', text):
            explicit_numbers.append(i)
        if re.sub(r'\s+', '', text) == '说明书附图':
            drawing_headings.append(i)
        records.append(record)
    styles = []
    if 'word/styles.xml' in z.namelist():
        sroot = ET.fromstring(z.read('word/styles.xml'))
        for s in sroot.findall('w:style', NS):
            name = s.find('w:name', NS)
            base = s.find('w:basedOn', NS)
            styles.append({
                'id': s.get(tag('w','styleId')),
                'type': s.get(tag('w','type')),
                'name': name.get(tag('w','val')) if name is not None else None,
                'based_on': base.get(tag('w','val')) if base is not None else None,
                'paragraph': props(s.find('w:pPr', NS)),
                'run': props(s.find('w:rPr', NS)),
            })
        defaults = sroot.find('w:docDefaults', NS)
        default_properties = ET.tostring(defaults, encoding='unicode') if defaults is not None else None
    else:
        default_properties = None
    return {
        'kind': 'docx',
        'paragraph_count': len(records),
        'omml_object_count': len(root.findall('.//m:oMath', NS)),
        'omml_paragraph_count': len(root.findall('.//m:oMathPara', NS)),
        'drawing_object_count': len(root.findall('.//w:drawing', NS)),
        'media': media(z, 'word/media/'),
        'manual_paragraph_number_indices': explicit_numbers,
        'drawing_section_heading_indices': drawing_headings,
        'sections': [props(n) for n in root.findall('.//w:sectPr', NS)],
        'styles': styles,
        'doc_defaults_xml': default_properties,
        'paragraphs': records,
        'units': 'OOXML raw: w:sz half-points; ind/spacing before/after and page sizes twips; line depends on lineRule.',
        'format_note': 'Direct properties and style inheritance are reported separately. Theme fonts, defaults and renderer behavior still require resolution/visual review.',
    }

def pptx_report(z, include_text):
    names = sorted((n for n in z.namelist() if re.fullmatch(r'ppt/slides/slide\d+\.xml', n)),
                   key=lambda n: int(re.search(r'(\d+)\.xml$', n).group(1)))
    slides = []
    for name in names:
        root = ET.fromstring(z.read(name))
        sp = root.findall('.//p:sp', NS)
        text_shapes = [s for s in sp if s.find('p:txBody//a:t', NS) is not None]
        record = {
            'part': name,
            'native_text_shapes': len(text_shapes),
            'native_custom_geometry_shapes': sum(s.find('p:spPr/a:custGeom', NS) is not None for s in sp),
            'native_preset_geometry_shapes': sum(s.find('p:spPr/a:prstGeom', NS) is not None for s in sp),
            'connectors': len(root.findall('.//p:cxnSp', NS)),
            'pictures': len(root.findall('.//p:pic', NS)),
            'groups': len(root.findall('.//p:grpSp', NS)),
            'graphic_frames': len(root.findall('.//p:graphicFrame', NS)),
        }
        if include_text:
            record['texts'] = [''.join(t.text or '' for t in s.findall('.//a:t', NS)) for s in text_shapes]
        slides.append(record)
    keys = ['native_text_shapes', 'native_custom_geometry_shapes', 'native_preset_geometry_shapes',
            'connectors', 'pictures', 'groups', 'graphic_frames']
    return {
        'kind':'pptx', 'slide_count':len(slides), 'slides':slides,
        'totals':{k:sum(s[k] for s in slides) for k in keys},
        'media':media(z, 'ppt/media/'),
        'editability_note':'Counts prove object types only. Text in pictures or SVG images is not counted as native text. Inspect content, overlap and actual rendered pages before claiming label/line editability.',
    }

def inspect(path, include_text=False):
    with ZipFile(path) as z:
        bad = z.testzip()
        if bad:
            raise ValueError('ZIP CRC failed: ' + bad)
        if 'word/document.xml' in z.namelist():
            report = docx_report(z, include_text)
        elif 'ppt/presentation.xml' in z.namelist():
            report = pptx_report(z, include_text)
        else:
            raise ValueError('Supported input is DOCX or PPTX.')
        report['external_relationships'] = []
        for name in z.namelist():
            if name.endswith('.rels'):
                for r in ET.fromstring(z.read(name)):
                    if r.get('TargetMode') == 'External':
                        item = {'part':name,'type':r.get('Type'),'id':r.get('Id')}
                        if include_text:
                            item['target'] = r.get('Target')
                        report['external_relationships'].append(item)
    report.update({'input_name':path.name, 'input_bytes':path.stat().st_size,
                   'input_sha256':digest(path.read_bytes()), 'zip_crc_ok':True,
                   'text_included':include_text,'rendered':False})
    return report

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input',type=Path)
    parser.add_argument('--output',type=Path)
    parser.add_argument('--include-text',action='store_true')
    parser.add_argument('--overwrite',action='store_true',help='Allow replacing an existing report, never the input.')
    args = parser.parse_args()
    if args.output and args.output.resolve() == args.input.resolve():
        parser.error('The report must not overwrite the source document.')
    if args.output and args.output.exists() and not args.overwrite:
        parser.error('Report exists; use a different path or explicit --overwrite.')
    try:
        report = inspect(args.input,args.include_text)
    except (OSError,BadZipFile,ET.ParseError,ValueError) as exc:
        parser.exit(2, str(exc)+'\n')
    result = json.dumps(report,ensure_ascii=False,indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(result,encoding='utf-8')
        print(json.dumps({'report':str(args.output),'kind':report['kind'],'zip_crc_ok':True},ensure_ascii=False))
    else:
        print(result)

if __name__ == '__main__':
    if hasattr(sys.stdout,'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    main()
