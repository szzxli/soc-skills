#!/usr/bin/env node
/* Unit tests for web/verify-lib.js (hash check + public gist anchor).
 * Run: node tests/test_verify_lib.js   (Node 18+, no dependencies)
 * Exits 1 on any failure. */
'use strict';
const path = require('path');
const fs = require('fs');
const V = require(path.join(__dirname, '..', 'web', 'verify-lib.js'));

let fails = 0, passes = 0;
function check(cond, msg) {
  if (cond) { passes++; console.log('PASS ' + msg); }
  else { fails++; console.log('FAIL ' + msg); }
}

const GIST_ID = 'aa5a315d61ae9438b18d';
function gist(over) {
  return Object.assign({
    id: GIST_ID,
    html_url: 'https://gist.github.com/someone/' + GIST_ID,
    public: true,
    created_at: '2026-10-21T10:00:00Z',
    updated_at: '2026-10-21T10:00:00Z',
    owner: { login: 'someone' },
    files: {}
  }, over);
}
function mockFetch(status, body) {
  return function (url) {
    mockFetch.lastUrl = url;
    return Promise.resolve({ status: status, ok: status >= 200 && status < 300,
      json: function () { return Promise.resolve(body); } });
  };
}

(async function main() {
  // --- canonicalize / package round trip ---
  check(V.canonicalize({ b: 1, a: [2, { d: null, c: 'x' }] }) === '{"a":[2,{"c":"x","d":null}],"b":1}',
    'canonicalize sorts keys recursively, keeps array order');
  const sample = JSON.parse(fs.readFileSync(path.join(__dirname, '..', 'web', 'samples', 'sample-package.json'), 'utf8'));
  const r1 = await V.verifyPackage(sample);
  check(r1.ok === true && r1.computed === sample.sha256, 'sample package verifies (hash matches)');

  const edited = JSON.parse(JSON.stringify(sample));
  edited.payload.domains[0].level = 'L3';
  const r2 = await V.verifyPackage(edited);
  check(r2.ok === false && /changed after the hash was made/.test(r2.reason), 'edited payload fails with "changed after the hash was made"');

  // The documented limitation: an editor who also recomputes the hash passes.
  // This is why the wording says "unchanged since the hash was made", not "authentic".
  const forged = await V.buildPackage(edited.payload);
  const r3 = await V.verifyPackage(forged);
  check(r3.ok === true && forged.sha256 !== sample.sha256, 're-hashed edit passes the hash check (not a signature) — anchor needed to detect it');

  const withAnchor = Object.assign({}, sample, { anchor: 'https://gist.github.com/someone/' + GIST_ID });
  check((await V.verifyPackage(withAnchor)).ok === true, 'top-level "anchor" field does not affect the hash');

  check((await V.verifyPackage({ type: 'nope' })).ok === false, 'wrong type rejected');

  // --- parseGistUrl ---
  check(V.parseGistUrl('https://gist.github.com/someone/' + GIST_ID) === GIST_ID, 'parseGistUrl: user/id');
  check(V.parseGistUrl('https://gist.github.com/' + GIST_ID) === GIST_ID, 'parseGistUrl: id only');
  check(V.parseGistUrl('  https://gist.github.com/some-one/' + GIST_ID.toUpperCase() + '/rev123#file-x  ') === GIST_ID, 'parseGistUrl: revision, fragment, whitespace, case');
  check(V.parseGistUrl(GIST_ID) === GIST_ID, 'parseGistUrl: bare id');
  check(V.parseGistUrl('https://github.com/someone/' + GIST_ID) === null, 'parseGistUrl: non-gist host rejected');
  check(V.parseGistUrl('https://gist.github.com.evil.com/x/' + GIST_ID) === null, 'parseGistUrl: look-alike host rejected');
  check(V.parseGistUrl('') === null && V.parseGistUrl(null) === null, 'parseGistUrl: empty rejected');
  check(V.gistApiUrl(GIST_ID) === 'https://api.github.com/gists/' + GIST_ID, 'gistApiUrl points at the public GitHub API');

  // --- anchorText ---
  const at = V.anchorText(sample.sha256.toUpperCase(), sample.payload);
  check(at.indexOf('sha256: ' + sample.sha256) !== -1 && /rubric: v1\.3/.test(at), 'anchorText contains lowercase hash and rubric');

  // --- checkGistAnchor ---
  const h = sample.sha256;
  let a = V.checkGistAnchor(gist({ files: { 'soc-skills.txt': { content: V.anchorText(h, sample.payload) } } }), h);
  check(a.ok && a.found && a.isPublic && !a.edited && a.publicSince === '2026-10-21T10:00:00Z' && a.owner === 'someone' && a.file === 'soc-skills.txt',
    'anchor: public, never-edited gist with the hash -> ok, publicSince = created');
  a = V.checkGistAnchor(gist({ updated_at: '2026-10-25T08:00:00Z', files: { 'a.md': { content: 'hash ' + h.toUpperCase() } } }), h);
  check(a.ok && a.edited && a.publicSince === '2026-10-25T08:00:00Z', 'anchor: edited gist -> publicSince is the LAST edit (conservative)');
  a = V.checkGistAnchor(gist({ public: false, files: { 'a.txt': { content: h } } }), h);
  check(a.found && a.ok && a.isPublic === false && /secret/.test(a.reason), 'anchor: secret gist flagged');
  a = V.checkGistAnchor(gist({ files: { 'a.txt': { content: 'nothing here' } } }), h);
  check(!a.ok && !a.found && /does not contain/.test(a.reason), 'anchor: missing hash -> not found');
  a = V.checkGistAnchor(gist({ files: { 'a.txt': { content: 'ff' + h + '00' } } }), h);
  check(!a.found, 'anchor: hash embedded inside a longer hex string does not count');
  a = V.checkGistAnchor(gist({ files: { 'a.txt': { content: h.slice(0, 63) } } }), h);
  check(!a.found, 'anchor: truncated/partial hash does not count');
  a = V.checkGistAnchor(gist({ files: { 'big.txt': { content: 'x', truncated: true } } }), h);
  check(!a.found && a.truncated && /too large/.test(a.reason), 'anchor: truncated gist file reported');
  check(!V.checkGistAnchor(gist({ files: { 'a': { content: h } } }), 'nothex').ok, 'anchor: invalid package hash rejected');
  check(!V.checkGistAnchor({ message: 'Not Found' }, h).ok, 'anchor: non-gist JSON rejected');

  // --- fetchGistAnchor (mocked network) ---
  a = await V.fetchGistAnchor('https://gist.github.com/someone/' + GIST_ID, h, mockFetch(200, gist({ files: { 'x.txt': { content: h } } })));
  check(a.ok && mockFetch.lastUrl === 'https://api.github.com/gists/' + GIST_ID, 'fetchGistAnchor: 200 -> checked via api.github.com');
  a = await V.fetchGistAnchor(GIST_ID, h, mockFetch(404, {}));
  check(!a.ok && /not found/i.test(a.reason), 'fetchGistAnchor: 404 -> not found');
  a = await V.fetchGistAnchor(GIST_ID, h, mockFetch(403, {}));
  check(!a.ok && /rate limit/i.test(a.reason), 'fetchGistAnchor: 403 -> rate-limit message');
  a = await V.fetchGistAnchor(GIST_ID, h, function () { return Promise.reject(new Error('offline')); });
  check(!a.ok && /offline/.test(a.reason), 'fetchGistAnchor: network error handled');
  a = await V.fetchGistAnchor('https://example.com/x', h, mockFetch(200, {}));
  check(!a.ok && /Not a GitHub gist URL/.test(a.reason), 'fetchGistAnchor: non-gist URL rejected without fetching');

  // --- rubric links pinned per version ---
  check(/rubric-prompt\.md$/.test(V.rubricLink('v1.3')) && /21976d9/.test(V.rubricLink('v1.1')) && /19b8d4f/.test(V.rubricLink('v1.2')),
    'rubricLink: v1.3 -> current file, v1.1/v1.2 pinned to their commits');

  console.log('\n' + (fails ? 'FAILED' : 'OK') + ': ' + passes + ' passed, ' + fails + ' failed');
  process.exit(fails ? 1 : 0);
})().catch(function (e) { console.error(e); process.exit(1); });
