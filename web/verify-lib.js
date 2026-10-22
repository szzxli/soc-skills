/* soc-skills verification packages — shared by index.html and verify.html.
 *
 * A verification package wraps one grading result (profile payload) with a
 * SHA-256 hash of its canonical JSON form. Anyone can recompute the hash.
 *
 * What a matching hash proves: the payload is unchanged since that hash was
 * made. It is NOT a signature: anyone who edits the payload can also recompute
 * the hash, so the check only has teeth when the hash was recorded somewhere
 * independent first (see "public anchor" below).
 * What it does NOT prove: that the content is truthful, who made the package,
 * the identity of the person assessed, that the underlying evidence was
 * genuine, or proctored/certification equivalence. The "issued" time inside
 * the payload is self-asserted by the generator.
 *
 * Public anchor (optional, free, no server): the candidate posts the hash in a
 * public GitHub gist. GitHub records when the gist was created and last
 * edited, so the gist shows the hash was public no later than that date.
 * checkGistAnchor() compares a gist's content and dates against a package.
 */
(function (global) {
  'use strict';

  var PKG_TYPE = 'soc-skills-verification-package';
  var PKG_FORMAT = 1;

  var RUBRIC_LINKS = {
    'v1.3': 'https://github.com/szzxli/soc-skills/blob/main/grader/rubric-prompt.md',
    'v1.2': 'https://github.com/szzxli/soc-skills/blob/19b8d4f/grader/rubric-prompt.md',
    'v1.1': 'https://github.com/szzxli/soc-skills/blob/21976d9/grader/rubric-prompt.md'
  };
  var RUBRIC_DIR = 'https://github.com/szzxli/soc-skills/tree/main/grader';

  /* Canonical JSON: object keys sorted recursively, arrays keep order,
   * no insignificant whitespace. Same input -> same string, everywhere. */
  function canonicalize(value) {
    if (value === null) return 'null';
    var t = typeof value;
    if (t === 'number' || t === 'boolean') return JSON.stringify(value);
    if (t === 'string') return JSON.stringify(value);
    if (Array.isArray(value)) {
      return '[' + value.map(function (v) {
        return canonicalize(v === undefined ? null : v);
      }).join(',') + ']';
    }
    if (t === 'object') {
      var keys = Object.keys(value).filter(function (k) {
        return value[k] !== undefined && typeof value[k] !== 'function';
      }).sort();
      return '{' + keys.map(function (k) {
        return JSON.stringify(k) + ':' + canonicalize(value[k]);
      }).join(',') + '}';
    }
    return 'null';
  }

  function sha256Hex(text) {
    var subtle = global.crypto && global.crypto.subtle;
    if (!subtle) {
      return Promise.reject(new Error('WebCrypto is not available in this browser (a secure context, e.g. HTTPS, is required).'));
    }
    return subtle.digest('SHA-256', new TextEncoder().encode(text)).then(function (buf) {
      var bytes = new Uint8Array(buf);
      var hex = '';
      for (var i = 0; i < bytes.length; i++) {
        hex += ('0' + bytes[i].toString(16)).slice(-2);
      }
      return hex;
    });
  }

  function hashPayload(payload) {
    return sha256Hex(canonicalize(payload));
  }

  /* Build a package object (hash filled in) from a payload object. */
  function buildPackage(payload) {
    return hashPayload(payload).then(function (hex) {
      return {
        type: PKG_TYPE,
        format: PKG_FORMAT,
        payload: payload,
        sha256: hex
      };
    });
  }

  /* Verify a parsed package object. Resolves { ok, computed, claimed, reason }. */
  function verifyPackage(pkg) {
    if (!pkg || typeof pkg !== 'object') {
      return Promise.resolve({ ok: false, reason: 'Package is not a JSON object.' });
    }
    if (pkg.type !== PKG_TYPE) {
      return Promise.resolve({ ok: false, reason: 'Not a soc-skills verification package (missing or wrong "type").' });
    }
    if (!pkg.payload || typeof pkg.payload !== 'object') {
      return Promise.resolve({ ok: false, reason: 'Package has no payload.' });
    }
    if (typeof pkg.sha256 !== 'string' || !/^[0-9a-f]{64}$/i.test(pkg.sha256)) {
      return Promise.resolve({ ok: false, reason: 'Package hash is missing or not a SHA-256 hex string.' });
    }
    return hashPayload(pkg.payload).then(function (computed) {
      var claimed = pkg.sha256.toLowerCase();
      var ok = computed === claimed;
      return {
        ok: ok,
        computed: computed,
        claimed: claimed,
        reason: ok ? '' : 'Hash mismatch: the payload no longer matches the hash written in this package — the file was changed after the hash was made.'
      };
    });
  }

  /* Split a level string like "L2 (lab)" into { level: "L2", scope: "lab" }.
   * Plain levels ("L1+", "L1+*", "—") get scope: null. */
  function splitLevel(s) {
    var str = String(s == null ? '' : s);
    var m = str.match(/^(.+?)\s*\(([^)]+)\)\s*$/);
    if (m) return { level: m[1].trim(), scope: m[2].trim() };
    return { level: str.trim(), scope: null };
  }

  function rubricLink(version) {
    return RUBRIC_LINKS[version] || RUBRIC_DIR;
  }

  /* ---- Public anchor: a GitHub gist that contains the package hash ---- */

  /* Accepts https://gist.github.com/<user>/<id>, https://gist.github.com/<id>,
   * optional trailing /<revision>, #fragment or query, and a bare gist id.
   * Returns the gist id (lowercase hex) or null. */
  function parseGistUrl(input) {
    var s = String(input == null ? '' : input).trim();
    if (!s) return null;
    if (/^[0-9a-f]{20,40}$/i.test(s)) return s.toLowerCase();
    var m = s.match(/^https?:\/\/gist\.github\.com\/(?:[A-Za-z0-9-]+\/)?([0-9a-f]{20,40})(?:[\/?#].*)?$/i);
    return m ? m[1].toLowerCase() : null;
  }

  function gistApiUrl(id) {
    return 'https://api.github.com/gists/' + id;
  }

  /* Text a candidate pastes into a new public gist. */
  function anchorText(sha256, payload) {
    var p = payload || {};
    return 'soc-skills verification package\n' +
      'sha256: ' + String(sha256 || '').toLowerCase() + '\n' +
      (p.rubric ? 'rubric: ' + p.rubric + '\n' : '') +
      (p.kind ? 'kind: ' + p.kind + '\n' : '') +
      'verify: https://szzxli.github.io/soc-skills/web/verify.html\n';
  }

  /* Pure check of a gist API response (JSON object) against a package hash.
   * The hash must appear as a whole 64-hex token in a file's content.
   * Dates come from GitHub's server (created_at / updated_at), not the user.
   * publicSince is the conservative bound: updated_at (the content has been
   * exactly as it is now since at least the last edit). */
  function checkGistAnchor(gist, sha256) {
    var want = String(sha256 || '').toLowerCase();
    var out = { ok: false, found: false, reason: '', owner: null, url: null,
      createdAt: null, updatedAt: null, publicSince: null, edited: false,
      isPublic: null, file: null, truncated: false };
    if (!/^[0-9a-f]{64}$/.test(want)) { out.reason = 'No valid package hash to compare.'; return out; }
    if (!gist || typeof gist !== 'object' || !gist.files) { out.reason = 'Not a GitHub gist response.'; return out; }
    out.owner = gist.owner && gist.owner.login ? gist.owner.login : null;
    out.url = gist.html_url || null;
    out.createdAt = gist.created_at || null;
    out.updatedAt = gist.updated_at || gist.created_at || null;
    out.edited = !!(out.createdAt && out.updatedAt && out.createdAt !== out.updatedAt);
    out.isPublic = gist.public === true;
    var names = Object.keys(gist.files);
    var re = new RegExp('(^|[^0-9a-f])' + want + '($|[^0-9a-f])', 'i');
    for (var i = 0; i < names.length; i++) {
      var f = gist.files[names[i]] || {};
      if (f.truncated) out.truncated = true;
      if (typeof f.content === 'string' && re.test(f.content)) {
        out.found = true; out.file = names[i]; break;
      }
    }
    if (!out.found) {
      out.reason = out.truncated
        ? 'The hash was not found, and a gist file was too large to read in full.'
        : 'This gist does not contain the package hash.';
      return out;
    }
    if (!out.isPublic) {
      out.reason = 'The hash is in the gist, but the gist is secret (unlisted), not public.';
    }
    out.publicSince = out.updatedAt;
    out.ok = true;
    return out;
  }

  /* Fetch a gist from the public GitHub API (no token; 60 requests/hour per
   * IP) and check it. fetchImpl is injectable for tests. */
  function fetchGistAnchor(input, sha256, fetchImpl) {
    var id = parseGistUrl(input);
    if (!id) return Promise.resolve({ ok: false, found: false, reason: 'Not a GitHub gist URL (expected https://gist.github.com/<user>/<id>).' });
    var f = fetchImpl || (global.fetch && global.fetch.bind(global));
    if (!f) return Promise.resolve({ ok: false, found: false, reason: 'fetch is not available.' });
    return f(gistApiUrl(id), { headers: { 'Accept': 'application/vnd.github+json' } }).then(function (r) {
      if (r.status === 404) return { ok: false, found: false, reason: 'Gist not found (deleted, or the URL is wrong).' };
      if (r.status === 403 || r.status === 429) return { ok: false, found: false, reason: 'GitHub API rate limit reached (60 requests/hour per network). Try again later, or open the gist and compare the hash by eye.' };
      if (!r.ok) return { ok: false, found: false, reason: 'GitHub API error: HTTP ' + r.status };
      return r.json().then(function (g) { return checkGistAnchor(g, sha256); });
    }, function (e) {
      return { ok: false, found: false, reason: 'Could not reach the GitHub API: ' + (e && e.message ? e.message : e) };
    });
  }

  var SocVerify = {
    PKG_TYPE: PKG_TYPE,
    PKG_FORMAT: PKG_FORMAT,
    canonicalize: canonicalize,
    sha256Hex: sha256Hex,
    hashPayload: hashPayload,
    buildPackage: buildPackage,
    verifyPackage: verifyPackage,
    splitLevel: splitLevel,
    rubricLink: rubricLink,
    parseGistUrl: parseGistUrl,
    gistApiUrl: gistApiUrl,
    anchorText: anchorText,
    checkGistAnchor: checkGistAnchor,
    fetchGistAnchor: fetchGistAnchor
  };

  global.SocVerify = SocVerify;
  if (typeof module !== 'undefined' && module.exports) {
    module.exports = SocVerify;
  }
})(typeof window !== 'undefined' ? window : globalThis);
