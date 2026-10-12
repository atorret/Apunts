function showTab(name, options) {
  options = options || {};
  if (name !== "library" && readingWide) {
    readingWide = false;
    document.body.classList.remove("reading-wide");
    syncWideButton();
  }
  ["library", "records", "files"].forEach(tab => {
    document.getElementById("panel-" + tab).classList.toggle("active", tab === name);
    document.querySelector('nav.tabs button[data-tab="' + tab + '"]').setAttribute("aria-selected", tab === name ? "true" : "false");
  });
  const url = new URL(window.location.href);
  if (name === "library") url.searchParams.delete("tab");
  else url.searchParams.set("tab", name);
  if (!options.keepNotice) {
    url.searchParams.delete("notice");
    url.searchParams.delete("error");
  }
  history.replaceState(null, "", url);
  if (name === "library" && !options.skipDraw) drawReading();
}

function namedSelect(values, current, label) {
  const sel = document.createElement("select");
  sel.setAttribute("aria-label", label);
  if (!current) {
    const blank = document.createElement("option");
    blank.value = "";
    blank.textContent = "—";
    blank.selected = true;
    sel.appendChild(blank);
  }
  const choices = current && !values.includes(current) ? [current, ...values] : values;
  choices.forEach(v => {
    const o = document.createElement("option");
    o.value = v;
    o.textContent = v;
    if (v === current) o.selected = true;
    sel.appendChild(o);
  });
  return sel;
}

function levelChoices(current) {
  const sel = document.createElement("select");
  sel.setAttribute("aria-label", "Level");
  const blank = document.createElement("option");
  blank.value = "";
  blank.textContent = "—";
  if (!current) blank.selected = true;
  sel.appendChild(blank);
  optionList(levelOptions, current).forEach(v => {
    const o = document.createElement("option");
    o.value = v;
    o.textContent = v;
    if (v === current) o.selected = true;
    sel.appendChild(o);
  });
  return sel;
}

function applyLocal(id, fields) {
  const chapter = byChapter[id];
  if (chapter) {
    if (fields.presence) chapter.presence = fields.presence;
    if (chapter.presence === "retired") chapter.editorial_status = "";
    else if (fields.status) chapter.editorial_status = fields.status;
    if (fields.level != null) chapter.level = fields.level;
    return;
  }
  const book = byBook[id];
  if (!book) return;
  if (fields.status) book.editorial_status = fields.status;
  if (fields.level != null) book.target_level = fields.level;
  data.chapters.filter(c => c.book === id).forEach(ch => {
    if (fields.presence) ch.presence = fields.presence;
    if (fields.status) ch.editorial_status = ch.presence === "retired" || fields.presence === "retired" ? "" : fields.status;
    if (fields.level != null) ch.level = fields.level;
  });
}

function refreshOrderColors() {
  const drop = ["s-Idea", "s-To-Design", "s-Building", "s-To-Review", "s-Finished", "s-custom", "s-none"];
  document.querySelectorAll(".order-box").forEach(box => {
    const book = byBook[box.dataset.book];
    if (!book) return;
    box.classList.remove(...drop);
    box.classList.add(statusClass(book.editorial_status));
  });
}

async function saveRecord(id, fields) {
  const chapter = byChapter[id];
  const book = byBook[id];
  const body = new URLSearchParams();
  body.set("id", id);
  body.set("next", "/");
  if (fields.presence) body.set("presence", fields.presence);
  if (fields.status) body.set("status", fields.status);
  const level = fields.level != null
    ? fields.level
    : (chapter ? (chapter.level || "") : (book ? (book.target_level || "") : null));
  if (level != null) body.set("level", level);
  const view = detailView;
  let res;
  try {
    res = await fetch("/record", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body,
      redirect: "manual"
    });
  } catch (err) {
    detailError = "Could not save.";
    if (view) fillDetail(view.id, view.limitIds, view.note);
    return;
  }
  const ok = res.type === "opaqueredirect" || (res.status >= 200 && res.status < 400);
  if (!ok) {
    detailError = (await res.text()) || "Could not save.";
    if (view) fillDetail(view.id, view.limitIds, view.note);
    return;
  }
  applyLocal(id, fields);
  if (byBook[id]) {
    drawLibrary();
    refreshOrderColors();
  }
  if (view) fillDetail(view.id, view.limitIds, view.note);
}

