const data = JSON.parse(document.getElementById("payload").textContent);
const byBook = Object.fromEntries(data.books.map(b => [b.code, b]));
const byChapter = Object.fromEntries(data.chapters.map(c => [c.id, c]));
const byPart = Object.fromEntries(data.parts.map(p => [p.id, p]));
let selected = null;
let readingGoal = null;
let detailView = null;
let detailError = "";

function esc(value) {
  return String(value ?? "").replace(/[&<>"']/g, ch => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
  }[ch]));
}
function statusClass(name) {
  if (!name) return "s-none";
  if (["Idea", "To Design", "Building", "To Review", "Finished"].includes(name))
    return "s-" + name.replace(/ /g, "-");
  return "s-custom";
}
function labelOf(id) {
  if (byChapter[id]) return byChapter[id].title;
  if (byBook[id]) return byBook[id].title;
  if (byPart[id]) return byPart[id].title;
  return id;
}
function fillSelect(el, values, current) {
  values.forEach(v => {
    const o = document.createElement("option");
    o.value = v;
    o.textContent = v;
    if (v === current) o.selected = true;
    el.appendChild(o);
  });
}
const f = data.filters;
fillSelect(document.getElementById("f-book"), data.books.map(b => b.code), f.book);
fillSelect(document.getElementById("f-status"), data.statuses.map(s => s.name), f.status);
const levelOptions = data.level_options || [...new Set(data.chapters.map(c => c.level).filter(Boolean))].sort();
fillSelect(document.getElementById("f-level"), levelOptions, f.level);
const statusNames = data.statuses.map(s => s.name);
const recordNext = () => {
  const url = new URL(window.location.href);
  url.searchParams.set("tab", "records");
  return url.pathname + url.search;
};
document.getElementById("f-presence").value = f.presence;
document.getElementById("f-q").value = f.q;

const legend = document.getElementById("legend");
data.statuses.forEach(s => {
  const span = document.createElement("span");
  span.innerHTML = `<i class="swatch ${statusClass(s.name)}"></i>${esc(s.name)}`;
  legend.appendChild(span);
});

function hardOptional(id) {
  const hard = new Set();
  const optional = new Set();
  const further = new Set();
  if (byChapter[id]) {
    data.prereqs.filter(p => p.chapter === id).forEach(p => {
      (p.kind === "optional" ? optional : hard).add(p.target);
      if (byChapter[p.target]) (p.kind === "optional" ? optional : hard).add(byChapter[p.target].book);
    });
    return {hard, optional, further};
  }
  if (!byBook[id]) return {hard, optional, further};
  const byPre = {};
  data.prereqs.forEach(p => { (byPre[p.chapter] = byPre[p.chapter] || []).push(p); });
  const reqs = {};
  data.requires.forEach(r => { (reqs[r.book] = reqs[r.book] || []).push(r.requires); });
  function markDirect(book, kind) {
    if (!byBook[book] || book === id) return;
    if (kind === "optional") {
      if (!hard.has(book)) optional.add(book);
    } else {
      optional.delete(book);
      hard.add(book);
    }
  }
  (reqs[id] || []).forEach(book => markDirect(book, "hard"));
  const roots = [];
  data.chapters.filter(c => c.book === id && c.presence !== "retired").forEach(c => {
    (byPre[c.id] || []).forEach(p => {
      const tb = bookOf(p.target);
      if (tb === id) return;
      markDirect(tb, p.kind === "optional" ? "optional" : "hard");
      roots.push(p.target);
    });
  });
  const seenCh = new Set();
  const expanded = new Set();
  const queue = [];
  function expandBook(code) {
    if (!byBook[code] || expanded.has(code)) return;
    expanded.add(code);
    queue.push({type: "book", id: code});
  }
  function touch(book, kind) {
    if (!byBook[book] || book === id || hard.has(book)) return;
    if (kind !== "optional") {
      if (optional.has(book)) {
        optional.delete(book);
        hard.add(book);
        return;
      }
      if (!further.has(book)) further.add(book);
      return;
    }
    if (!optional.has(book) && !further.has(book)) further.add(book);
  }
  (reqs[id] || []).forEach(expandBook);
  roots.forEach(ch => {
    if (seenCh.has(ch)) return;
    seenCh.add(ch);
    queue.push({type: "chapter", id: ch});
  });
  while (queue.length) {
    const item = queue.pop();
    if (item.type === "book") {
      (reqs[item.id] || []).forEach(dep => {
        touch(dep, "hard");
        expandBook(dep);
      });
      data.chapters.filter(c => c.book === item.id && c.presence !== "retired").forEach(c => {
        if (seenCh.has(c.id)) return;
        seenCh.add(c.id);
        queue.push({type: "chapter", id: c.id});
      });
      continue;
    }
    (byPre[item.id] || []).forEach(p => {
      const tb = bookOf(p.target);
      if (tb !== bookOf(item.id)) touch(tb, p.kind === "optional" ? "optional" : "hard");
      if (!byChapter[p.target] && !byPart[p.target]) return;
      if (seenCh.has(p.target)) return;
      seenCh.add(p.target);
      queue.push({type: "chapter", id: p.target});
    });
  }
  return {hard, optional, further};
}

