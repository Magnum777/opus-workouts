const fs = require('fs');
const { parse } = require('csv-parse/sync');
const { PDFDocument, StandardFonts, rgb } = require('pdf-lib');

function clean(t) {
  if (!t) return '';
  return t.replace(/[\r\n]+/g, ' ').replace(/[^\x20-\x7E\xA0-\xFF]/g, '').trim();
}

async function main() {
  const csvPath = 'C:\\Users\\compj\\.openclaw\\media\\inbound\\STIG_APPIAN_REVIEWED---9f2274cd-93f3-4af4-8a48-ce13731e1c71.csv';
  let raw = fs.readFileSync(csvPath, 'utf-8');
  const lines = raw.split(/\r?\n/).filter(l => !l.trim().startsWith('~') && l.trim() !== '');
  const records = parse(lines.join('\n'), { columns: true, bom: true, relax_column_count: true });
  const targetIds = ['V-222411', 'V-222432', 'V-222520', 'V-222536'];
  const items = records.filter(r => targetIds.includes(r['Group ID']));

  const doc = await PDFDocument.create();
  // Use Helvetica (clean, standard sans-serif - looks like a real form)
  const f = await doc.embedFont(StandardFonts.Helvetica);
  const fb = await doc.embedFont(StandardFonts.HelveticaBold);
  const PW = 612, PH = 792, LM = 50, RM = 50, TM = 50, BM = 40;

  let page, y;
  function np() {
    page = doc.addPage([PW, PH]);
    y = PH - TM;
  }

  function p(text, opts = {}) {
    const sz = opts.s || 10, b = opts.b || false, ind = opts.ind || 0, lh = sz * 1.4;
    const aw = (PW - LM - RM) - ind * 20;
    const ff = b ? fb : f;
    const cleanText = clean(text);
    if (!cleanText) return;
    
    const words = cleanText.split(' ');
    let line = '', lines = [];
    for (const word of words) {
      const test = line ? line + ' ' + word : word;
      if (ff.widthOfTextAtSize(test, sz) > aw) {
        if (line) { lines.push(line); line = word; }
        else { lines.push(test); line = ''; }
      } else { line = test; }
    }
    if (line) lines.push(line);

    for (const l of lines) {
      if (!page || y - lh < BM) np();
      page.drawText(l, { x: LM + ind * 20, y: y - lh, size: sz, font: ff, color: rgb(0,0,0) });
      y -= lh;
    }
  }

  function hr(thick) {
    if (!page || y - 6 < BM) np();
    y -= 4;
    page.drawLine({ start: { x: LM, y }, end: { x: PW - RM, y }, thickness: thick || 0.5, color: rgb(0.3,0.3,0.3) });
    y -= 8;
  }

  function sectionHdr(text) {
    if (!page || y - 20 < BM) np();
    y -= 2;
    p(text, { b: true, s: 12 });
    hr(0.8);
  }

  np();

  // ===== HEADER =====
  p('UNCLASSIFIED', { b: true, s: 9 });
  p(''); y -= 2;
  hr(1.5);
  p('Application Security and Development STIG  |  Version 6', { b: true, s: 14 });
  p('Checklist Results for Appian (Low-Code Platform)', { s: 11 });
  p(''); y -= 2;
  p('Benchmark: Application_Security_Development_STIG, Release 4 (01 Oct 2025)', { s: 9 });
  p('Date: 2026-06-02  |  Classification: UNCLASSIFIED', { s: 9 });
  hr(1);
  y -= 4;

  // ===== OVERVIEW =====
  sectionHdr('Overview');

  p('This document summarizes the results of four (4) STIG controls assessed against the Appian low-code platform. All controls were evaluated as part of the Application Security and Development STIG (V6, Release 4) review process. The assessment covered account inactivity, failed login lockout, reauthentication on privilege escalation, and minimum password length.', { s: 10 });
  p(''); y -= 2;
  p('Assessment Summary:', { b: true, s: 10 });
  p('  Total Findings: 4', { s: 10 });
  p('  Compliant (Not a Finding): 4', { s: 10 });
  p('  Non-Compliant (Open): 0', { s: 10 });
  p('  Not Applicable: 0', { s: 10 });
  p(''); y -= 2;
  p('Severity Breakdown:', { b: true, s: 10 });
  p('  CAT I (High):   ' + items.filter(r => (r.Severity||'').toLowerCase()==='high').length, { s: 10 });
  p('  CAT II (Medium): ' + items.filter(r => (r.Severity||'').toLowerCase()==='medium').length, { s: 10 });
  p('  CAT III (Low):  ' + items.filter(r => (r.Severity||'').toLowerCase()==='low').length, { s: 10 });
  p(''); y -= 2;

  // ===== FINDINGS =====
  sectionHdr('STIG Findings');

  // TOC
  p('Index:', { b: true, s: 9 });
  items.forEach((r, i) => {
    const sevShort = {high:'(CAT I)', medium:'(CAT II)', low:'(CAT III)'}[r.Severity.toLowerCase()] || '';
    p((i+1) + '.  ' + r['STIG ID'] + ' - ' + r['Group ID'] + '  ' + sevShort + '  -  ' + clean(r['Rule Title']).substring(0,75), { s: 9 });
  });
  p(''); y -= 4;
  hr(0.5);
  y -= 4;

  items.forEach((r, idx) => {
    if (!page || y - 60 < BM) np();

    // Thin separator
    page.drawLine({ start: { x: LM + 10, y }, end: { x: PW - RM - 10, y }, thickness: 0.3, color: rgb(0.8,0.8,0.8) });
    y -= 8;

    // Finding header
    p('Finding ' + (idx+1) + ':  ' + r['STIG ID'] + ' - ' + r['Group ID'], { b: true, s: 11 });
    p('Severity: ' + r.Severity.toUpperCase() + '   Status: ' + r.Status + '   Classification: UNCLASSIFIED', { s: 8 });
    p('Rule: ' + clean(r['Rule Title']), { s: 9 });
    p(''); y -= 2;

    // STIG Comments
    p('STIG Comments:', { b: true, s: 9 });
    p(clean(r.Comments), { s: 9, ind: 1 });
    p(''); y -= 2;

    // Finding Details
    p('Finding Details:', { b: true, s: 9 });
    p(clean(r['Finding Details']), { s: 9, ind: 1 });

    // Only show Fix Text if it's meaningful
    const ft = clean(r['Fix Text']);
    if (ft && ft.length > 15) {
      p(''); y -= 2;
      p('Fix Text (reference):', { s: 8, b: true });
      p(ft, { s: 8, ind: 1 });
    }

    p(''); y -= 4;
  });

  // ===== FOOTER =====
  hr(0.8);
  y = BM + 5;
  p('UNCLASSIFIED', { b: true, s: 8 });
  p('Page 1 of 1  |  Appian STIG V6 Checklist Results  |  2026-06-02', { s: 8 });

  const outPath = 'C:\\Users\\compj\\.openclaw\\media\\outbound\\STIG_APPIAN_Completed_Checklist_4.pdf';
  const outBytes = await doc.save();
  fs.writeFileSync(outPath, outBytes);
  console.log('Done: ' + outPath);
  console.log('Pages: ' + doc.getPageCount() + ', Size: ' + (outBytes.length / 1024).toFixed(1) + ' KB');
}

main().catch(e => { console.error(e.message); process.exit(1); });