function fillDetail(id, limitIds, note) {
  const box = document.getElementById("detail-body");
  const kept = box.querySelector(".ch-list");
  const scroll = kept ? kept.scrollTop : 0;
  detailView = { id, limitIds: limitIds || null, note: note || "" };
  const chapter = byChapter[id];
  const book = byBook[id] || (chapter && byBook[chapter.book]);
  const part = byPart[id];
  box.innerHTML = "";
  if (!chapter && !book) {
    box.innerHTML = `<p>${esc(part ? part.title : id)}</p>`;
    return;
  }
  if (detailError) {
    const err = document.createElement("p");
    err.className = "note detail-error";
    err.textContent = detailError;
    box.appendChild(err);
    detailError = "";
  }
  const head = document.createElement("div");
  head.className = "detail-head";
  const h = document.createElement("h2");
  h.textContent = id;
  const title = document.createElement("p");
  title.textContent = (chapter || book).title;
  head.appendChild(h);
  head.appendChild(title);
  box.appendChild(head);
  if (book) {
    const facts = document.createElement("div");
    facts.className = "book-facts";
    const statusLabel = document.createElement("label");
    statusLabel.textContent = "Book status";
    const statusSel = namedSelect(statusNames, book.editorial_status || "", "Book status");
    statusSel.addEventListener("change", () => saveRecord(book.code, { status: statusSel.value }));
    statusLabel.appendChild(statusSel);
    const levelLabel = document.createElement("label");
    levelLabel.textContent = "Target level";
    const levelSel = levelChoices(book.target_level || "");
    levelSel.setAttribute("aria-label", "Target level");
    levelSel.addEventListener("change", () => saveRecord(book.code, { level: levelSel.value }));
    levelLabel.appendChild(levelSel);
    const entry = document.createElement("p");
    entry.className = "note";
    entry.textContent = "Entry level: " + (book.entry_level || "—");
    facts.appendChild(statusLabel);
    facts.appendChild(levelLabel);
    facts.appendChild(entry);
    box.appendChild(facts);
    if (book.notes) {
      const notes = document.createElement("details");
      const summary = document.createElement("summary");
      summary.textContent = "Notes";
      const body = document.createElement("p");
      body.className = "note";
      body.textContent = book.notes;
      notes.appendChild(summary);
      notes.appendChild(body);
      box.appendChild(notes);
    }
  }
  if (chapter && (chapter.explain || "").trim()) {
    const explain = document.createElement("details");
    explain.open = true;
    const summary = document.createElement("summary");
    summary.textContent = "What to explain";
    const body = document.createElement("p");
    body.className = "note explain-brief";
    body.textContent = chapter.explain;
    explain.appendChild(summary);
    explain.appendChild(body);
    box.appendChild(explain);
  }
  const ids = limitIds
    ? limitIds.slice()
    : (byBook[id]
      ? data.chapters.filter(c => c.book === id).map(c => c.id).sort(compareChapters)
      : (chapter ? [chapter.id] : []));
  if (!ids.length) return;
  const section = document.createElement("section");
  section.className = "detail-chapters";
  if (note) {
    const caption = document.createElement("p");
    caption.className = "note";
    caption.textContent = note;
    section.appendChild(caption);
  }
  const list = document.createElement("div");
  list.className = "ch-list";
  const header = document.createElement("div");
  header.className = "ch-line head";
  ["Chapter", "Title", "Presence", "Status", "Level"].forEach(text => {
    const span = document.createElement("span");
    span.textContent = text;
    header.appendChild(span);
  });
  list.appendChild(header);
  ids.forEach(chId => {
    const ch = byChapter[chId];
    const partRow = byPart[chId];
    if (!ch && !partRow) return;
    const row = document.createElement("div");
    row.className = "ch-line" + (chId === id ? " selected" : "");
    const num = (String(chId).match(/\/ch(\d+)/) || [])[1];
    const idBtn = document.createElement("button");
    idBtn.type = "button";
    idBtn.className = "ch-title ch-id" + (ch && ch.presence === "retired" ? " retired" : "");
    idBtn.textContent = num ? "ch" + num : (partRow ? partRow.title : chId);
    if (ch || partRow) idBtn.addEventListener("click", () => select(chId));
    const name = document.createElement("span");
    name.textContent = ch ? ch.title : "";
    if (ch && ch.presence === "retired") name.className = "retired";
    row.appendChild(idBtn);
    row.appendChild(name);
    if (!ch) {
      list.appendChild(row);
      return;
    }
    const presence = namedSelect(["absent", "present", "retired"], ch.presence || "absent", "Presence");
    const status = namedSelect(statusNames, ch.editorial_status || "", "Status");
    status.disabled = ch.presence === "retired";
    const level = levelChoices(ch.level || "");
    presence.addEventListener("change", () => {
      const retired = presence.value === "retired";
      status.disabled = retired;
      const fields = { presence: presence.value };
      if (!retired) {
        if (!status.value && statusNames.length) status.value = statusNames[0];
        fields.status = status.value;
      }
      saveRecord(ch.id, fields);
    });
    status.addEventListener("change", () => saveRecord(ch.id, { status: status.value }));
    level.addEventListener("change", () => saveRecord(ch.id, { level: level.value }));
    row.appendChild(presence);
    row.appendChild(status);
    row.appendChild(level);
    list.appendChild(row);
  });
  section.appendChild(list);
  box.appendChild(section);
  list.scrollTop = scroll;
}

