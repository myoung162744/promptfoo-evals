const parseOutput = require('./parse_output');

// Model's overall score within tolerance of the human score
// (tolerance var defaults to 1; ELLIPSE sets 0.5 for its half-point scale).
module.exports = (output, { vars }) => {
  const o = parseOutput(output);
  if (!o || typeof o.overall !== 'number') {
    return { pass: false, score: 0, reason: 'unparseable output' };
  }
  const human = Number(vars.human_overall);
  const tol = Number(vars.tolerance ?? 1);
  const diff = Math.abs(o.overall - human);
  const ok = diff <= tol + 1e-9;
  return {
    pass: ok, score: ok ? 1 : 0,
    reason: `model ${o.overall} vs human ${human} (diff ${diff.toFixed(1)}, tol ${tol})`,
  };
};