let boxMode = "expanded";
let readingWide = false;
let orderZoom = 1;
const ORDER_ZOOM_MIN = 0.35;
let openChapterLists = new Set();
let closedChapterLists = new Set();
let openChapterGoal = null;

function syncBoxButton() {
  const btn = document.getElementById("box-mode");
  if (!btn) return;
  const compressed = boxMode === "compressed";
  btn.textContent = compressed ? "Expand boxes" : "Compress boxes";
  btn.setAttribute("aria-pressed", compressed ? "true" : "false");
}

function paneLimits() {
  const pictures = document.querySelector(".pictures");
  const libCard = document.getElementById("library-card");
  const host = document.getElementById("library");
  const gap = parseFloat(getComputedStyle(pictures).gap) || 16;
  const available = Math.max(0, pictures.clientWidth - gap);
  const cardStyle = getComputedStyle(libCard);
  const hostStyle = getComputedStyle(host);
  const chrome =
    parseFloat(cardStyle.paddingLeft) + parseFloat(cardStyle.paddingRight) +
    parseFloat(cardStyle.borderLeftWidth) + parseFloat(cardStyle.borderRightWidth) +
    parseFloat(hostStyle.paddingLeft) + parseFloat(hostStyle.paddingRight);
  const maxLibCard = available / 1.75;
  return { available, chrome, maxGraph: Math.max(1, maxLibCard - chrome), maxLibCard };
}

function measureWrap() {
  const wrap = document.querySelector("#library .cols");
  const prevWidth = wrap.style.width;
  const prevTransform = wrap.style.transform;
  wrap.style.transform = "none";
  wrap.style.width = "max-content";
  const width = wrap.scrollWidth;
  const height = wrap.offsetHeight;
  wrap.style.width = prevWidth;
  wrap.style.transform = prevTransform;
  return { width, height };
}

const wideIcons = {
  expand: '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M2.5 6.5V2.5h4M9.5 2.5h4v4M13.5 9.5v4h-4M6.5 13.5h-4v-4" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="square"/></svg>',
  restore: '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M6.5 2.5v4h-4M9.5 2.5v4h4M13.5 9.5h-4v4M6.5 13.5v-4h-4" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="square"/></svg>'
};

function syncWideButton() {
  const btn = document.getElementById("reading-wide");
  if (!btn) return;
  const label = readingWide ? "Restore" : "Fill window";
  btn.innerHTML = readingWide ? wideIcons.restore : wideIcons.expand;
  btn.setAttribute("aria-label", label);
  btn.title = label;
  btn.setAttribute("aria-pressed", readingWide ? "true" : "false");
}

function setReadingWide(on) {
  if (readingWide === on) return;
  readingWide = on;
  document.body.classList.toggle("reading-wide", on);
  syncWideButton();
  const chain = document.getElementById("chain");
  if (chain) {
    chain.style.height = "";
    chain.style.maxHeight = "";
  }
  drawReading();
}

function matchReadingHeight() {
  const reading = document.getElementById("reading-card");
  const libCard = document.getElementById("library-card");
  if (!reading || !libCard) return;
  if (readingWide) {
    reading.style.height = "";
    return;
  }
  const next = libCard.offsetHeight + "px";
  if (reading.style.height !== next) reading.style.height = next;
}

function fitPanes() {
  const reading = document.getElementById("reading-card");
  if (readingWide) {
    if (reading) reading.style.height = "";
    placeReading();
    return;
  }
  const wrap = document.querySelector("#library .cols");
  const host = document.getElementById("library");
  const libCard = document.getElementById("library-card");
  const panel = document.getElementById("panel-library");
  if (!wrap || !libCard || !panel.offsetWidth) return;
  const limits = paneLimits();
  panel.classList.toggle("compact", boxMode === "compressed");
  const naturalBox = measureWrap();
  const natural = naturalBox.width;
  let scale = 1;
  let graphW = natural;
  if (natural > limits.maxGraph) {
    scale = limits.maxGraph / natural;
    graphW = limits.maxGraph;
  }
  wrap.style.width = natural + "px";
  wrap.style.transformOrigin = "top left";
  wrap.style.transform = scale < 0.999 ? "scale(" + scale + ")" : "";
  host.style.height = Math.ceil(naturalBox.height * scale + 6) + "px";
  const cardW = Math.min(limits.maxLibCard, Math.ceil(graphW + limits.chrome));
  libCard.style.flex = "0 0 auto";
  libCard.style.width = cardW + "px";
  matchReadingHeight();
  syncBoxButton();
  placeChainScroll();
  placeReading();
}