function focusOrderBook(code, chapterId) {
  const goalId = readingGoal || selected;
  if (!goalId || !byBook[code]) return;
  const model = readingModel(goalId);
  const ids = neededChapterIds(model, code);
  const goal = byBook[model.goalBook];
  const note = code === model.goalBook
    ? "Chapters needed in this book."
    : "Chapters needed for " + (goal ? goal.title : model.goalBook) + ".";
  document.querySelectorAll(".order-box").forEach(box => {
    box.classList.toggle("picked", box.dataset.book === code);
  });
  document.querySelectorAll(".order-box .ch-btn").forEach(btn => {
    btn.classList.toggle("selected", !!chapterId && btn.dataset.id === chapterId);
  });
  fillDetail(chapterId || code, ids, note);
}

function select(id) {
  selected = id;
  readingGoal = id;
  showTab("library");
  drawLibrary();
  fillDetail(id);
}

function optionList(values, current) {
  const set = new Set(values);
  if (current) set.add(current);
  return [...set].sort((a, b) => a.localeCompare(b));
}
function addPresenceSelect(current, allowUnset) {
  const sel = document.createElement("select");
  sel.name = "presence";
  if (allowUnset) {
    const o = document.createElement("option");
    o.value = "";
    o.textContent = "—";
    o.selected = true;
    sel.appendChild(o);
  }
  ["absent", "present", "retired"].forEach(v => {
    const o = document.createElement("option");
    o.value = v;
    o.textContent = v;
    if (v === current) o.selected = true;
    sel.appendChild(o);
  });
  return sel;
}
function addStatusSelect(current, retired) {
  const sel = document.createElement("select");
  sel.name = "status";
  if (!current) {
    const blank = document.createElement("option");
    blank.value = "";
    blank.textContent = "—";
    blank.selected = true;
    sel.appendChild(blank);
  }
  statusNames.forEach(v => {
    const o = document.createElement("option");
    o.value = v;
    o.textContent = v;
    if (v === current) o.selected = true;
    sel.appendChild(o);
  });
  sel.disabled = retired;
  if (!retired) sel.addEventListener("change", () => sel.form.requestSubmit());
  return sel;
}
function addLevelSelect(current) {
  const sel = document.createElement("select");
  sel.name = "level";
  const o0 = document.createElement("option");
  o0.value = "";
  o0.textContent = "—";
  if (!current) o0.selected = true;
  sel.appendChild(o0);
  optionList(levelOptions, current).forEach(v => {
    const o = document.createElement("option");
    o.value = v;
    o.textContent = v;
    if (v === current) o.selected = true;
    sel.appendChild(o);
  });
  sel.addEventListener("change", () => sel.form.requestSubmit());
  return sel;
}
let recordSeq = 0;
function addEditableRow(kind, id, title, presence, status, level, mixedPresence) {
  const form = document.createElement("form");
  form.setAttribute("id", "record-form-" + (++recordSeq));
  form.method = "post";
  form.action = "/record";
  form.appendChild(Object.assign(document.createElement("input"), {type: "hidden", name: "id", value: id}));
  form.appendChild(Object.assign(document.createElement("input"), {type: "hidden", name: "next", value: recordNext()}));
  document.getElementById("record-forms").appendChild(form);
  const tr = document.createElement("tr");
  const tdKind = document.createElement("td");
  tdKind.textContent = kind;
  tr.appendChild(tdKind);
  const tdId = document.createElement("td");
  const idBtn = document.createElement("button");
  idBtn.type = "button";
  idBtn.textContent = id;
  idBtn.addEventListener("click", () => select(id));
  tdId.appendChild(idBtn);
  tr.appendChild(tdId);
  const tdTitle = document.createElement("td");
  tdTitle.textContent = title;
  tr.appendChild(tdTitle);
  const retired = !mixedPresence && presence === "retired";
  const presSel = addPresenceSelect(mixedPresence ? "" : (presence || "absent"), mixedPresence);
  const statSel = addStatusSelect(status || "", retired);
  const levelSel = addLevelSelect(level || "");
  [presSel, statSel, levelSel].forEach(sel => sel.setAttribute("form", form.getAttribute("id")));
  const tdPres = document.createElement("td");
  tdPres.appendChild(presSel);
  tr.appendChild(tdPres);
  const tdStat = document.createElement("td");
  tdStat.appendChild(statSel);
  tr.appendChild(tdStat);
  const tdLvl = document.createElement("td");
  tdLvl.appendChild(levelSel);
  tr.appendChild(tdLvl);
  presSel.addEventListener("change", () => {
    const nowRetired = presSel.value === "retired";
    statSel.disabled = nowRetired;
    if (!nowRetired && !statSel.value && statusNames.length) statSel.value = statusNames[0];
    form.requestSubmit();
  });
  document.getElementById("rows").appendChild(tr);
}
function uniformChapterField(bookCode, field) {
  const vals = data.chapters.filter(c => c.book === bookCode).map(c => c[field]);
  if (!vals.length) return "";
  const first = vals[0];
  return vals.every(v => v === first) ? (first || "") : "";
}
function addReadOnlyRow(kind, id, title) {
  const tr = document.createElement("tr");
  tr.innerHTML = `<td>${esc(kind)}</td><td><button type="button">${esc(id)}</button></td><td>${esc(title)}</td><td></td><td></td><td></td>`;
  tr.querySelector("button").addEventListener("click", () => select(id));
  document.getElementById("rows").appendChild(tr);
}
data.visible.books.forEach(code => {
  const b = byBook[code];
  const presUniform = uniformChapterField(code, "presence");
  const hasCh = data.chapters.some(c => c.book === code);
  addEditableRow(
    "book", b.code, b.title,
    presUniform,
    b.editorial_status || "",
    b.target_level || "",
    hasCh && !presUniform
  );
});
const listedParts = data.parts.filter(p => {
  const f = data.filters;
  if (f.presence || f.status || f.level) return false;
  if (f.book && p.book !== f.book) return false;
  const blob = (p.title + " " + p.id).toLowerCase();
  return !f.q || blob.includes(f.q);
});
listedParts.forEach(p => addReadOnlyRow("part", p.id, p.title));
data.visible.chapters.forEach(id => {
  const c = byChapter[id];
  addEditableRow("chapter", c.id, c.title, c.presence, c.editorial_status || "", c.level || "");
});
data.visible.concepts.forEach(slug => {
  const c = data.concepts.find(x => x.slug === slug);
  const owners = data.links.filter(l => l.concept === slug && l.role === "owner").map(l => l.target).join(", ");
  addReadOnlyRow("concept", c.slug, c.title + (owners ? " — " + owners : ""));
});
data.visible.roadmaps.forEach(id => {
  const r = data.roadmaps.find(x => x.id === id);
  addReadOnlyRow("roadmap", r.id, r.title);
});
const counts = [
  data.visible.books.length,
  listedParts.length,
  data.visible.chapters.length,
  data.visible.concepts.length,
  data.visible.roadmaps.length
];
document.getElementById("record-count").textContent = counts.every(n => n === 0)
  ? "Nothing matches these filters."
  : `${counts[0]} books, ${counts[1]} parts, ${counts[2]} chapters, ${counts[3]} concepts, ${counts[4]} roadmaps`;

