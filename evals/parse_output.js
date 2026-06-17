// Shared parser: extract the grader's JSON object from raw model output,
// tolerating markdown fences and surrounding prose.
module.exports = function parseOutput(output) {
  if (typeof output !== 'string') return null;
  const t = output.replace(/```(json)?/g, '').trim();
  const s = t.indexOf('{');
  if (s === -1) return null;
  let o = null;
  // Greedy first try; then fall back to the first brace-balanced object.
  // Some models (notably Opus) emit a stray premature "}" — e.g.
  // {... "evidence": "..."}, "feedback": "..."} — that breaks a naive
  // first-{ .. last-} slice. The leading balanced object still carries
  // "overall" and "trait_scores" (all the score metrics need).
  try {
    o = JSON.parse(t.slice(s, t.lastIndexOf('}') + 1));
  } catch {
    let depth = 0, inStr = false, esc = false;
    for (let i = s; i < t.length; i++) {
      const c = t[i];
      if (inStr) {
        if (esc) esc = false;
        else if (c === '\\') esc = true;
        else if (c === '"') inStr = false;
      } else if (c === '"') inStr = true;
      else if (c === '{') depth++;
      else if (c === '}' && --depth === 0) {
        try { o = JSON.parse(t.slice(s, i + 1)); } catch { o = null; }
        break;
      }
    }
  }
  if (o === null) return null;
  // Tolerate a common model mistake: "overall" nested inside trait_scores.
  if (o && typeof o.overall !== 'number' && o.trait_scores
      && typeof o.trait_scores.overall === 'number') {
    o.overall = o.trait_scores.overall;
    delete o.trait_scores.overall;
  }
  return o;
};