function placeChainScroll() {
  const chain = document.getElementById("chain");
  const panel = document.getElementById("panel-library");
  if (!chain || !panel.classList.contains("active")) return;
  if (readingWide) {
    if (chain.style.height || chain.style.maxHeight) {
      chain.style.height = "";
      chain.style.maxHeight = "";
    }
    return;
  }
  if (chain.style.height || chain.style.maxHeight) {
    chain.style.height = "";
    chain.style.maxHeight = "";
  }
}

function syncZoomButtons() {
  const out = document.getElementById("zoom-out");
  const inn = document.getElementById("zoom-in");
  if (out) out.disabled = orderZoom <= ORDER_ZOOM_MIN + 0.001;
  if (inn) inn.disabled = orderZoom >= 0.999;
}

function applyOrderZoom(zoom, anchorX, anchorY) {
  const host = document.getElementById("chain");
  const canvas = document.getElementById("order-canvas");
  const stage = document.getElementById("order-stage");
  if (!host || !canvas || !stage) {
    syncZoomButtons();
    return;
  }
  const prev = orderZoom || 1;
  const next = Math.min(1, Math.max(ORDER_ZOOM_MIN, zoom));
  const naturalW = Number(stage.dataset.w);
  const naturalH = Number(stage.dataset.h);
  const rect = host.getBoundingClientRect();
  const localX = anchorX == null ? host.clientWidth / 2 : anchorX - rect.left;
  const localY = anchorY == null ? host.clientHeight / 2 : anchorY - rect.top;
  const contentX = (host.scrollLeft + localX) / prev;
  const contentY = (host.scrollTop + localY) / prev;
  const unchanged = Math.abs(next - prev) < 0.0001 && anchorX == null && anchorY == null;
  orderZoom = next;
  canvas.style.width = Math.ceil(naturalW * next) + "px";
  canvas.style.height = Math.ceil(naturalH * next) + "px";
  stage.style.transform = next === 1 ? "" : "scale(" + next + ")";
  placeReading();
  if (!unchanged) {
    if (!host.classList.contains("center-x")) host.scrollLeft = contentX * next - localX;
    if (!host.classList.contains("center-y")) host.scrollTop = contentY * next - localY;
  }
  syncZoomButtons();
}

function placeReading(retry) {
  const host = document.getElementById("chain");
  const canvas = document.getElementById("order-canvas");
  if (!host) return;
  if (!canvas) {
    host.classList.add("center-x", "center-y");
    return;
  }
  if (!retry && host.clientHeight < 40) {
    requestAnimationFrame(() => placeReading(true));
    return;
  }
  const fitX = canvas.offsetWidth <= host.clientWidth + 1;
  const fitY = canvas.offsetHeight <= host.clientHeight + 1;
  host.classList.toggle("center-x", fitX);
  host.classList.toggle("center-y", fitY);
  if (fitX) host.scrollLeft = 0;
  if (fitY) host.scrollTop = 0;
}

function drawLibrary() {
  const host = document.getElementById("library");
  host.innerHTML = "";
  const incoming = {};
  data.books.forEach(b => incoming[b.code] = []);
  data.requires.forEach(r => { if (incoming[r.book]) incoming[r.book].push(r.requires); });
  const rank = {};
  function depth(code, seen) {
    if (rank[code] != null) return rank[code];
    if (seen.has(code)) return 0;
    seen.add(code);
    const ds = (incoming[code] || []).map(d => depth(d, seen));
    rank[code] = ds.length ? Math.max(...ds) + 1 : 0;
    return rank[code];
  }
  data.books.forEach(b => depth(b.code, new Set()));
  const tracks = [
    ["M0", "M1", "M2"],
    ["M3"],
    ["CM1", "CM2"],
    ["CM3"],
    ["EM"],
    ["TH"],
    ["F1", "F2"],
    ["QM", "QFT"],
    ["GR"],
    ["GLOSSARY"],
  ];
  const ordered = [];
  const seen = new Set();
  tracks.forEach(track => track.forEach(code => {
    if (!byBook[code] || seen.has(code)) return;
    seen.add(code);
    ordered.push(code);
  }));
  const extras = data.books.map(b => b.code).filter(code => !seen.has(code));
  extras.sort((a, b) => (rank[a] - rank[b]) || a.localeCompare(b));
  ordered.push(...extras);
  const marks = selected ? hardOptional(selected) : {hard: new Set(), optional: new Set(), further: new Set()};
  const wrap = document.createElement("div");
  wrap.className = "cols";
  ordered.forEach(code => {
    const b = byBook[code];
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "node " + statusClass(b.editorial_status);
    if (selected === code) btn.classList.add("selected");
    if (marks.hard.has(code)) btn.classList.add("hard");
    else if (marks.optional.has(code)) btn.classList.add("optional");
    else if (marks.further.has(code)) btn.classList.add("further");
    btn.innerHTML = `<strong>${esc(b.code)}</strong><small>${esc(b.title)}</small><span class="all">${esc(b.editorial_status || "")}</span>`;
    btn.addEventListener("click", () => select(code));
    wrap.appendChild(btn);
  });
  host.appendChild(wrap);
  fitPanes();
}

