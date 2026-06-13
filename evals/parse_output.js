// Shared parser: extract the grader's JSON object from raw model output,
// tolerating markdown fences and surrounding prose.
module.exports = function parseOutput(output) {
  if (typeof output !== 'string') return null;
  const t = output.replace(/```(json)?/g, '').trim();
  const s = t.indexOf('{');
  const e = t.lastIndexOf('}');
  if (s === -1 || e <= s) return null;
  let o;
  try {
    o = JSON.parse(t.slice(s, e + 1));
  } catch {
    return null;
  }
  // Tolerate a common model mistake: "overall" nested inside trait_scores.
  if (o && typeof o.overall !== 'number' && o.trait_scores
      && typeof o.trait_scores.overall === 'number') {
    o.overall = o.trait_scores.overall;
    delete o.trait_scores.overall;
  }
  return o;
};
