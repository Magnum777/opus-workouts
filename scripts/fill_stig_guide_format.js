const fs = require('fs');
const { parse } = require('csv-parse/sync');
const { PDFDocument, StandardFonts, rgb } = require('pdf-lib');

function sanitize(t) {
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
  console.log('Items: ' + items.length);

  const doc = await PDFDocument.create();
  const font = await doc.embedFont(StandardFonts.Helvetica);
  const fb = await doc.embedFont(StandardFonts.HelveticaBold);
  const PAGE_W = 612, PAGE_H = 792, M = 40, CW = PAGE_W - 2 * M;

  let page, y;
  function np() { page = doc.addPage([PAGE_W, PAGE_H]); y = PAGE_H - M; }

  function draw(text, x, yp, opts = {}) {
    page.drawText(text, { x, y: yp, size: opts.size || 9, font: opts.bold ? fb : font, color: rgb(0,0,0) });
  }

  // Draw a table row with status col + comments col + finding details col
  function drawTableRow(status, comments, findingDetails, colWidths) {
    const cw1 = colWidths[0] || 80;  // Status
    const cw2 = colWidths[1] || 240; // Comments
    const cw3 = colWidths[2] || CW - cw1 - cw2 - 4; // Finding Details
    const lh = 9 * 1.35;
    const x1 = M, x2 = M + cw1 + 2, x3 = M + cw1 + cw2 + 4;

    // Wrap text for each column
    const colTexts = [status, comments, findingDetails];
    const colWidthsArr = [cw1, cw2, cw3];
    
    // Calculate how many lines each column needs
    let maxLines = 1;
    const wrappedLines = [];
    for (let c = 0; c < 3; c++) {
      const clean = sanitize(colTexts[c] || '');
      const words = clean.split(' ');
      let line = '', lines = [];
      for (const w of words) {
        const test = line ? line + ' ' + w : w;
        if (font.widthOfTextAtSize(test, 8) > colWidthsArr[c] - 4) {
          if (line) { lines.push(line); line = w; }
          else { lines.push(test); line = ''; }
        } else line = test;
      }
      if (line) lines.push(line);
      wrappedLines.push(lines.length ? lines : ['']);
      if (lines.length > maxLines) maxLines = lines.length;
    }

    const rowH = Math.max(maxLines * 9 * 1.35 + 6, 20);
    if (!page || y - rowH < M) np();

    // Draw cell borders
    const rowY = y;
    const bx = [x1, x2, x3, M + cw1 + cw2 + cw3 + 4];
    
    // Draw column headers
    const headers = ['Status', 'STIG Comments', 'STIG Finding Details'];
    const hx = [x1 + 2, x2 + 2, x3 + 2];
    
    // Header row
    if (y - 24 < M) np();
    const hdrY = y;
    for (let c = 0; c < 3; c++) {
      draw(headers[c], hx[c], hdrY - 13, { bold: true, size: 9 });
    }
    // Header underline
    page.drawLine({ start: { x: x1, y: hdrY - 20 }, end: { x: bx[3], y: hdrY - 20 }, thickness: 0.8, color: rgb(0,0,0) });
    y = hdrY - 20 - 2;

    // Draw the horizontal line before content
    y = hdrY - 24;
    
    // Draw content with dividers
    // Status col
    const st = sanitize(status || '');
    draw(st, x1 + 2, y - lh, { bold: true, size: 8 });

    // Comments col  
    let my = y;
    const cLines = wrappedLines[1];
    for (const l of cLines) {
      draw(l, x2 + 2, my - lh, { size: 8 });
      my -= lh;
    }

    // Finding Details col
    my = y;
    const dLines = wrappedLines[2];
    for (const l of dLines) {
      draw(l, x3 + 2, my - lh, { size: 8 });
      my -= lh;
    }

    const rowBottom = y - rowH;
    // Vertical dividers
    page.drawLine({ start: { x: x1 - 1, y: hdrY - 18 }, end: { x: x1 - 1, y: rowBottom }, thickness: 0.5, color: rgb(0.5,0.5,0.5) });
    page.drawLine({ start: { x: x2 - 1, y: hdrY - 18 }, end: { x: x2 - 1, y: rowBottom }, thickness: 0.5, color: rgb(0.5,0.5,0.5) });
    page.drawLine({ start: { x: x3 - 1, y: hdrY - 18 }, end: { x: x3 - 1, y: rowBottom }, thickness: 0.5, color: rgb(0.5,0.5,0.5) });
    page.drawLine({ start: { x: bx[3], y: hdrY - 18 }, end: { x: bx[3], y: rowBottom }, thickness: 0.5, color: rgb(0.5,0.5,0.5) });
    // Horizontal bottom
    page.drawLine({ start: { x: x1, y: rowBottom }, end: { x: bx[3], y: rowBottom }, thickness: 0.5, color: rgb(0.5,0.5,0.5) });

    y = rowBottom - 5;
  }

  // ===== BUILD =====
  np();

  // A. Title
  draw('Application Security and Development STIG V6 - Checklist Results', M, y - 14, { bold: true, size: 14 }); y -= 20;
  draw('Application: Appian (Low-Code Platform)', M, y - 12, { bold: true, size: 11 }); y -= 16;
  draw('Benchmark: Application Security and Development STIG, Release 4, Benchmark Date: 01 Oct 2025', M, y - 10, { size: 9 }); y -= 12;
  draw('Version 6 | Classification: Unclassified  ~~~~~~~', M, y - 10, { size: 9 }); y -= 12;
  draw('Date Generated: 2026-06-02', M, y - 10, { size: 9 }); y -= 18;
  
  // Horizontal rule
  page.drawLine({ start: { x: M, y: y }, end: { x: PAGE_W - M, y }, thickness: 1, color: rgb(0.4,0.4,0.4) }); y -= 10;

  // B. Summary / Table of Contents
  draw('SUMMARY / TABLE OF CONTENTS', M, y - 12, { bold: true, size: 12 }); y -= 16;
  page.drawLine({ start: { x: M, y }, end: { x: PAGE_W - M, y }, thickness: 0.5, color: rgb(0.6,0.6,0.6) }); y -= 8;
  
  draw('Total Items (Filtered): 4  |  By Status: 4 Not a Finding, 0 Open', M, y - 10, { size: 9 }); y -= 12;
  const catCounts = { high: 0, medium: 0, low: 0 };
  items.forEach(r => { const s = (r.Severity || '').toLowerCase(); if (catCounts[s] !== undefined) catCounts[s]++; });
  draw('Severity: High(' + catCounts.high + ') Medium(' + catCounts.medium + ') Low(' + catCounts.low + ')', M, y - 10, { size: 9 }); y -= 14;
  
  items.forEach((r, i) => {
    draw((i+1) + '.  ' + r['STIG ID'] + ' - ' + r['Group ID'] + '  |  Severity: ' + r.Severity.toUpperCase() + '  |  ' + r.Status, M + 10, y - 10, { size: 8 });
    y -= 11;
  });
  y -= 5;
  page.drawLine({ start: { x: M, y }, end: { x: PAGE_W - M, y }, thickness: 0.5, color: rgb(0.6,0.6,0.6) }); y -= 10;

  // C. Evidence by Group ID
  items.forEach((r, idx) => {
    const gid = r['Group ID'];
    const stigId = r['STIG ID'];
    const sev = r.Severity;
    const status = r.Status;
    const rule = r['Rule Title'];
    const comments = r.Comments;
    const findingDetails = r['Finding Details'];
    const fixText = r['Fix Text'];
    const discussion = r.Discussion;

    if (y < M + 50) np();

    // Vulnerability header
    draw('________________________________________________________________', M, y - 3, { size: 2 }); y -= 6;
    draw('FINDING ' + (idx+1) + ':  ' + stigId + ' - ' + gid, M, y - 11, { bold: true, size: 11 }); y -= 14;
    draw('Rule Title: ' + rule, M, y - 10, { size: 8 }); y -= 11;
    draw('Severity: ' + sev.toUpperCase() + ' | Status: ' + status + ' | Classification: Unclassified', M, y - 10, { size: 8 }); y -= 12;
    page.drawLine({ start: { x: M, y }, end: { x: PAGE_W - M, y }, thickness: 0.5, color: rgb(0.6,0.6,0.6) }); y -= 6;

    if (status === 'Not a Finding') {
      // Per PIEE Guide: For compliant findings, use the 3-column table format
      const commentText = 'Compliant evidence: ' + comments;
      const findingText = 'Compliance check: ' + findingDetails;
      drawTableRow(status, commentText, findingText, [80, 230, CW - 312]);
    } else if (status === 'Open') {
      const commentText = 'Non-compliant: ' + comments + '. ' + fixText;
      const findingText = 'POAM needed: ' + findingDetails;
      drawTableRow(status, commentText, findingText, [80, 230, CW - 312]);
    } else {
      drawTableRow(status, comments || 'N/A', findingDetails || 'N/A', [80, 230, CW - 312]);
    }

    y -= 5;
  });

  const outPath = 'C:\\Users\\compj\\.openclaw\\media\\outbound\\STIG_APPIAN_Completed_Checklist_4.pdf';
  const outBytes = await doc.save();
  fs.writeFileSync(outPath, outBytes);
  console.log('Output: ' + outPath);
  console.log('Size: ' + (outBytes.length / 1024).toFixed(1) + ' KB, Pages: ' + doc.getPageCount());
}

main().catch(e => { console.error(e.message); process.exit(1); });