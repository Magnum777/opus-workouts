const fs = require('fs');
const { parse } = require('csv-parse/sync');

const csvText = fs.readFileSync('C:\\Users\\compj\\.openclaw\\media\\inbound\\STIG_APPIAN_REVIEWED---3459477b-872a-41b4-8e70-977a42ccc09c.csv', 'utf-8');
const lines = csvText.split(/\r?\n/).filter(l => !l.trim().startsWith('~') && l.trim() !== '');
const records = parse(lines.join('\n'), { columns: true, bom: true, relax_column_count: true });

const targetIds = ['V-222411', 'V-222432', 'V-222520', 'V-222536'];
const filtered = records.filter(r => targetIds.includes(r['Group ID']));

filtered.forEach(r => {
  console.log('=== ' + r['STIG ID'] + ' - ' + r['Group ID'] + ' ===');
  console.log('Severity: ' + r.Severity + ' | Status: ' + r.Status);
  console.log('Rule: ' + r['Rule Title']);
  console.log('');
  console.log('Comments:');
  console.log(r.Comments || '(none)');
  console.log('');
  console.log('Finding Details:');
  console.log(r['Finding Details'] || '(none)');
  console.log('');
  console.log('Fix Text:');
  console.log(r['Fix Text'] || '(none)');
  console.log('');
  console.log('Discussion:');
  console.log(r.Discussion || '(none)');
  console.log('========================================');
  console.log('');
});

console.log('--- Summary ---');
filtered.forEach(r => console.log(r['Group ID'] + ': ' + r.Status));