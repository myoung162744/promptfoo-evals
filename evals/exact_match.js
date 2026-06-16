const parseOutput = require('./parse_output');

// Model's overall score exactly equals the human score.
module.exports = (output, { vars }) => {
  const o = parseOutput(output);
  if (!o || typeof o.overall !== 'number') {
    return { pass: false, score: 0, reason: 'unparseable output' };
  }
  const human = Number(vars.human_overall);
  const exact = Math.abs(o.overall - human) < 1e-9;
  return { pass: exact, score: exact ? 1 : 0, reason: `model ${o.overall} vs human ${human}` };
};