function orgPath(code) {
  const book = byBook[code];
  const folder = book && book.folder ? String(book.folder).replace(/\\/g, "/").replace(/^\/+|\/+$/g, "") : "";
  return (folder || code) + "/" + code + "-organization.md";
}
function optionHint(select, value) {
  const opt = [...select.options].find(item => item.value === value);
  return opt && opt.title ? opt.title : "";
}
function enhanceCombo(select) {
  const wrap = document.createElement("div");
  wrap.className = "combo";
  wrap.id = select.id + "-combo";
  select.parentNode.insertBefore(wrap, select);
  wrap.appendChild(select);
  select.classList.add("combo-native");
  select.tabIndex = -1;
  select.setAttribute("aria-hidden", "true");
  const toggle = document.createElement("button");
  toggle.type = "button";
  toggle.className = "combo-toggle";
  toggle.setAttribute("aria-haspopup", "listbox");
  toggle.setAttribute("aria-expanded", "false");
  toggle.setAttribute("aria-label", select.closest("label") ? select.closest("label").childNodes[0].textContent.trim() : "Choose");
  const list = document.createElement("div");
  list.className = "combo-list hidden";
  list.setAttribute("role", "listbox");
  const tip = document.createElement("p");
  tip.className = "combo-tip";
  function selectedOption() {
    return [...select.options].find(item => item.value === select.value) || select.options[0];
  }
  function paintToggle() {
    const opt = selectedOption();
    toggle.textContent = opt ? opt.textContent : "";
  }
  function setTip(opt) {
    tip.textContent = opt && opt.title ? opt.title : "";
  }
  function closeList() {
    list.classList.add("hidden");
    toggle.setAttribute("aria-expanded", "false");
    if (select.id === "export-kind") syncExport();
    else if (select.id === "import-mode") syncImport(false);
    else setTip(selectedOption());
  }
  function openList() {
    list.classList.remove("hidden");
    toggle.setAttribute("aria-expanded", "true");
    const current = list.querySelector('.combo-option[data-value="' + select.value + '"]');
    if (current) current.focus();
    else {
      const first = list.querySelector(".combo-option");
      if (first) first.focus();
    }
  }
  [...select.options].forEach(opt => {
    const item = document.createElement("button");
    item.type = "button";
    item.className = "combo-option";
    item.setAttribute("role", "option");
    item.dataset.value = opt.value;
    item.textContent = opt.textContent;
    item.title = opt.title;
    item.setAttribute("aria-selected", opt.value === select.value ? "true" : "false");
    item.addEventListener("mouseenter", () => setTip(opt));
    item.addEventListener("focus", () => setTip(opt));
    item.addEventListener("click", () => {
      select.value = opt.value;
      select.dispatchEvent(new Event("change"));
      closeList();
      toggle.focus();
    });
    list.appendChild(item);
  });
  wrap.appendChild(toggle);
  wrap.appendChild(list);
  wrap.appendChild(tip);
  paintToggle();
  setTip(selectedOption());
  toggle.addEventListener("click", () => {
    if (list.classList.contains("hidden")) openList();
    else closeList();
  });
  toggle.addEventListener("keydown", event => {
    if (event.key === "ArrowDown" || event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      openList();
    }
  });
  list.addEventListener("keydown", event => {
    const items = [...list.querySelectorAll(".combo-option")];
    const at = items.indexOf(document.activeElement);
    if (event.key === "Escape") {
      event.preventDefault();
      closeList();
      toggle.focus();
    } else if (event.key === "ArrowDown" && at >= 0) {
      event.preventDefault();
      items[Math.min(at + 1, items.length - 1)].focus();
    } else if (event.key === "ArrowUp" && at >= 0) {
      event.preventDefault();
      items[Math.max(at - 1, 0)].focus();
    }
  });
  select.addEventListener("change", () => {
    paintToggle();
    setTip(selectedOption());
    list.querySelectorAll(".combo-option").forEach(item => {
      item.setAttribute("aria-selected", item.dataset.value === select.value ? "true" : "false");
    });
  });
  document.addEventListener("mousedown", event => {
    if (!wrap.contains(event.target)) closeList();
  });
  return wrap;
}
function syncExport() {
  const kindSel = document.getElementById("export-kind");
  const kind = kindSel.value;
  const bookSel = document.getElementById("export-book");
  const isBook = kind === "book";
  document.getElementById("export-book-label").classList.toggle("hidden", !isBook);
  bookSel.disabled = !isBook;
  const book = bookSel.value;
  let hint = optionHint(kindSel, kind);
  if (kind === "book") {
    hint = book === "all"
      ? "Overwrites the organization file in every book folder, including sources and which books must be finished first."
      : (book ? "Overwrites " + orgPath(book) + ", including its sources and which books must be finished first." : "Choose a book.");
  }
  const tip = document.querySelector("#export-kind-combo .combo-tip");
  if (tip) tip.textContent = hint;
  document.getElementById("export-download").disabled = isBook && !book;
  const scan = kind === "internal-references";
  document.getElementById("scan-form").classList.toggle("hidden", !scan);
}
const exportBook = document.getElementById("export-book");
const allBooks = document.createElement("option");
allBooks.value = "all";
allBooks.textContent = "All books";
exportBook.appendChild(allBooks);
data.books.forEach(b => {
  const o = document.createElement("option");
  o.value = b.code;
  o.textContent = b.code + " — " + b.title;
  exportBook.appendChild(o);
});
enhanceCombo(document.getElementById("export-kind"));
["export-kind", "export-book"].forEach(id => {
  document.getElementById(id).addEventListener("change", syncExport);
});
syncExport();