function bookOf(id) {
  return String(id).split("/")[0];
}
function chapterSortKey(id) {
  const match = String(id).match(/\/ch(\d+)/);
  if (match) return [0, Number(match[1])];
  if (byPart[id]) return [1, byPart[id].title];
  return [2, id];
}
function readingModel(id) {
  const goalBook = byChapter[id] ? byChapter[id].book : id;
  const goals = byChapter[id]
    ? [id]
    : data.chapters.filter(c => c.book === id && c.presence !== "retired").map(c => c.id);
  const reqs = {};
  data.requires.forEach(r => { (reqs[r.book] = reqs[r.book] || []).push(r.requires); });
  const whole = new Set();
  (function walk(book, seen) {
    if (seen.has(book)) return;
    seen.add(book);
    (reqs[book] || []).forEach(req => { whole.add(req); walk(req, seen); });
  })(goalBook, new Set());
  const byPre = {};
  data.prereqs.forEach(p => { (byPre[p.chapter] = byPre[p.chapter] || []).push(p); });
  const needed = {};
  const cross = [];
  const seen = new Set(goals);
  const queue = goals.slice();
  while (queue.length) {
    const ch = queue.pop();
    const chBook = byChapter[ch] ? byChapter[ch].book : bookOf(ch);
    (byPre[ch] || []).forEach(p => {
      const tb = bookOf(p.target);
      if (tb === goalBook) {
        if (byChapter[p.target] && !seen.has(p.target)) {
          seen.add(p.target);
          queue.push(p.target);
        }
        return;
      }
      if (tb !== chBook && !(whole.has(tb) && whole.has(chBook))) cross.push([tb, chBook]);
      if (whole.has(tb)) {
        if (byChapter[p.target] && !seen.has(p.target)) {
          seen.add(p.target);
          queue.push(p.target);
        }
        return;
      }
      if (!needed[tb]) needed[tb] = {hard: new Set(), optional: new Set()};
      needed[tb][p.kind === "optional" ? "optional" : "hard"].add(p.target);
      if (byChapter[p.target] && !seen.has(p.target)) {
        seen.add(p.target);
        queue.push(p.target);
      }
    });
  }
  const nodes = new Set([...whole, ...Object.keys(needed), goalBook]);
  const raw = [];
  const seenEdge = new Set();
  function addEdge(a, b) {
    if (a === b || !nodes.has(a) || !nodes.has(b)) return;
    const key = a + ">" + b;
    if (seenEdge.has(key)) return;
    seenEdge.add(key);
    raw.push([a, b]);
  }
  data.requires.forEach(r => addEdge(r.requires, r.book));
  cross.forEach(pair => addEdge(pair[0], pair[1]));
  const adj = {};
  nodes.forEach(n => { adj[n] = new Set(); });
  raw.forEach(([a, b]) => adj[a].add(b));
  function canReach(start, goal) {
    const stack = [...adj[start]];
    const visited = new Set();
    while (stack.length) {
      const node = stack.pop();
      if (node === goal) return true;
      if (visited.has(node)) continue;
      visited.add(node);
      adj[node].forEach(next => stack.push(next));
    }
    return false;
  }
  const edges = raw.filter(([a, b]) => {
    adj[a].delete(b);
    const via = canReach(a, b);
    adj[a].add(b);
    return !via;
  });
  const goalChapters = [...seen].filter(id => byChapter[id] && byChapter[id].book === goalBook);
  goalChapters.sort(compareChapters);
  return {goalBook, whole, needed, goalChapters, nodes: [...nodes], edges};
}

