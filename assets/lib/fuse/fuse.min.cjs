/* Blowfish v3 search compatibility for Hugo's resource minifier. */
(function () {
  function normalize(value) {
    return String(value || "").toLocaleLowerCase();
  }

  function subsequenceScore(text, query) {
    let textIndex = 0;
    let queryIndex = 0;
    let firstMatch = -1;
    let lastMatch = -1;

    while (textIndex < text.length && queryIndex < query.length) {
      if (text[textIndex] === query[queryIndex]) {
        if (firstMatch < 0) firstMatch = textIndex;
        lastMatch = textIndex;
        queryIndex += 1;
      }
      textIndex += 1;
    }

    if (queryIndex !== query.length) return null;
    return (lastMatch - firstMatch + 1 - query.length) / Math.max(text.length, 1) + 0.5;
  }

  function Fuse(list, options) {
    this.list = Array.isArray(list) ? list : [];
    this.keys = (options && options.keys) || [];
  }

  Fuse.prototype.search = function (pattern) {
    const query = normalize(pattern).trim();
    if (!query) return [];

    return this.list
      .map((item, refIndex) => {
        let bestScore = Infinity;

        this.keys.forEach((keyConfig) => {
          const name = typeof keyConfig === "string" ? keyConfig : keyConfig.name;
          const weight = typeof keyConfig === "string" ? 1 : keyConfig.weight || 1;
          const value = normalize(item[name]);
          const exactIndex = value.indexOf(query);

          if (exactIndex >= 0) {
            bestScore = Math.min(bestScore, exactIndex / Math.max(value.length, 1) / weight);
            return;
          }

          const fuzzyScore = subsequenceScore(value, query);
          if (fuzzyScore !== null) bestScore = Math.min(bestScore, fuzzyScore / weight);
        });

        return Number.isFinite(bestScore) ? { item, refIndex, score: bestScore, matches: [] } : null;
      })
      .filter(Boolean)
      .sort((left, right) => left.score - right.score)
      .slice(0, 30);
  };

  module.exports=Fuse;
})();