const importBook = document.getElementById("import-book");
const importAll = document.createElement("option");
importAll.value = "all";
importAll.textContent = "All books";
importBook.appendChild(importAll);
data.books.forEach(b => {
  const o = document.createElement("option");
  o.value = b.code;
  o.textContent = b.code + " — " + b.title;
  importBook.appendChild(o);
});
function syncImport(resetFile) {
  const modeSel = document.getElementById("import-mode");
  const chapter = modeSel.value === "chapter";
  const book = importBook.value;
  document.getElementById("import-book-label").classList.toggle("hidden", chapter);
  importBook.disabled = chapter;
  document.getElementById("import-template").classList.toggle("hidden", !chapter);
  const file = document.getElementById("import-file");
  const fileLabel = document.getElementById("import-file-label");
  fileLabel.classList.toggle("hidden", !chapter);
  file.disabled = !chapter;
  file.required = chapter;
  let hint = optionHint(modeSel, modeSel.value);
  if (chapter) {
    document.getElementById("import-file-caption").textContent = "Document";
    file.accept = ".md,.markdown,text/markdown";
  } else if (book === "all") {
    hint = "Import reads the organization file in every book folder, including sources and which books must be finished first.";
  } else {
    hint = "Import reads " + orgPath(book) + " and replaces that book, including its sources and which books must be finished first.";
  }
  const tip = document.querySelector("#import-mode-combo .combo-tip");
  if (tip) tip.textContent = hint;
  if (resetFile) {
    file.value = "";
    const name = document.getElementById("import-name");
    name.textContent = "";
    name.classList.add("hidden");
  }
}
enhanceCombo(document.getElementById("import-mode"));
document.getElementById("import-mode").addEventListener("change", () => syncImport(true));
importBook.addEventListener("change", () => syncImport(true));
syncImport(false);
document.getElementById("import-file").addEventListener("change", () => {
  const file = document.getElementById("import-file").files[0];
  const name = document.getElementById("import-name");
  name.textContent = file ? file.name : "";
  name.classList.toggle("hidden", !file);
});
document.getElementById("scan-form").addEventListener("submit", (event) => {
  const form = event.target;
  if (form.dataset.ready === "1") return;
  event.preventDefault();
  if (!window.confirm("Scan reads the .tex files and replaces the internal references stored in the library. Continue?")) return;
  form.dataset.ready = "1";
  form.submit();
});