function compareChapters(a, b) {
  const ka = chapterSortKey(a);
  const kb = chapterSortKey(b);
  return ka[0] - kb[0] || (ka[1] < kb[1] ? -1 : ka[1] > kb[1] ? 1 : 0);
}

function neededChapterIds(model, code) {
  if (code === model.goalBook) return model.goalChapters;
  if (model.whole.has(code)) {
    return data.chapters
      .filter(c => c.book === code && c.presence !== "retired")
      .map(c => c.id)
      .sort(compareChapters);
  }
  const info = model.needed[code] || {hard: new Set(), optional: new Set()};
  return [...new Set([...info.hard, ...info.optional])].sort(compareChapters);
}

function orderLayers(cols, edges, bookOrder) {
  const preds = {};
  const succs = {};
  edges.forEach(([src, dst]) => {
    (succs[src] = succs[src] || []).push(dst);
    (preds[dst] = preds[dst] || []).push(src);
  });
  const ranks = Object.keys(cols).map(Number).sort((a, b) => a - b);
  const index = {};
  function reindex() {
    Object.keys(index).forEach(key => { delete index[key]; });
    ranks.forEach(rank => cols[rank].forEach((code, i) => { index[code] = i; }));
  }
  function bary(code, neighbors) {
    const vals = (neighbors || []).filter(n => index[n] != null).map(n => index[n]);
    if (!vals.length) return index[code] || 0;
    return vals.reduce((sum, n) => sum + n, 0) / vals.length;
  }
  reindex();
  for (let pass = 0; pass < 4; pass++) {
    ranks.forEach(rank => {
      cols[rank].sort((a, b) => bary(a, preds[a]) - bary(b, preds[b]) || (bookOrder[a] ?? 99) - (bookOrder[b] ?? 99) || a.localeCompare(b));
      reindex();
    });
    [...ranks].reverse().forEach(rank => {
      cols[rank].sort((a, b) => bary(a, succs[a]) - bary(b, succs[b]) || (bookOrder[a] ?? 99) - (bookOrder[b] ?? 99) || a.localeCompare(b));
      reindex();
    });
  }
  const rankOf = {};
  ranks.forEach(rank => cols[rank].forEach(code => { rankOf[code] = rank; }));
  const snapshot = {...index};
  ranks.forEach((rank, place) => {
    const prev = place ? ranks[place - 1] : null;
    cols[rank].sort((a, b) => {
      const score = code => {
        const neighbors = (preds[code] || []).filter(item => prev != null && rankOf[item] === prev);
        const vals = neighbors.filter(item => snapshot[item] != null).map(item => snapshot[item]);
        const at = vals.length ? vals.reduce((sum, n) => sum + n, 0) / vals.length : (snapshot[code] || 0);
        return at * 100000 + (snapshot[code] || 0);
      };
      return score(a) - score(b) || a.localeCompare(b);
    });
  });
}

