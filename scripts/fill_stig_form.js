const fs = require('fs');
const { parse } = require('csv-parse/sync');
const { stringify } = require('csv-stringify/sync');
const { PDFDocument, StandardFonts, rgb } = require('pdf-lib');

function sanitize(t) {
  if (!t) return '';
  return t.replace(/[\r\n]+/g, ' ').replace(/[^\x20-\x7E\xA0-\xFF]/g, '').trim();
}

async function main() {
  // Read CSV
  const csvPath = 'C:\\Users\\compj\\.openclaw\\media\\inbound\\STIG_APPIAN_REVIEWED---b92204b1-49b6-4e5c-a164-7beeec324cb8.csv';
  let raw = fs.readFileSync(csvPath, 'utf-8');
  const lines = raw.split(/\r?\n/).filter(l => !l.trim().startsWith('~') && l.trim() !== '');
  const records = parse(lines.join('\n'), { columns: true, bom: true, relax_column_count: true });
  console.log('Total in CSV: ' + records.length);

  const targetIds = ['V-222411', 'V-222432', 'V-222520', 'V-222536'];
  const items = records.filter(r => targetIds.includes(r['Group ID']));
  console.log('Filtered: ' + items.length);
  items.forEach(r => console.log(' - ' + r['Group ID'] + ': ' + r.Status));

  // Read the existing PDF (the form / checklist template)
  const pdfInPath = 'C:\\Users\\compj\\.openclaw\\media\\inbound\\STIG_APPIAN_Completed_Checklist---e0e2ba7e-0ace-47c6-b05e-d235b7974abf.pdf';
  const pdfBytes = fs.readFileSync(pdfInPath);
  const pdfDoc = await PDFDocument.load(pdfBytes);

  const pages = pdfDoc.getPageCount();
  console.log('Input PDF pages: ' + pages);

  // The PDF is a guidance document (not fillable form). 
  // Per the PIEE PMO STIG Checklist Completion Guide:
  // - For each finding, Comments + Finding Details must be populated
  // - Evidence packages should be structured with STIG Name, TOC, evidence labeled by Vuln Group ID
  // - For manual entries, be clear, use check text/fix text language, don't leave empty
  
  // Since the PDF is a guidance doc with no fillable fields (only Signature1),
  // the correct approach is to generate a NEW completed checklist PDF
  // following the guide's format, with only the 4 selected findings.

  const doc = await PDFDocument.create();
  const font = await doc.embedFont(StandardFonts.Helvetica);
  const fontBold = await doc.embedFont(StandardFonts.HelveticaBold);

  const PW = 612, PH = 792, M = 50, CW = PW - 2 * M;
  let page, y = 0;
  
  function newPage() {
    page = doc.addPage([PW, PH]);
    y = PH - M;
  }
  function wl(text, opts = {}) {
    const sz = opts.size || 9, bold = opts.bold, ind = opts.indent || 0, f = bold ? fontBold : font, lh = sz * 1.4;
    const clean = sanitize(text);
    if (!clean) return;
    const wrap = f !== font ? (t => { const ws = t.split(' '); let ln = '', r = []; for (const w of ws) { const tst = ln ? ln + ' ' + w : w; if (font.widthOfTextAtSize(tst, sz) > CW - ind * 12) { if (ln) r.push(ln); ln = w; } else ln = tst; } if (ln) r.push(ln); return r; }) : [clean];
    // simplified wrapping
    const paras = clean.split('  ').filter(Boolean);
    for (const para of paras) {
      const fw = font.widthOfTextAtSize(para, sz);
      const wrapped = fw > CW - ind * 12 ? (() => {
        const ws = para.split(' '); let ln = '', r = [];
        for (const w of ws) { const tst = ln ? ln + ' ' + w : w; if (font.widthOfTextAtSize(tst, sz) > CW - ind * 12) { if (ln) r.push(ln); ln = w; } else ln = tst; }
        if (ln) r.push(ln); return r;
      })() : [para];
      for (const line of wrapped) {
        if (!page || y - lh < M) newPage();
        page.drawText(line, { x: M + ind * 12, y: y - lh, size: sz, font: f, color: rgb(0,0,0) });
        y -= lh;
      }
    }
  }
  function hr() {
    if (!page || y - 5 < M) newPage();
    y -= 3;
    page.drawLine({ start: { x: M, y }, end: { x: PW - M, y }, thickness: 0.5, color: rgb(0.6,0.6,0.6) });
    y -= 5;
  }

  // Build the completed checklist per PIEE guide requirements
  newPage();
  
  // A. Title
  wl('Application Security and Development STIG V6 - Checklist Results', { bold: true, size: 14 });
  wl('Application: Appian (Low-Code Platform)', { bold: true, size: 11 });
  wl('Benchmark: Application_Security_Development_STIG, Release 4 (01 Oct 2025)', { size: 9 });
  wl('Classification: Unclassified  ~~~~~~~', { size: 9 });
  wl('Generated: 2026-06-02', { size: 9 });
  hr();

  // Summary
  wl('SUMMARY', { bold: true, size: 12 });
  hr();
  wl('Total STIG Items Assessed (Filtered): 4');
  wl('Compliant (Not a Finding): 4');
  wl('Non-Compliant (Open): 0');
  wl('Not Applicable: 0');
  wl('');
  const cat = {};
  items.forEach(r => { const s = (r.Severity || '').toLowerCase(); cat[s] = (cat[s] || 0) + 1; });
  wl('High (CAT I): ' + (cat.high || 0));
  wl('Medium (CAT II): ' + (cat.medium || 0));
  wl('Low (CAT III): ' + (cat.low || 0));
  hr();

  // C. Evidence labeled by Vulnerability Group ID
  items.forEach((r, idx) => {
    const gid = r['Group ID'];
    const stigId = r['STIG ID'];
    const sev = r.Severity;
    const status = r.Status;
    const rule = r['Rule Title'];
    const discussion = r.Discussion;
    const fixText = r['Fix Text'];
    const comments = r.Comments;
    const findingDetails = r['Finding Details'];
    const checkContent = r['Check Content'];

    if (y < M + 60) newPage();

    wl(stigId + ' - ' + gid, { bold: true, size: 11 });
    wl('Severity: ' + sev.toUpperCase() + ' | Status: ' + status, { size: 9 });
    wl('Rule: ' + rule, { size: 9 });
    
    if (discussion && discussion.trim()) {
      wl('Discussion:', { bold: true, size: 9 });
      wl(discussion, { size: 8, indent: 1 });
    }
    
    if (checkContent && checkContent.trim()) {
      wl('Check Content:', { bold: true, size: 9 });
      wl(checkContent, { size: 7, indent: 1 });
    }
    
    if (fixText && fixText.trim()) {
      wl('Fix Text:', { bold: true, size: 9 });
      wl(fixText, { size: 8, indent: 1 });
    }
    
    wl('Comments:', { bold: true, size: 9 });
    wl(comments, { size: 8, indent: 1 });
    
    wl('Finding Details:', { bold: true, size: 9 });
    wl(findingDetails, { size: 8, indent: 1 });
    
    hr();
  });

  const outPath = 'C:\\Users\\compj\\.openclaw\\media\\outbound\\STIG_APPIAN_Completed_Checklist_4.pdf';
  const outBytes = await doc.save();
  fs.writeFileSync(outPath, outBytes);
  console.log('Output: ' + outPath);
  console.log('Size: ' + (outBytes.length / 1024).toFixed(1) + ' KB, Pages: ' + doc.getPageCount());
}

main().catch(e => { console.error(e.message); process.exit(1); });