document.getElementById("import-form").addEventListener("submit", async (event) => {
  const form = event.target;
  if (form.dataset.ready === "1") return;
  event.preventDefault();
  const chapter = document.getElementById("import-mode").value === "chapter";
  const book = importBook.value;
  const file = document.getElementById("import-file").files[0];
  let message;
  if (!chapter && book === "all") {
    message = "Import replaces every book from the organization file in its folder, including sources and which books must be finished first, then rewrites EDITORIAL_ORGANIZATION.md. Continue?";
  } else if (!chapter) {
    message = "Import replaces " + book + " from " + orgPath(book) + ", including its sources and which books must be finished first, then rewrites EDITORIAL_ORGANIZATION.md. Continue?";
  } else if (!file) {
    return;
  } else if (chapter) {
    const head = await file.slice(0, 4000).text();
    if (!/^kind:\s*editorial-organization/m.test(head)) {
      window.alert("Choose a chapter-changes file. Download the template, fill in the new, edited, and deleted books and chapters, then import that file.");
      return;
    }
    message = "Import applies the new, edited, and deleted books and chapters in this file. Finish first on a book replaces that book's dependencies. Then it rewrites EDITORIAL_ORGANIZATION.md. Continue?";
  }
  if (!window.confirm(message)) return;
  form.dataset.ready = "1";
  form.submit();
});