function readingArrowPaths(pos, rank, colKeys, edges, boxW, contentBottom) {
  const rankAt = Object.fromEntries(colKeys.map((key, i) => [key, i]));
  const short = [];
  const long = [];
  edges.forEach(([src, dst]) => {
    if (!pos[src] || !pos[dst]) return;
    const span = (rankAt[rank[dst]] ?? 0) - (rankAt[rank[src]] ?? 0);
    if (span < 1) return;
    (span === 1 ? short : long).push([src, dst]);
  });
  function portY(group, side) {
    const buckets = {};
    group.forEach(item => {
      const key = side === "out" ? item[0] : item[1];
      (buckets[key] = buckets[key] || []).push(item);
    });
    const found = {};
    Object.keys(buckets).forEach(key => {
      const items = buckets[key];
      const other = side === "out" ? 1 : 0;
      items.sort((a, b) => pos[a[other]].y - pos[b[other]].y);
      const top = pos[key].y;
      const height = pos[key].h;
      items.forEach((item, i) => {
        if (items.length === 1) found[item.join(">")] = top + height / 2;
        else {
          const margin = Math.min(12, height / 4);
          found[item.join(">")] = top + margin + (height - 2 * margin) * i / (items.length - 1);
        }
      });
    });
    return found;
  }
  const both = short.concat(long);
  const leaveY = portY(both, "out");
  const enterY = portY(both, "in");
  const paths = [];
  short.forEach(([src, dst]) => {
    const x1 = pos[src].x + boxW;
    const y1 = leaveY[src + ">" + dst];
    const x2 = pos[dst].x;
    const y2 = enterY[src + ">" + dst];
    const mid = (x1 + x2) / 2;
    paths.push(`M ${x1} ${y1} C ${mid} ${y1}, ${mid} ${y2}, ${x2} ${y2}`);
  });
  const clearance = 6;
  const laneGap = 11;
  const lowBound = 8;
  const highBound = contentBottom + 12 + Math.max(long.length, 1) * laneGap + 8;
  function freeRows(blockers) {
    const spans = [];
    blockers.forEach(([top, bottom]) => {
      const start = top - clearance;
      const end = bottom + clearance;
      if (end > lowBound && start < highBound) spans.push([Math.max(start, lowBound), Math.min(end, highBound)]);
    });
    spans.sort((a, b) => a[0] - b[0]);
    const merged = [];
    spans.forEach(([start, end]) => {
      if (end <= start) return;
      if (!merged.length || start > merged[merged.length - 1][1]) merged.push([start, end]);
      else merged[merged.length - 1][1] = Math.max(merged[merged.length - 1][1], end);
    });
    const free = [];
    let cursor = lowBound;
    merged.forEach(([start, end]) => {
      if (start - cursor >= 3) free.push([cursor, start]);
      cursor = Math.max(cursor, end);
    });
    if (highBound - cursor >= 3) free.push([cursor, highBound]);
    return free;
  }
  function nearestRow(free, y1, y2) {
    const lo = Math.min(y1, y2);
    const hi = Math.max(y1, y2);
    const mid = (y1 + y2) / 2;
    if (!free.length) return Math.max(mid, contentBottom + 12);
    let bestY = mid;
    let bestKey = null;
    free.forEach(([start, end]) => {
      let y;
      let cost;
      if (end < lo) { y = end; cost = lo - end; }
      else if (start > hi) { y = start; cost = start - hi; }
      else {
        const left = Math.max(start, lo);
        const right = Math.min(end, hi);
        y = Math.min(Math.max(mid, left), right);
        cost = 0;
      }
      const key = cost * 100000 + Math.abs(y - mid);
      if (bestKey == null || key < bestKey) { bestY = y; bestKey = key; }
    });
    return bestY;
  }
  function placeRow(ideal, free, taken) {
    const legal = y => free.some(([start, end]) => y >= start && y <= end) && taken.every(other => Math.abs(y - other) >= laneGap - 0.01);
    if (legal(ideal)) return ideal;
    for (let step = 1; step < 500; step++) {
      if (legal(ideal - step)) return ideal - step;
      if (legal(ideal + step)) return ideal + step;
    }
    if (!free.length) return ideal;
    const span = free.slice().sort((a, b) => {
      const da = ideal < a[0] ? a[0] - ideal : ideal > a[1] ? ideal - a[1] : 0;
      const db = ideal < b[0] ? b[0] - ideal : ideal > b[1] ? ideal - b[1] : 0;
      return da - db;
    })[0];
    return Math.min(Math.max(ideal, span[0]), span[1]);
  }
  const byRank = {};
  Object.keys(rank).forEach(code => {
    if (!pos[code]) return;
    (byRank[rank[code]] = byRank[rank[code]] || []).push(code);
  });
  const ideals = {};
  long.forEach(([src, dst]) => {
    const srcAt = rankAt[rank[src]] ?? 0;
    const dstAt = rankAt[rank[dst]] ?? 0;
    const blockers = [];
    colKeys.forEach(key => {
      const at = rankAt[key];
      if (srcAt < at && at < dstAt) (byRank[key] || []).forEach(code => blockers.push([pos[code].y, pos[code].y + pos[code].h]));
    });
    const y1 = leaveY[src + ">" + dst];
    const y2 = enterY[src + ">" + dst];
    ideals[src + ">" + dst] = {y: nearestRow(freeRows(blockers), y1, y2), free: freeRows(blockers)};
  });
  const channels = {};
  const taken = [];
  long.slice().sort((a, b) => ideals[a[0] + ">" + a[1]].y - ideals[b[0] + ">" + b[1]].y).forEach(([src, dst]) => {
    const picked = ideals[src + ">" + dst];
    channels[src + ">" + dst] = placeRow(picked.y, picked.free, taken);
    taken.push(channels[src + ">" + dst]);
  });
  function sideSlot(index) {
    const groups = {};
    long.forEach(item => { (groups[item[index]] = groups[item[index]] || []).push(item); });
    const found = {};
    Object.keys(groups).forEach(key => {
      groups[key].sort((a, b) => channels[a[0] + ">" + a[1]] - channels[b[0] + ">" + b[1]]);
      groups[key].forEach((item, i) => { found[item[0] + ">" + item[1]] = i; });
    });
    return found;
  }
  const leaveSlot = sideSlot(0);
  const enterSlot = sideSlot(1);
  let low = contentBottom;
  long.forEach(([src, dst]) => {
    const x1 = pos[src].x + boxW;
    const y1 = leaveY[src + ">" + dst];
    const x2 = pos[dst].x;
    const y2 = enterY[src + ">" + dst];
    const channel = channels[src + ">" + dst];
    let leave = x1 + 12 + Math.min(leaveSlot[src + ">" + dst], 6) * 5;
    let enter = x2 - 12 - Math.min(enterSlot[src + ">" + dst], 6) * 5;
    if (enter < leave) {
      leave = (x1 + x2) / 2 - 2;
      enter = (x1 + x2) / 2 + 2;
    }
    low = Math.max(low, y1, y2, channel);
    paths.push(`M ${x1} ${y1} L ${leave} ${y1} L ${leave} ${channel} L ${enter} ${channel} L ${enter} ${y2} L ${x2} ${y2}`);
  });
  return {paths, extra: low <= contentBottom ? 0 : low - contentBottom + 10};
}

