const parseOutput = require('./parse_output');

// Format compliance: output is parseable JSON with a numeric "overall".
module.exports = (output) => {
  const o = parseOutput(output);
  if (!o || typeof o.overall !== 'number') {
    return { pass: false, score: 0, reason: 'No parseable JSON with numeric "overall"' };
  }
  return { pass: true, score: 1, reason: `overall=${o.overall}` };
};