if (data.notice) {
  const note = document.getElementById("notice");
  note.classList.remove("hidden");
  note.textContent = data.notice;
  note.classList.toggle("error", !!data.noticeError);
}
document.querySelectorAll("nav.tabs button").forEach(btn => {
  btn.addEventListener("click", () => showTab(btn.dataset.tab));
});
document.getElementById("box-mode").addEventListener("click", () => {
  boxMode = boxMode === "compressed" ? "expanded" : "compressed";
  document.getElementById("panel-library").classList.toggle("compact", boxMode === "compressed");
  syncBoxButton();
  drawReading();
  fitPanes();
});
document.getElementById("reading-wide").addEventListener("click", () => setReadingWide(!readingWide));
document.getElementById("zoom-out").addEventListener("click", () => applyOrderZoom(orderZoom * 0.8));
document.getElementById("zoom-in").addEventListener("click", () => applyOrderZoom(orderZoom / 0.8));
document.getElementById("chain").addEventListener("wheel", (event) => {
  if (!event.ctrlKey && !event.metaKey) return;
  if (!document.getElementById("order-stage")) return;
  event.preventDefault();
  applyOrderZoom(orderZoom * (event.deltaY > 0 ? 0.9 : 1.1), event.clientX, event.clientY);
}, { passive: false });
document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && readingWide) setReadingWide(false);
});
window.addEventListener("resize", () => {
  if (readingWide) drawReading();
});
new ResizeObserver(() => fitPanes()).observe(document.querySelector(".pictures"));
function enableDrag() {
  const host = document.getElementById("chain");
  let drag = null;
  host.addEventListener("pointerdown", (event) => {
    if (event.button !== 0) return;
    drag = {
      x: event.clientX,
      y: event.clientY,
      left: host.scrollLeft,
      top: host.scrollTop,
      moved: false,
      pointer: event.pointerId
    };
  });
  host.addEventListener("pointermove", (event) => {
    if (!drag || event.pointerId !== drag.pointer) return;
    const dx = event.clientX - drag.x;
    const dy = event.clientY - drag.y;
    if (!drag.moved && Math.hypot(dx, dy) < 4) return;
    if (!drag.moved) {
      drag.moved = true;
      host.classList.add("dragging");
      try { host.setPointerCapture(event.pointerId); } catch (err) {}
    }
    host.scrollLeft = drag.left - dx;
    host.scrollTop = drag.top - dy;
  });
  function end(event) {
    if (!drag || event.pointerId !== drag.pointer) return;
    const moved = drag.moved;
    drag = null;
    host.classList.remove("dragging");
    if (!moved) return;
    const stop = (ev) => {
      ev.preventDefault();
      ev.stopPropagation();
      host.removeEventListener("click", stop, true);
    };
    host.addEventListener("click", stop, true);
  }
  host.addEventListener("pointerup", end);
  host.addEventListener("pointercancel", end);
}
enableDrag();
window.addEventListener("scroll", placeChainScroll, {passive: true});

syncWideButton();
syncZoomButtons();
drawLibrary();
const initialTab = data.tab || "library";
if (initialTab === "library") drawReading();
showTab(initialTab, {keepNotice: true, skipDraw: true});
if (data.notice) {
  const url = new URL(window.location.href);
  url.searchParams.delete("notice");
  url.searchParams.delete("error");
  history.replaceState(null, "", url);
}