function drawReading() {
  const host = document.getElementById("chain");
  const scrollLeft = host.scrollLeft;
  const scrollTop = host.scrollTop;
  host.innerHTML = "";
  host.style.width = "";
  host.style.height = "";
  const goalId = readingGoal || selected;
  const goalBook = goalId && (byBook[goalId] ? goalId : (byChapter[goalId] && byChapter[goalId].book));
  if (!goalBook) {
    const note = document.createElement("p");
    note.className = "note";
    note.textContent = "Click a book.";
    host.appendChild(note);
    host.classList.add("center-x", "center-y");
    return;
  }
  const model = readingModel(goalId);
  if (openChapterGoal !== model.goalBook) {
    openChapterLists = new Set();
    closedChapterLists = new Set();
    openChapterGoal = model.goalBook;
  }
  const bookOrder = Object.fromEntries(data.books.map((b, i) => [b.code, i]));
  const incoming = {};
  model.nodes.forEach(code => { incoming[code] = []; });
  model.edges.forEach(([before, after]) => incoming[after].push(before));
  const rank = {};
  function depth(code, seen) {
    if (rank[code] != null) return rank[code];
    if (seen.has(code)) return 0;
    seen.add(code);
    const ds = incoming[code].map(d => depth(d, seen));
    rank[code] = ds.length ? Math.max(...ds) + 1 : 0;
    return rank[code];
  }
  model.nodes.forEach(code => depth(code, new Set()));
  const cols = {};
  model.nodes.forEach(code => { (cols[rank[code]] = cols[rank[code]] || []).push(code); });
  Object.values(cols).forEach(list => list.sort((a, b) => (bookOrder[a] ?? 99) - (bookOrder[b] ?? 99)));
  orderLayers(cols, model.edges, bookOrder);

  const measure = document.createElement("div");
  measure.style.position = "absolute";
  measure.style.visibility = "hidden";
  measure.style.left = "0";
  host.appendChild(measure);
  const boxes = {};
  model.nodes.forEach(code => {
    const box = document.createElement("div");
    box.className = "order-box " + statusClass((byBook[code] || {}).editorial_status);
    box.dataset.book = code;
    if (code === model.goalBook) box.classList.add("goal");
    const head = document.createElement("button");
    head.type = "button";
    head.className = "book-btn";
    const book = byBook[code];
    head.title = book ? book.title : code;
    head.innerHTML = `<strong>${esc(code)}</strong><small>${esc(book ? book.title : "")}</small>`;
    head.addEventListener("click", () => focusOrderBook(code));
    box.appendChild(head);
    if (code === model.goalBook) {
      const line = document.createElement("p");
      line.className = "all";
      line.textContent = byChapter[goalId] ? byChapter[goalId].title : "Read in chapter order";
      box.appendChild(line);
    } else if (model.whole.has(code)) {
      const line = document.createElement("p");
      line.className = "all";
      line.textContent = "All chapters";
      box.appendChild(line);
    } else {
      const info = model.needed[code] || {hard: new Set(), optional: new Set()};
      const items = [
        ...[...info.hard].map(target => ({target, kind: "hard"})),
        ...[...info.optional].filter(target => !info.hard.has(target)).map(target => ({target, kind: "optional"})),
      ].sort((a, b) => compareChapters(a.target, b.target));
      if (items.some((item, index) => index >= 3 && item.target === goalId) && !closedChapterLists.has(code)) openChapterLists.add(code);
      const open = openChapterLists.has(code);
      if (open) box.classList.add("open");
      const list = document.createElement("ul");
      items.forEach((item, index) => {
        const li = document.createElement("li");
        if (index >= 3) li.classList.add("more");
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "ch-btn" + (item.kind === "optional" ? " optional" : "");
        btn.dataset.id = item.target;
        if (goalId === item.target) btn.classList.add("selected");
        const ch = byChapter[item.target];
        const num = (String(item.target).match(/\/ch(\d+)/) || [])[1];
        const name = ch ? ch.title : (byPart[item.target] ? byPart[item.target].title : item.target);
        btn.innerHTML = `<strong>${esc(num ? "ch" + num : name)}</strong>` + (num ? `<small>${esc(name)}</small>` : "");
        if (ch || byPart[item.target]) btn.addEventListener("click", () => focusOrderBook(code, item.target));
        li.appendChild(btn);
        list.appendChild(li);
      });
      box.appendChild(list);
      if (items.length > 3) {
        const more = document.createElement("button");
        more.type = "button";
        more.className = "more-btn";
        more.setAttribute("aria-expanded", open ? "true" : "false");
        more.setAttribute("aria-label", open ? "Show three chapters" : "Show all chapters");
        more.addEventListener("click", () => {
          if (openChapterLists.has(code)) {
            openChapterLists.delete(code);
            closedChapterLists.add(code);
          } else {
            closedChapterLists.delete(code);
            openChapterLists.add(code);
          }
          drawReading();
        });
        box.appendChild(more);
      }
    }
    measure.appendChild(box);
    boxes[code] = box;
  });
  const boxW = model.nodes.length ? boxes[model.nodes[0]].offsetWidth : 200;
  const colGap = 78;
  const rowGap = 16;
  const pad = 8;
  const heights = {};
  model.nodes.forEach(code => { heights[code] = boxes[code].offsetHeight; });
  const colKeys = Object.keys(cols).map(Number).sort((a, b) => a - b);
  const colX = {};
  const pos = {};
  let x = pad;
  let maxBottom = pad;
  colKeys.forEach(key => {
    colX[key] = x;
    let y = pad;
    cols[key].forEach(code => {
      pos[code] = {x, y, h: heights[code]};
      y += heights[code] + rowGap;
    });
    maxBottom = Math.max(maxBottom, y);
    x += boxW + colGap;
  });
  const width = Math.max(x - colGap + pad, pad + boxW);
  const contentBottom = maxBottom - rowGap;
  const arrowPaths = readingArrowPaths(pos, rank, colKeys, model.edges, boxW, contentBottom);
  const height = Math.max(contentBottom + arrowPaths.extra + pad, pad + 40);
  host.style.width = "";
  host.style.height = "";
  const canvas = document.createElement("div");
  canvas.id = "order-canvas";
  const stage = document.createElement("div");
  stage.id = "order-stage";
  stage.dataset.w = String(width);
  stage.dataset.h = String(height);
  stage.style.width = width + "px";
  stage.style.height = height + "px";
  const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  svg.setAttribute("id", "arrows");
  svg.setAttribute("width", width);
  svg.setAttribute("height", height);
  const defs = document.createElementNS("http://www.w3.org/2000/svg", "defs");
  const marker = document.createElementNS("http://www.w3.org/2000/svg", "marker");
  marker.setAttribute("id", "arr");
  marker.setAttribute("markerWidth", "8");
  marker.setAttribute("markerHeight", "8");
  marker.setAttribute("refX", "7");
  marker.setAttribute("refY", "3");
  marker.setAttribute("orient", "auto");
  const tip = document.createElementNS("http://www.w3.org/2000/svg", "path");
  const arrow = getComputedStyle(document.documentElement).getPropertyValue("--arrow").trim() || "#7c6b58";
  tip.setAttribute("d", "M0,0 L8,3 L0,6 Z");
  tip.setAttribute("fill", arrow);
  marker.appendChild(tip);
  defs.appendChild(marker);
  svg.appendChild(defs);
  arrowPaths.paths.forEach(d => {
    const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
    path.setAttribute("d", d);
    path.setAttribute("fill", "none");
    path.setAttribute("stroke", arrow);
    path.setAttribute("stroke-width", "1.4");
    path.setAttribute("stroke-linejoin", "round");
    path.setAttribute("stroke-linecap", "round");
    path.setAttribute("marker-end", "url(#arr)");
    svg.appendChild(path);
  });
  stage.appendChild(svg);
  model.nodes.forEach(code => {
    const box = boxes[code];
    box.style.left = pos[code].x + "px";
    box.style.top = pos[code].y + "px";
    stage.appendChild(box);
  });
  canvas.appendChild(stage);
  measure.remove();
  host.appendChild(canvas);
  applyOrderZoom(orderZoom);
  fitPanes();
  if (!host.classList.contains("center-x")) host.scrollLeft = scrollLeft;
  if (!host.classList.contains("center-y")) host.scrollTop = scrollTop;
}

