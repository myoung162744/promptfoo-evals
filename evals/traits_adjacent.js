const parseOutput = require('./parse_output');

// Per-trait agreement: score = fraction of traits within tolerance of the
// human trait score; passes only if every trait is within tolerance.
// Only meaningful for datasets whose tests carry a `traits` var (ASAP++, ELLIPSE).
module.exports = (output, { vars }) => {
  const o = parseOutput(output);
  if (!o) return { pass: false, score: 0, reason: 'unparseable output' };
  const traits = String(vars.traits || '').split(',').map((x) => x.trim()).filter(Boolean);
  if (!traits.length) return { pass: true, score: 1, reason: 'no traits for this dataset' };
  const tol = Number(vars.tolerance ?? 1);
  const details = [];
  let within = 0;
  for (const tr of traits) {
    const model = o.trait_scores ? Number(o.trait_scores[tr]) : NaN;
    const human = Number(vars['human_' + tr]);
    const ok = Number.isFinite(model) && Math.abs(model - human) <= tol + 1e-9;
    if (ok) within++;
    details.push(`${tr}: ${Number.isFinite(model) ? model : 'missing'} vs ${human}${ok ? '' : ' ✗'}`);
  }
  return {
    pass: within === traits.length,
    score: within / traits.length,
    reason: details.join('; '),
  };
};
