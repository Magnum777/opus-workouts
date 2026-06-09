const fs = require('fs');
const path = require('path');
const { parse } = require('csv-parse/sync');
const { PDFDocument, StandardFonts, rgb } = require('pdf-lib');

function sanitizeText(t) {
  if (!t) return '';
  return t.replace(/[\r\n]+/g, ' ').replace(/[^\x20-\x7E\xA0-\xFF]/g, '').trim();
}

async function main() {
  const csvPath = 'C:\\Users\\compj\\.openclaw\\media\\inbound\\STIG_APPIAN_REVIEWED---3459477b-872a-41b4-8e70-977a42ccc09c.csv';
  const pdfOutPath = 'C:\\Users\\compj\\.openclaw\\media\\outbound\\STIG_APPIAN_Completed_Checklist.pdf';

  let csvText = fs.readFileSync(csvPath, 'utf-8');
  const lines = csvText.split(/\r?\n/).filter(l => !l.trim().startsWith('~') && l.trim() !== '');
  csvText = lines.join('\n');

  const records = parse(csvText, { columns: true, bom: true, relax_column_count: true });
  console.log('Parsed ' + records.length + ' records from CSV');

  const statusCounts = {};
  records.forEach(r => {
    const s = r.Status || 'Unknown';
    statusCounts[s] = (statusCounts[s] || 0) + 1;
  });
  console.log('Status breakdown:', JSON.stringify(statusCounts));

  // Create new PDF document
  const doc = await PDFDocument.create();
  const font = await doc.embedFont(StandardFonts.Helvetica);
  const fontBold = await doc.embedFont(StandardFonts.HelveticaBold);

  const PAGE_W = 612;
  const PAGE_H = 792;
  const MARGIN = 50;
  const CONTENT_W = PAGE_W - 2 * MARGIN;

  let currentPage = null;
  let yPos = 0;

  function addPage() {
    currentPage = doc.addPage([PAGE_W, PAGE_H]);
    yPos = PAGE_H - MARGIN;
  }

  function wrapText(text, maxWidth, size) {
    const words = text.split(' ');
    const wrapped = [];
    let line = '';
    for (const word of words) {
      const testLine = line ? line + ' ' + word : word;
      const w = font.widthOfTextAtSize(testLine, size);
      if (w > maxWidth) {
        if (line) { wrapped.push(line); line = word; }
        else { wrapped.push(testLine); line = ''; }
      } else {
        line = testLine;
      }
    }
    if (line) wrapped.push(line);
    return wrapped;
  }

  function writeLine(text, opts) {
    opts = opts || {};
    const size = opts.size || 10;
    const bold = opts.bold || false;
    const indent = opts.indent || 0;
    const maxWidth = opts.maxWidth || CONTENT_W;
    const f = bold ? fontBold : font;
    const lineHeight = size * 1.4;
    const actualWidth = maxWidth - indent * 15;
    const clean = sanitizeText(text);
    if (!clean) return yPos;

    // Split on double spaces for intentional breaks
    const paragraphs = clean.split('  ').filter(Boolean);
    
    for (const para of paragraphs) {
      const fw = font.widthOfTextAtSize(para, size);
      const wrappedLines = fw > actualWidth ? wrapText(para, actualWidth, size) : [para];

      for (const line of wrappedLines) {
        if (!currentPage || yPos - lineHeight < MARGIN) {
          addPage();
        }
        currentPage.drawText(line, {
          x: MARGIN + indent * 15,
          y: yPos - lineHeight,
          size: size,
          font: f,
          color: rgb(0, 0, 0),
        });
        yPos -= lineHeight;
      }
      // small gap between paragraphs
      yPos -= 2;
    }
    return yPos;
  }

  function writeHR() {
    if (!currentPage) addPage();
    if (yPos - 5 < MARGIN) addPage();
    yPos -= 5;
    currentPage.drawLine({
      start: { x: MARGIN, y: yPos },
      end: { x: PAGE_W - MARGIN, y: yPos },
      thickness: 1,
      color: rgb(0.5, 0.5, 0.5),
    });
    yPos -= 5;
  }

  // ========= BUILD REPORT =========
  addPage();

  writeLine('Application Security and Development STIG V6 - Checklist Results', { bold: true, size: 14 });
  writeLine('Application: Appian (Low-Code Platform)', { bold: true, size: 11 });
  writeLine('Benchmark: Application_Security_Development_STIG, Release 4 (01 Oct 2025)', { size: 9 });
  writeLine('Classification: Unclassified', { size: 9 });
  const now = new Date();
  writeLine('Generated: ' + now.toISOString().split('T')[0], { size: 9 });
  writeHR();

  // Summary
  writeLine('SUMMARY', { bold: true, size: 13 });
  writeHR();
  const openCount = records.filter(r => r.Status === 'Open').length;
  const nafCount = records.filter(r => r.Status === 'Not a Finding').length;
  const naCount = records.filter(r => r.Status === 'Not Applicable').length;
  const catI = records.filter(r => (r.Severity || '').toLowerCase() === 'high').length;
  const catII = records.filter(r => (r.Severity || '').toLowerCase() === 'medium').length;
  const catIII = records.filter(r => (r.Severity || '').toLowerCase() === 'low').length;

  writeLine('Total STIG Items Assessed: ' + records.length);
  writeLine('Compliant (Not a Finding): ' + nafCount);
  writeLine('Non-Compliant (Open): ' + openCount);
  writeLine('Not Applicable: ' + naCount);
  writeLine('');
  writeLine('Severity Breakdown (All Items):');
  writeLine('  High (CAT I):   ' + catI);
  writeLine('  Medium (CAT II): ' + catII);
  writeLine('  Low (CAT III):  ' + catIII);
  writeHR();

  // Detailed Findings
  records.forEach((r, idx) => {
    const groupId = r['Group ID'] || 'N/A';
    const stigId = r['STIG ID'] || 'N/A';
    const severity = r.Severity || 'N/A';
    const status = r.Status || 'N/A';
    const ruleTitle = r['Rule Title'] || '';
    const comments = r.Comments || '';
    const findingDetails = r['Finding Details'] || '';
    const sevOverride = r['Severity Override'] || '';

    // Estimate page break
    const estLines = 4 + Math.ceil(comments.length / 60) + Math.ceil(findingDetails.length / 60);
    if (yPos < MARGIN + estLines * 12) {
      addPage();
    }

    writeLine(stigId + ' - ' + groupId, { bold: true, size: 11 });
    writeLine('Severity: ' + severity.toUpperCase() + ' | Status: ' + status, { size: 9 });
    if (sevOverride && sevOverride.trim()) {
      writeLine('Severity Override: ' + sevOverride, { size: 9 });
    }
    writeLine('Rule: ' + ruleTitle, { size: 9, maxWidth: CONTENT_W });

    // Comments section
    if (comments && comments.trim()) {
      writeLine('Comments:', { bold: true, size: 9 });
      writeLine(comments, { size: 8, indent: 1, maxWidth: CONTENT_W });
    }

    // Finding Details section
    if (findingDetails && findingDetails.trim()) {
      writeLine('Finding Details:', { bold: true, size: 9 });
      writeLine(findingDetails, { size: 8, indent: 1, maxWidth: CONTENT_W });
    }

    writeHR();
  });

  // Write output
  const outDir = path.dirname(pdfOutPath);
  if (!fs.existsSync(outDir)) {
    fs.mkdirSync(outDir, { recursive: true });
  }

  const outBytes = await doc.save();
  fs.writeFileSync(pdfOutPath, outBytes);
  console.log('\nWritten to: ' + pdfOutPath);
  console.log('File size: ' + (outBytes.length / 1024).toFixed(1) + ' KB');
  console.log('Pages: ' + doc.getPageCount());
}

main().catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});