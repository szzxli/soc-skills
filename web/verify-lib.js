/* soc-skills verification packages — shared by index.html and verify.html.
 *
 * A verification package wraps one grading result (profile payload) with a
 * SHA-256 hash of its canonical JSON form. Anyone can recompute the hash and
 * confirm the payload has not been altered since the package was generated.
 *
 * What this proves: the payload contents match the hash in the package, and
 * the payload names the rubric version it was produced against.
 * What it does NOT prove: the identity of the person assessed, that the
 * underlying evidence was genuine, or proctored/certification equivalence.
 * The timestamp inside the payload is self-asserted by the generator.
 */
(function (global) {
  'use strict';

  var PKG_TYPE = 'soc-skills-verification-package';
  var PKG_FORMAT = 1;

  var RUBRIC_LINKS = {
    'v1.2': 'https://github.com/szzxli/soc-skills/blob/main/grader/rubric-prompt.md',
    'v1.1': 'https://github.com/szzxli/soc-skills/blob/main/grader/validation-v1.1.md'
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
        reason: ok ? '' : 'Hash mismatch: the payload has been altered since this package was generated.'
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

  var SocVerify = {
    PKG_TYPE: PKG_TYPE,
    PKG_FORMAT: PKG_FORMAT,
    canonicalize: canonicalize,
    sha256Hex: sha256Hex,
    hashPayload: hashPayload,
    buildPackage: buildPackage,
    verifyPackage: verifyPackage,
    splitLevel: splitLevel,
    rubricLink: rubricLink
  };

  global.SocVerify = SocVerify;
  if (typeof module !== 'undefined' && module.exports) {
    module.exports = SocVerify;
  }
})(typeof window !== 'undefined' ? window : globalThis);
