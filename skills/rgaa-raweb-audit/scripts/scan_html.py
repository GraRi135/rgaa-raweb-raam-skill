#!/usr/bin/env python3
"""Static pre-check of one HTML page against RGAA 4.1.2 / RAWeb 1.1 criteria (stdlib only).

  scan_html.py page.html                       # markdown report, RAWeb 1.1 numbering, English titles
  scan_html.py https://example.lu/ --standard rgaa --lang fr
  scan_html.py https://app.example.lu/ --render   # render with a browser first (needs node + playwright, see render_page.js)
  scan_html.py page.html --json                   # machine-readable findings

What it does: parses the delivered HTML and reports, per criterion and test:
  FAIL    the code itself is a non-conformity (missing alt, iframe without title, li outside a list, ...)
  REVIEW  something an auditor must judge (generic link text, suspicious alt, required field without visible mark, ...)
  INFO    inventory that tells you which criteria are applicable on this page (media, tables, forms, documents, ...)
What it cannot do: render, measure contrast, run JavaScript, use a screen reader or a keyboard. A criterion
without findings is NOT compliant by default. Use the output as evidence and a to-do list, never as the audit.
"""
import argparse, json, os, re, signal, subprocess, sys, urllib.request
from html.parser import HTMLParser

if hasattr(signal, "SIGPIPE"):
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)  # no traceback when the output is piped into head

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "references", "data")

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr", "basefont", "frame"}
BLOCK = {"address", "article", "aside", "blockquote", "details", "dialog", "dd", "div", "dl", "dt", "fieldset", "figcaption", "figure", "footer", "form", "h1", "h2", "h3", "h4", "h5", "h6", "header", "hgroup", "hr", "li", "main", "nav", "ol", "p", "pre", "section", "table", "ul", "menu"}
PRESENTATIONAL_TAGS = {"basefont", "big", "blink", "center", "font", "marquee", "s", "strike", "tt", "u"}
PRESENTATIONAL_ATTRS = {"align", "alink", "background", "bgcolor", "border", "cellpadding", "cellspacing", "char", "charoff", "clear", "color", "compact", "frameborder", "hspace", "link", "marginheight", "marginwidth", "text", "valign", "vlink", "vspace"}
GENERIC_LINK_TEXT = {"click here", "cliquez ici", "cliquer ici", "here", "ici", "read more", "lire la suite", "lire plus", "en savoir plus", "learn more", "more", "plus", "plus d'infos", "voir", "voir plus", "see more", "link", "lien", "download", "télécharger", "telecharger", "suite", "détails", "details", "continuer", "continue", "next", "suivant", "previous", "précédent", "précédente", "+", ">", "»", "→", "ouvrir", "open", "info", "infos", "page", "go", "aller", "dëst", "méi"}
GENERIC_TITLES = {"", "home", "accueil", "untitled", "document", "new page", "index", "page", "site", "startseite", "title", "titre", "welcome", "bienvenue"}
GENERIC_FRAME_TITLES = {"iframe", "frame", "video", "widget", "embed", "content", "contenu", "map", "carte"}
LANG_RE = re.compile(r"^[A-Za-z]{2,3}(-[A-Za-z0-9]{1,8})*$")
PERSONAL_FIELD_RE = re.compile(r"(e-?mail|courriel|tel|phone|gsm|mobile|fax|firstname|first-name|first_name|prenom|prénom|lastname|last-name|last_name|surname|nom|name|address|adresse|street|rue|postal|zip|cp|city|ville|country|pays|birth|naissance|dob|password|passwd|mot-de-passe|username|login|identifiant|organization|organisation|company|societe|société|iban|cc-|card)", re.I)
AUTOCOMPLETE_TOKENS = {"on", "off", "name", "honorific-prefix", "given-name", "additional-name", "family-name", "honorific-suffix", "nickname", "username", "new-password", "current-password", "one-time-code", "organization-title", "organization", "street-address", "address-line1", "address-line2", "address-line3", "address-level4", "address-level3", "address-level2", "address-level1", "country", "country-name", "postal-code", "cc-name", "cc-given-name", "cc-additional-name", "cc-family-name", "cc-number", "cc-exp", "cc-exp-month", "cc-exp-year", "cc-csc", "cc-type", "transaction-currency", "transaction-amount", "language", "bday", "bday-day", "bday-month", "bday-year", "sex", "url", "photo", "tel", "tel-country-code", "tel-national", "tel-area-code", "tel-local", "tel-local-prefix", "tel-local-suffix", "tel-extension", "email", "impp", "webauthn", "shipping", "billing", "home", "work", "mobile", "fax", "pager"}
ARIA_ROLES = {"alert", "alertdialog", "application", "article", "banner", "button", "cell", "checkbox", "columnheader", "combobox", "complementary", "contentinfo", "definition", "dialog", "directory", "document", "feed", "figure", "form", "grid", "gridcell", "group", "heading", "img", "link", "list", "listbox", "listitem", "log", "main", "marquee", "math", "menu", "menubar", "menuitem", "menuitemcheckbox", "menuitemradio", "navigation", "none", "note", "option", "presentation", "progressbar", "radio", "radiogroup", "region", "row", "rowgroup", "rowheader", "scrollbar", "search", "searchbox", "separator", "slider", "spinbutton", "status", "switch", "tab", "table", "tablist", "tabpanel", "term", "textbox", "timer", "toolbar", "tooltip", "tree", "treegrid", "treeitem", "generic", "meter", "blockquote", "caption", "code", "deletion", "emphasis", "insertion", "paragraph", "strong", "subscript", "superscript", "time", "mark", "suggestion", "comment"}
WIDGET_ROLES = {"button", "link", "checkbox", "radio", "switch", "tab", "menuitem", "menuitemcheckbox", "menuitemradio", "option", "slider", "spinbutton", "textbox", "combobox", "searchbox", "treeitem", "gridcell"}
NAMED_ROLES = WIDGET_ROLES | {"dialog", "alertdialog", "img", "region", "progressbar", "meter", "table", "grid", "tree", "listbox", "radiogroup", "tablist", "menu", "menubar", "toolbar", "form"}
OFFICE_EXT = re.compile(r"\.(pdf|docx?|xlsx?|pptx?|odt|ods|odp|rtf|epub)(\?|#|$)", re.I)
FOCUSABLE_TAGS = {"a", "button", "input", "select", "textarea", "summary", "iframe", "audio", "video"}
SKIP_LINK_RE = re.compile(r"(skip|aller|accéder|acceder|accès|acces|contenu|content|main|principal|navigation|menu|sprangen|iwwersprangen|zum inhalt|inhalt)", re.I)


class Node:
    __slots__ = ("tag", "attrs", "children", "parent", "line", "text", "dup_attrs")

    def __init__(self, tag, attrs=None, parent=None, line=0, text=None):
        self.tag, self.attrs, self.children, self.parent, self.line, self.text = tag, attrs or {}, [], parent, line, text
        self.dup_attrs = []

    def get(self, k, default=None):
        return self.attrs.get(k, default)

    def has(self, k):
        return k in self.attrs

    def iter(self):
        yield self
        for c in self.children:
            yield from c.iter()

    def elements(self):
        return (n for n in self.iter() if n.tag)

    def find_all(self, *tags):
        return [n for n in self.iter() if n.tag in tags]

    def ancestors(self):
        n = self.parent
        while n is not None:
            yield n
            n = n.parent

    def closest(self, *tags):
        for a in self.ancestors():
            if a.tag in tags:
                return a
        return None

    def role(self):
        r = (self.get("role") or "").strip().lower().split()
        return r[0] if r else ""

    def aria_hidden(self):
        return any(a.get("aria-hidden") == "true" for a in [self] + list(self.ancestors()))

    def hidden(self):
        return self.aria_hidden() or self.css_hidden()

    def css_hidden(self):
        """Hidden from everyone (hidden attribute, inline display:none / visibility:hidden), as opposed to aria-hidden."""
        for a in [self] + list(self.ancestors()):
            if a.tag is None:
                continue
            if a.has("hidden"):
                return True
            st = (a.get("style") or "").replace(" ", "").lower()
            if "display:none" in st or "visibility:hidden" in st:
                return True
        return False

    def css_path(self):
        """A CSS selector that finds this element again in a browser (id if unique, else nth-of-type chain)."""
        parts = []
        n = self
        while n is not None and n.tag not in (None, "#document", "html"):
            if n.get("id") and re.match(r"^[A-Za-z][\w-]*$", n.get("id")):
                parts.append("#" + n.get("id"))
                break
            same = [c for c in (n.parent.children if n.parent else []) if c.tag == n.tag]
            idx = same.index(n) + 1 if n in same else 1
            parts.append(f"{n.tag}:nth-of-type({idx})" if len(same) > 1 else n.tag)
            n = n.parent
        return " > ".join(reversed(parts))

    def snippet(self, limit=110):
        if self.tag is None:
            return (self.text or "")[:limit]
        parts = [self.tag] + [f'{k}="{v[:40]}"' if v else k for k, v in list(self.attrs.items())[:6]]
        s = "<" + " ".join(parts) + ">"
        return s if len(s) <= limit else s[:limit - 1] + "…"


class TreeBuilder(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node("#document")
        self.cur = self.root
        self.doctype = None
        self.doctype_line = None
        self.html_line = None

    def handle_decl(self, decl):
        if decl.lower().startswith("doctype"):
            self.doctype = decl
            self.doctype_line = self.getpos()[0]

    def _close_implicit(self, tag):
        def nearest(*cands):
            n = self.cur
            while n is not None and n.tag != "#document":
                if n.tag in cands:
                    return n
                n = n.parent
            return None
        if tag == "li":
            n = nearest("li", "ul", "ol", "menu")
            if n is not None and n.tag == "li":
                self.cur = n.parent
        elif tag in ("dt", "dd"):
            n = nearest("dt", "dd", "dl")
            if n is not None and n.tag in ("dt", "dd"):
                self.cur = n.parent
        elif tag in ("td", "th"):
            n = nearest("td", "th", "tr", "table")
            if n is not None and n.tag in ("td", "th"):
                self.cur = n.parent
        elif tag == "tr":
            n = nearest("td", "th", "tr", "thead", "tbody", "tfoot", "table")
            if n is not None and n.tag in ("td", "th"):
                n = n.parent if n.parent.tag == "tr" else n
                self.cur = n.parent
            elif n is not None and n.tag == "tr":
                self.cur = n.parent
        elif tag in ("thead", "tbody", "tfoot"):
            n = nearest("table")
            if n is not None:
                self.cur = n
        elif tag in ("option", "optgroup"):
            n = nearest("option", "select", "datalist", "optgroup")
            if n is not None and n.tag == "option":
                self.cur = n.parent
        elif tag in BLOCK:
            n = self.cur
            while n is not None and n.tag not in BLOCK and n.tag not in ("body", "#document"):
                n = n.parent
            if n is not None and n.tag == "p":
                self.cur = n.parent

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        d, dups = {}, []
        for k, v in attrs:
            k = k.lower()
            if k in d:
                dups.append(k)
            d[k] = v if v is not None else ""
        self._close_implicit(tag)
        node = Node(tag, d, self.cur, self.getpos()[0])
        node.dup_attrs = dups
        self.cur.children.append(node)
        if tag == "html" and self.html_line is None:
            self.html_line = self.getpos()[0]
        if tag not in VOID:
            self.cur = node

    def handle_startendtag(self, tag, attrs):
        tag = tag.lower()
        if tag in VOID:
            self.handle_starttag(tag, attrs)
        else:
            self.handle_starttag(tag, attrs)
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag in VOID:
            return
        n = self.cur
        while n is not None and n.tag != "#document":
            if n.tag == tag:
                self.cur = n.parent
                return
            n = n.parent

    def handle_data(self, data):
        if self.cur.tag in ("script", "style", "template"):
            self.cur.children.append(Node(None, parent=self.cur, line=self.getpos()[0], text=data))
            return
        if data:
            self.cur.children.append(Node(None, parent=self.cur, line=self.getpos()[0], text=data))


def norm(s):
    return re.sub(r"\s+", " ", s or "").strip()


def text_of(node, byid=None, include_hidden=False, _seen=None):
    """Text alternative computation (simplified accessible name from content).
    _seen guards against aria-labelledby loops (an element naming itself or an ancestor)."""
    out = []
    _seen = set(_seen or ())
    if node.tag is not None and node.get("id"):
        _seen.add(node.get("id"))
    def walk(n):
        if n.tag is None:
            if n.parent is None or n.parent.tag not in ("script", "style", "template", "noscript"):
                out.append(n.text or "")
            return
        if not include_hidden and n.get("aria-hidden") == "true":
            return
        if n.tag in ("script", "style", "template"):
            return
        if n.get("aria-labelledby") and byid is not None and n is not node:
            ids = [i for i in n.get("aria-labelledby").split() if i in byid and i not in _seen]
            if ids:
                out.append(" ".join(text_of(byid[i], byid, include_hidden, _seen | {i}) for i in ids))
                return
        if n.get("aria-label") and n is not node:
            out.append(n.get("aria-label")); return
        if n.tag in ("img", "area"):
            out.append(n.get("alt") or ""); return
        if n.tag == "input" and (n.get("type") or "").lower() == "image":
            out.append(n.get("alt") or n.get("title") or ""); return
        if n.tag == "svg":
            t = [c for c in n.children if c.tag == "title"]
            out.append(norm(text_of(t[0])) if t else "")
            return
        for c in n.children:
            walk(c)
    walk(node)
    return norm(" ".join(out))


def accessible_name(node, byid, labels_for):
    """Return (name, source). Placeholder is deliberately not a valid source (RGAA/RAWeb 11.1)."""
    lb = node.get("aria-labelledby")
    if lb:
        own = {node.get("id")} if node.get("id") else set()
        parts = [text_of(byid[i], byid, include_hidden=True, _seen=own | {i}) for i in lb.split() if i in byid and i not in own]
        name = norm(" ".join(parts))
        if name:
            return name, "aria-labelledby"
    al = norm(node.get("aria-label"))
    if al:
        return al, "aria-label"
    tag = node.tag
    if tag in ("img", "area"):
        if norm(node.get("alt")):
            return norm(node.get("alt")), "alt"
    elif tag == "input":
        t = (node.get("type") or "text").lower()
        if t == "image" and norm(node.get("alt")):
            return norm(node.get("alt")), "alt"
        if t in ("submit", "reset", "button"):
            if norm(node.get("value")):
                return norm(node.get("value")), "value"
            if t in ("submit", "reset"):
                return t.capitalize(), "browser default"
    if tag in ("input", "select", "textarea", "meter", "progress", "output"):
        nid = node.get("id")
        if nid and nid in labels_for:
            name = norm(" ".join(text_of(l, byid) for l in labels_for[nid]))
            if name:
                return name, "label[for]"
        wrap = node.closest("label")
        if wrap is not None:
            name = text_of(wrap, byid)
            if name:
                return name, "wrapping label"
    if tag in ("button", "a", "summary") or node.role() in WIDGET_ROLES or node.role() == "heading":
        name = text_of(node, byid)
        if name:
            return name, "content"
    if tag == "svg":
        t = [c for c in node.children if c.tag == "title"]
        if t and norm(text_of(t[0])):
            return norm(text_of(t[0])), "svg title"
    if tag in ("iframe", "frame") and norm(node.get("title")):
        return norm(node.get("title")), "title"
    if norm(node.get("title")):
        return norm(node.get("title")), "title"
    return "", None


class Scanner:
    def __init__(self, root, builder, standard, lang, source):
        self.root, self.b, self.standard, self.lang, self.source = root, builder, standard, lang, source
        self.findings = []
        self.inventory = {}
        self.byid = {}
        self.labels_for = {}
        self.dup_ids = {}
        for n in root.elements():
            i = n.get("id")
            if i:
                if i in self.byid:
                    self.dup_ids.setdefault(i, [self.byid[i].line]).append(n.line)
                else:
                    self.byid[i] = n
            if n.tag == "label" and n.get("for"):
                self.labels_for.setdefault(n.get("for"), []).append(n)
        self.body = (root.find_all("body") or [root])[0]
        self.titles = self._load_titles()

    def _load_titles(self):
        name = "rgaa-4.1.2-fr.json" if self.standard == "rgaa" else f"raweb-1.1-{self.lang}.json"
        try:
            std = json.load(open(os.path.join(DATA, name), encoding="utf-8"))
        except OSError:
            return {}
        out = {}
        for t in std["topics"]:
            for c in t["criteria"]:
                out[c["id"]] = (c["level"], re.sub(r"\[([^\]]+)\]\(#[^)]*\)", r"\1", c["title"]))
        return out

    def add(self, status, crit, test, msg, node=None):
        self.findings.append({"status": status, "criterion": crit, "test": test, "message": msg,
                              "line": node.line if node is not None else None, "element": node.snippet() if node is not None else None,
                              "selector": node.css_path() if node is not None and node.tag not in (None, "#document", "html") else None})

    # ---------------- checks ----------------
    def check_page(self):
        b = self.b
        if not b.doctype:
            self.add("fail", "8.1", "8.1.1", "No doctype declaration.")
        else:
            if b.html_line and b.doctype_line and b.doctype_line > b.html_line:
                self.add("fail", "8.1", "8.1.3" if self.standard == "rgaa" else "8.1.1", "Doctype is declared after the <html> tag.")
            if "html" not in b.doctype.lower():
                self.add("review", "8.1", "8.1.2" if self.standard == "rgaa" else "8.1.1", f"Unusual doctype: {b.doctype[:60]}")
        html = self.root.find_all("html")
        html = html[0] if html else None
        lang = (html.get("lang") or html.get("xml:lang")) if html is not None else None
        if html is None:
            self.add("fail", "8.3", "8.3.1", "No <html> element found (fragment?). Default language cannot be declared.")
        elif not norm(lang):
            self.add("fail", "8.3", "8.3.1", "No lang attribute on <html>: the default language is not declared.", html)
        elif not LANG_RE.match(lang.strip()):
            self.add("fail", "8.4", "8.4.1", f'Invalid language code lang="{lang}".', html)
        else:
            self.add("review", "8.4", "8.4.1", f'Default language is "{lang}": check it matches the main language of the content.', html)
        titles = [t for t in self.root.find_all("title") if t.closest("svg") is None]
        if not titles or not norm(text_of(titles[0])):
            self.add("fail", "8.5", "8.5.1", "No <title> (or empty title).")
        else:
            t = norm(text_of(titles[0]))
            self.inventory["title"] = t
            if t.lower() in GENERIC_TITLES or len(t) < 4:
                self.add("review", "8.6", "8.6.1", f'Page title "{t}" looks generic: it should identify the page content and ideally the site.', titles[0])
            else:
                self.add("review", "8.6", "8.6.1", f'Page title is "{t}": check it is relevant (identifies the page and the site).', titles[0])
        # language changes
        changes = [n for n in self.body.elements() if n.has("lang") and n.tag != "html"]
        for n in changes:
            if not LANG_RE.match((n.get("lang") or "").strip()):
                self.add("fail", "8.8", "8.8.1", f'Invalid language code lang="{n.get("lang")}" on a language change.', n)
        self.inventory["language_changes"] = len(changes)
        self.add("review", "8.7", "8.7.1", f"{len(changes)} element(s) carry a lang attribute. Foreign-language words or passages without a lang attribute cannot be detected statically: read the page.")
        # duplicate ids / attributes
        for i, lines in self.dup_ids.items():
            self.add("fail", "8.2", "8.2.1", f'Duplicate id="{i}" (lines {", ".join(map(str, lines))}). Note: the SIP records 8.1/8.2 as compliant in simplified audits; report the consequence under the criterion that breaks (11.1 label/for, 7.1 ARIA references) as well.')
        for n in self.body.elements():
            if n.dup_attrs:
                self.add("fail", "8.2", "8.2.1", f"Duplicate attribute(s) {', '.join(n.dup_attrs)}.", n)
        # presentational markup
        for n in self.root.elements():
            if n.tag in PRESENTATIONAL_TAGS:
                self.add("fail", "10.1", "10.1.1", f"Presentational tag <{n.tag}> in the source.", n)
                if n.tag in ("marquee", "blink"):
                    self.add("fail", "13.8", "13.8.1" if n.tag == "marquee" else "13.8.2", f"<{n.tag}> moves or blinks without user control.", n)
            if n.tag in ("link", "meta", "script", "style", "svg") or n.closest("svg") is not None:
                continue
            bad = [a for a in n.attrs if a in PRESENTATIONAL_ATTRS and not (a == "border" and n.tag == "img")]
            if bad:
                self.add("fail", "10.1", "10.1.2", f"Presentational attribute(s) {', '.join(bad)}.", n)
        # spaced-out letters
        for n in self.body.iter():
            if n.tag is None and n.parent.tag not in ("script", "style") and re.search(r"(?:\b[A-Za-zÀ-ÿ] ){4,}[A-Za-zÀ-ÿ]\b", n.text or ""):
                self.add("review", "10.1", "10.1.3", "Letters separated by spaces (spaced-out word?).", n)
        # meta refresh / redirect
        for m in self.root.find_all("meta"):
            if (m.get("http-equiv") or "").lower() == "refresh":
                c = m.get("content") or ""
                secs = re.match(r"\s*(\d+)", c)
                secs = int(secs.group(1)) if secs else 0
                if "url=" in c.lower():
                    if secs > 0:
                        self.add("fail", "13.1", "13.1.2", f"Delayed <meta> redirect ({secs} s): redirects via meta must be immediate.", m)
                elif secs > 0 and secs < 72000:
                    self.add("fail", "13.1", "13.1.1", f"Automatic page refresh every {secs} s without user control.", m)
            if (m.get("name") or "").lower() == "viewport":
                c = (m.get("content") or "").replace(" ", "").lower()
                if "user-scalable=no" in c or "user-scalable=0" in c or re.search(r"maximum-scale=1(\.0)?(,|$)", c):
                    self.add("fail", "10.4", "10.4.1", "Viewport blocks pinch zoom (user-scalable=no / maximum-scale=1): text cannot be enlarged to 200 % on mobile.", m)
        # inline window.open at load
        for s in self.root.find_all("script"):
            code = "".join(c.text or "" for c in s.children)
            if re.search(r"window\.open\s*\(", code) and not re.search(r"(onclick|addEventListener\(['\"]click)", code):
                self.add("review", "13.2", "13.2.1", "window.open() found in a script: make sure no window opens without a user action.", s)
        for n in self.body.elements():
            if n.tag == "select" and re.search(r"(location|submit\(\))", n.get("onchange") or ""):
                self.add("review", "7.4", "7.4.1", "onchange on a <select> triggers navigation or submission: context change without warning or control?", n)
        # focus outline removed (inline <style> and linked stylesheets)
        sheets = [("".join(c.text or "" for c in s.children), s, "inline <style>") for s in self.root.find_all("style")]
        for link in self.root.find_all("link"):
            if "stylesheet" in (link.get("rel") or "").lower() and link.get("href"):
                css = load_stylesheet(link.get("href"), self.source)
                if css is not None:
                    sheets.append((css, link, link.get("href")))
        self.inventory["stylesheets_read"] = [name for _, _, name in sheets if name != "inline <style>"]
        for css, node, name in sheets:
            css_nc = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
            for m in re.finditer(r"([^{}]*:focus(?:-visible)?[^{]*)\{([^}]*)\}", css_nc, re.I):
                if re.search(r"outline\s*:\s*(none|0)(px)?\s*(!important)?\s*(;|$)", m.group(2), re.I) and not re.search(r"(box-shadow|border|background|text-decoration)\s*:", m.group(2), re.I):
                    self.add("review", "10.7", "10.7.1", f"{name}: '{m.group(1).strip()[:60]}' removes the focus outline without an obvious replacement in the same rule: check that a visible focus style exists (3:1 against the background).", node)
            if re.search(r"\*\s*\{[^}]*outline\s*:\s*(none|0)", css_nc, re.I):
                self.add("review", "10.7", "10.7.1", f"{name}: a universal rule removes outlines.", node)
        # accesskeys / tabindex
        for n in self.body.elements():
            ti = n.get("tabindex")
            if ti and re.match(r"^\s*[1-9]\d*\s*$", ti):
                self.add("review", "12.8", "12.8.1", f"Positive tabindex={ti.strip()} changes the natural tab order.", n)
            if n.has("accesskey"):
                self.add("info", "12.10", "12.10.1", f'accesskey="{n.get("accesskey")}" (uses modifier keys, so out of 12.10 scope; still check for conflicts).', n)

    def check_images(self):
        imgs = self.body.find_all("img")
        self.inventory["images"] = len(imgs)
        stricter = self.standard != "rgaa"   # RAWeb 1.1 restricts role=presentation/none
        for n in imgs:
            if n.hidden():
                continue
            role = n.role()
            alt = n.get("alt")
            has_name = any(norm(n.get(a)) for a in ("alt", "aria-label", "aria-labelledby", "title"))
            if alt is None and not has_name and role not in ("presentation", "none"):
                self.add("fail", "1.1", "1.1.1", "Image without alt (and no aria-label/aria-labelledby/title): NC under 1.1 if it conveys information, under 1.2 if decorative (needs alt=\"\").", n)
                continue
            if alt is not None and not norm(alt):
                extra = [a for a in ("title", "aria-label", "aria-labelledby") if norm(n.get(a))]
                if extra:
                    self.add("fail", "1.2", "1.2.1", f'alt="" but also {", ".join(extra)}: a decorative image must carry no other text alternative.', n)
                else:
                    self.add("info", "1.2", "1.2.1", "alt=\"\": treated as decorative. Confirm it conveys no information (otherwise NC 1.1).", n)
                continue
            if role in ("presentation", "none"):
                extra = [a for a in ("title", "aria-label", "aria-labelledby") if norm(n.get(a))]
                if extra and stricter:
                    self.add("fail", "1.2", "1.2.1", f'role="{role}" with {", ".join(extra)} (RAWeb 1.1 forbids this combination).', n)
                continue
            a = norm(alt or n.get("aria-label") or n.get("title") or "")
            src = os.path.basename((n.get("src") or "").split("?")[0])
            if a and (re.search(r"\.(jpe?g|png|gif|svg|webp|bmp|tiff?)$", a, re.I) or (src and a.lower() == src.lower())):
                self.add("review", "1.3", "1.3.1", f'alt="{a}" looks like a file name: not a relevant alternative.', n)
            elif a and a.lower() in {"image", "img", "photo", "picture", "icon", "icône", "icone", "logo", "illustration", "spacer", "bild", "graphic"}:
                self.add("review", "1.3", "1.3.1", f'alt="{a}" is generic: it should convey the information of the image (or alt="" if decorative).', n)
            elif len(a) > 150:
                self.add("review", "1.3", "1.3.1", f"alt is {len(a)} characters long: should be short and concise; use a detailed description (1.6) instead.", n)
            elif a:
                self.add("review", "1.3", "1.3.1", f'alt="{a[:80]}": check relevance against the image.', n)
            if n.closest("a") is not None:
                pass  # handled with links
        for n in self.body.elements():
            if n.tag == "img":
                continue
            if n.role() == "img" and not n.hidden() and not any(norm(n.get(a)) for a in ("aria-label", "aria-labelledby")):
                self.add("fail", "1.1", "1.1.1", 'role="img" without aria-label/aria-labelledby.', n)
            if n.tag == "input" and (n.get("type") or "").lower() == "image" and not any(norm(n.get(a)) for a in ("alt", "aria-label", "aria-labelledby", "title")):
                self.add("fail", "1.1", "1.1.3", "Image button without alt.", n)
            if n.tag == "area" and n.has("href") and not any(norm(n.get(a)) for a in ("alt", "aria-label", "aria-labelledby", "title")):
                self.add("fail", "1.1", "1.1.2", "Image-map area without alt.", n)
            if n.tag == "svg" and not n.hidden():
                has_title = any(c.tag == "title" and norm(text_of(c)) for c in n.children)
                named = has_title or norm(n.get("aria-label")) or norm(n.get("aria-labelledby"))
                if n.role() == "img" and not named:
                    self.add("fail", "1.1", "1.1.5", '<svg role="img"> without text alternative (<title>, aria-label or aria-labelledby).', n)
                elif n.role() != "img":
                    where = " (inside a link/button: the parent must then carry the name)" if n.closest("a", "button") is not None else ""
                    self.add("fail", "1.1", "1.1.5", f'<svg> is neither role="img" with a name (if informative, 1.1.5) nor aria-hidden="true" (if decorative, 1.2.4){where}.', n)
            if n.tag == "canvas" and not n.hidden():
                self.add("review", "1.1", "1.1.8", "<canvas>: needs role=img + name, inner alternative content, or an adjacent alternative if informative; aria-hidden if decorative (1.2.5).", n)
            if n.tag in ("object", "embed") and (n.get("type") or "").lower().startswith("image/") and not n.hidden():
                self.add("review", "1.1", "1.1.6" if n.tag == "object" else "1.1.7", f"<{n.tag}> image: check role=img + alternative, or aria-hidden if decorative.", n)
        figs = self.body.find_all("figure")
        for f in figs:
            cap = [c for c in f.children if c.tag == "figcaption"]
            if cap and f.find_all("img", "svg", "canvas", "object"):
                ok = f.role() == "figure" and (norm(f.get("aria-label")) or norm(f.get("aria-labelledby")))
                self.add("review" if not ok else "info", "1.9", "1.9.1", "Image with a caption: RGAA/RAWeb expects <figure role=\"figure\" aria-label=\"[caption text]\"> (or aria-labelledby to the figcaption) and the image alt must not be the caption." if not ok else "Captioned figure correctly structured.", f)
        self.inventory["figures_with_caption"] = sum(1 for f in figs if any(c.tag == "figcaption" for c in f.children))

    def check_frames(self):
        frames = [n for n in self.body.find_all("iframe", "frame") if not n.hidden()]
        self.inventory["frames"] = len(frames)
        for n in frames:
            t = norm(n.get("title"))
            if not t:
                self.add("fail", "2.1", "2.1.1", "Frame without title attribute.", n)
            elif t.lower() in GENERIC_FRAME_TITLES:
                self.add("review", "2.2", "2.2.1", f'Frame title "{t}" is generic: it should describe the frame content.', n)
            else:
                self.add("review", "2.2", "2.2.1", f'Frame title "{t}": check relevance.', n)
            src = (n.get("src") or "").lower()
            if re.search(r"(youtube|youtu\.be|vimeo|dailymotion|soundcloud|spotify)", src):
                self.add("info", "4.1", None, "Embedded media player: criteria 4.1 to 4.13 apply (transcript, captions, audio description, identification, keyboard control, AT compatibility).", n)

    def check_links(self):
        links = [n for n in self.body.elements() if (n.tag == "a" and n.has("href")) or n.role() == "link"]
        self.inventory["links"] = len(links)
        seen = {}
        for n in links:
            if n.hidden():
                continue
            name, src = accessible_name(n, self.byid, self.labels_for)
            href = n.get("href") or ""
            only_images = bool(n.find_all("img", "svg")) and not norm("".join(c.text or "" for c in n.iter() if c.tag is None and c.parent.tag not in ("title",)))
            if not name:
                self.add("fail", "6.2", "6.2.1", "Link without accessible name" + (" (image link with empty alt / svg without title)" if only_images else " (empty link)") + ".", n)
                continue
            low = name.lower().strip(" .:!…")
            if low in GENERIC_LINK_TEXT:
                self.add("review", "6.1", "6.1.2" if only_images else "6.1.1", f'Link "{name}" is not explicit on its own: NC unless the link context (same sentence, paragraph, list item, table cell or preceding heading) makes the destination clear.', n)
            elif only_images:
                self.add("review", "6.1", "6.1.2", f'Image link named "{name[:60]}" (from {src}): the name must describe the destination/function, not the image.', n)
            if src == "title" and only_images is False:
                self.add("review", "6.2", "6.2.1", f'Link name comes only from the title attribute ("{name[:60]}"): title is not reliably rendered; prefer visible text or aria-label.', n)
            vis = text_of(n, self.byid)
            if n.get("aria-label") and vis and vis.lower() not in name.lower():
                self.add("fail", "6.1", "6.1.5", f'aria-label "{name[:50]}" does not contain the visible label "{vis[:50]}".', n)
            key = low
            # RAWeb 1.1 test 6.1.6 (identical links, same destination); RGAA 4.1.2 6.1 has no such test.
            if key in seen and seen[key] != href and low not in GENERIC_LINK_TEXT and self.standard != "rgaa":
                self.add("review", "6.1", "6.1.6", f'Several links named "{name[:50]}" point to different targets ({seen[key][:40]} vs {href[:40]}).', n)
            seen.setdefault(key, href)
            if href.startswith("#") and n.tag == "a" and (n.has("onclick") or n.role() == "button") or href.lower().startswith("javascript:"):
                self.add("review", "7.3", "7.3.1", "Link used as a button (href=# / javascript:): check role, name and keyboard operation (Enter and Space for role=button).", n)
            if OFFICE_EXT.search(href):
                self.add("review", "13.3", "13.3.1", f"Downloadable office document ({href[-60:]}): it must be accessible or have an accessible version (13.3/13.4); good practice: announce format and size in the link.", n)
            if (n.get("target") or "").lower() == "_blank":
                self.add("info", "13.2", None, "Link opens a new window on user action (allowed); warning the user is good practice.", n)
        # skip link
        skip = None
        for n in links[:8]:
            href = n.get("href") or ""
            if href.startswith("#") and (SKIP_LINK_RE.search(text_of(n, self.byid)) or re.search(r"#(main|content|contenu|principal)", href, re.I)):
                skip = n
                break
        if skip is None:
            self.add("review", "12.7", "12.7.1", "No skip link to the main content detected among the first links of the page (NC unless the page has no repeated blocks before the main content).")
        else:
            target = (skip.get("href") or "")[1:]
            anchors = {x.get("name") for x in self.body.find_all("a") if x.get("name")}
            if target and target.lower() != "top" and target not in self.byid and target not in anchors:
                self.add("fail", "12.7", "12.7.2", f'Skip link target "#{target}" does not exist (no element with that id or name): the link is not functional.', skip)
            else:
                self.add("review", "12.7", "12.7.2", f'Skip link "{text_of(skip, self.byid)[:40]}" found: check it is visible or visible on focus, functional, and at the same place on every page.', skip)

    def check_headings(self):
        hs = []
        for n in self.body.elements():
            if n.hidden():
                continue
            if n.tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
                hs.append((int(n.tag[1]), n))
            elif n.role() == "heading":
                lvl = n.get("aria-level")
                if not lvl or not lvl.strip().isdigit():
                    self.add("fail", "9.1", "9.1.1", 'role="heading" without a valid aria-level.', n)
                    lvl = "2"
                hs.append((int(lvl), n))
        self.inventory["headings"] = {f"h{l}": sum(1 for x, _ in hs if x == l) for l in range(1, 7) if any(x == l for x, _ in hs)}
        if not hs:
            self.add("review", "9.1", "9.1.3", "No heading at all: if the page has visually distinct section titles, they must be <hx> or role=heading (9.1.3); a page with no title structure is NC 9.1.")
        elif not any(l == 1 for l, _ in hs):
            self.add("review", "9.1", "9.1.1", "No level-1 heading. The RGAA/RAWeb glossary does not require an h1 and tolerates level jumps as long as the looser hierarchy stays consistent: check consistency rather than counting it as NC.")
        prev = 0
        for l, n in hs:
            if not norm(text_of(n, self.byid)):
                self.add("fail", "9.1", "9.1.2", "Empty heading.", n)
            if prev and l > prev + 1:
                self.add("review", "9.1", "9.1.1", f"Heading level jump (h{prev} → h{l}): tolerated by the glossary if the hierarchy stays consistent; NC only if sibling sections get different levels or the outline misleads.", n)
            prev = l
        for n in self.body.elements():
            cls = (n.get("class") or "").lower()
            if n.tag in ("p", "div", "span", "strong", "b") and re.search(r"(^|[\s_-])(title|titre|heading|h[1-6]|subtitle|sous-titre)([\s_-]|$)", cls) and not n.closest("h1", "h2", "h3", "h4", "h5", "h6", "a", "button", "label", "summary", "th", "td"):
                txt = text_of(n, self.byid)
                if 2 <= len(txt) <= 120 and n.role() != "heading":
                    self.add("review", "9.1", "9.1.3", f'<{n.tag} class="{cls[:40]}"> "{txt[:50]}" looks like a visual heading implemented without <hx>/role=heading.', n)

    def check_landmarks(self):
        els = [n for n in self.body.elements() if not n.hidden()]
        def with_role(tag, role):
            return [n for n in els if (n.tag == tag and (n.closest("article", "section", "aside", "nav", "main") is None if tag in ("header", "footer") else True)) or n.role() == role]
        main = with_role("main", "main")
        header = with_role("header", "banner")
        footer = with_role("footer", "contentinfo")
        nav = with_role("nav", "navigation")
        self.inventory["landmarks"] = {"main": len(main), "banner": len(header), "contentinfo": len(footer), "navigation": len(nav)}
        if not main:
            self.add("fail", "9.2", "9.2.1", "No <main> / role=main: the main content region is not identified.")
        elif len(main) > 1:
            self.add("fail", "9.2", "9.2.2" if self.standard != "rgaa" else "9.2.1", f"{len(main)} visible main regions: there must be exactly one.")
        if not header:
            self.add("review", "9.2", "9.2.1", "No <header> / role=banner at page level: NC if the page has a header zone (logo, site title, main navigation).")
        if not footer:
            self.add("review", "9.2", "9.2.1", "No <footer> / role=contentinfo at page level: NC if the page has a footer zone.")
        if not nav:
            menus = [u for u in self.body.find_all("ul", "ol") if len(u.find_all("a")) >= 3 and u.closest("nav") is None and u.closest("main") is None]
            if menus:
                self.add("fail", "9.2", "9.2.1", f"Navigation menu(s) not structured with <nav> / role=navigation ({len(menus)} list(s) of links outside a nav).", menus[0])
        if self.standard != "rgaa":
            search_inputs = [n for n in els if n.tag == "input" and (n.get("type") or "").lower() == "search"]
            for s in search_inputs:
                if s.closest("search") is None and not any(a.role() == "search" for a in s.ancestors()):
                    self.add("review", "9.2", "9.2.1", "Search field not inside a search landmark (<search> or role=\"search\"): RAWeb 1.1 expects the search zone to have the computed role search.", s)

    def check_lists(self):
        for n in self.body.elements():
            if n.tag == "li":
                p = n.parent
                while p is not None and p.tag in ("template",):
                    p = p.parent
                if p is None or (p.tag not in ("ul", "ol", "menu") and p.role() != "list"):
                    self.add("fail", "9.3", "9.3.1", f"<li> whose parent is <{p.tag if p else '?'}> instead of <ul>/<ol>.", n)
            if n.tag in ("dt", "dd") and n.closest("dl") is None:
                self.add("fail", "9.3", "9.3.3", f"<{n.tag}> outside a <dl>.", n)
            if n.tag in ("ul", "ol"):
                kids = [c for c in n.children if c.tag]
                bad = [c for c in kids if c.tag not in ("li", "script", "template")]
                if bad:
                    self.add("fail", "9.3", "9.3.1", f"<{n.tag}> contains <{bad[0].tag}> as direct child instead of <li>.", n)
                if not kids:
                    self.add("fail", "9.3", "9.3.1", f"Empty <{n.tag}>.", n)
        # textual pseudo lists
        for n in self.body.elements():
            if n.tag in ("p", "div"):
                lines = [norm(c.text) for c in n.children if c.tag is None]
                items = [l for l in lines if re.match(r"^([-–•*]|\d+[.)])\s+\S", l)]
                if len(items) >= 2:
                    self.add("review", "9.3", "9.3.1", f"Visual list made of text lines ({items[0][:30]} …) without <ul>/<ol>.", n)
        self.inventory["lists"] = len(self.body.find_all("ul", "ol", "dl"))

    def check_tables(self):
        tables = [t for t in self.body.find_all("table") if not t.hidden()]
        self.inventory["tables"] = len(tables)
        for t in tables:
            ths = [n for n in t.elements() if n.tag == "th" or n.role() in ("columnheader", "rowheader")]
            cap = [c for c in t.children if c.tag == "caption"]
            layout = t.role() in ("presentation", "none")
            if layout:
                data_stuff = ths or cap or t.find_all("thead", "tfoot") or norm(t.get("summary")) or [n for n in t.find_all("td") if n.has("scope") or n.has("headers") or n.has("axis")]
                if data_stuff:
                    self.add("fail", "5.8", "5.8.1", "Layout table (role=presentation) uses data-table elements/attributes (th, caption, thead/tfoot, summary, scope/headers).", t)
                continue
            rows = t.find_all("tr")
            if not ths:
                self.add("review", "5.6", "5.6.1", f"Table ({len(rows)} rows) without any <th>/columnheader/rowheader: NC 5.6 if it is a data table; if it is a layout table it should have role=\"presentation\" (and keep linearised reading order, 5.3).", t)
                continue
            self.add("review", "5.4", "5.4.1", ("Data table with <caption>: check the caption is relevant (5.5)." if cap else "Data table without <caption>: if a visible title relates to the table, associate it (caption or aria-labelledby) (5.4)."), t)
            has_col = any((n.get("scope") or "").lower() == "col" or n.role() == "columnheader" or (n.closest("thead") is not None) for n in ths)
            has_row = any((n.get("scope") or "").lower() == "row" or n.role() == "rowheader" or (n.closest("thead") is None and n.parent and n.parent.children and [c for c in n.parent.children if c.tag][0] is n) for n in ths)
            no_scope = [n for n in ths if n.tag == "th" and not n.has("scope") and not n.has("id") and n.role() not in ("columnheader", "rowheader")]
            spans = [n for n in t.find_all("td", "th") if (n.get("colspan") or "1") != "1" or (n.get("rowspan") or "1") != "1"]
            if has_col and has_row and no_scope:
                self.add("review", "5.7", "5.7.1", "Table with both column and row headers: each <th> needs scope (or id/headers) so that cells are associated with their headers.", t)
            elif no_scope:
                self.add("info", "5.7", "5.7.1", f"{len(no_scope)} <th> without scope: acceptable for simple tables with one header row/column; check association.", t)
            if spans or (len(t.find_all("thead")) and len(t.find_all("thead")[0].find_all("tr")) > 1):
                if not (cap or norm(t.get("summary")) or norm(t.get("aria-describedby"))):
                    self.add("review", "5.1", "5.1.1", "Looks like a complex data table (merged cells / multi-level headers): it needs a summary (via <caption> or aria-describedby/summary).", t)

    def check_forms(self):
        fields = [n for n in self.body.elements() if (n.tag in ("select", "textarea")) or (n.tag == "input" and (n.get("type") or "text").lower() not in ("hidden", "submit", "reset", "button", "image"))]
        fields = [f for f in fields if not f.hidden()]
        self.inventory["forms"] = len(self.body.find_all("form"))
        self.inventory["fields"] = len(fields)
        form_note = bool(re.search(r"(obligatoire|required|mandatory|champs? marqués|fields? marked|\*\s*=|pflichtfeld)", text_of(self.body, self.byid), re.I))
        for f in fields:
            name, src = accessible_name(f, self.byid, self.labels_for)
            fid = f.get("id")
            if fid and fid in self.labels_for and not norm(" ".join(text_of(l, self.byid) for l in self.labels_for[fid])):
                self.add("fail", "11.2", "11.2.1", "Associated <label> is empty.", f)
            if not name:
                ph = norm(f.get("placeholder"))
                self.add("fail", "11.1", "11.1.1", "Form field without label (no <label for>, aria-label, aria-labelledby or title)" + (f'; placeholder "{ph[:40]}" alone is not a label.' if ph else "."), f)
                continue
            if src in ("aria-label", "title") or (src == "aria-labelledby"):
                self.add("review", "11.1", "11.1.3", f'Field labelled only via {src} ("{name[:50]}"): a visible label or a title/visible text is needed so the expected input is understandable (11.1.3); check the visible label is contained in the name (11.2.5).', f)
            elif src in ("label[for]", "wrapping label"):
                lbl = self.labels_for.get(fid, []) if fid else []
                for l in lbl:
                    cls = (l.get("class") or "").lower()
                    if re.search(r"(sr-only|visually-hidden|visuallyhidden|screen-reader|hidden)", cls):
                        self.add("review", "11.1", "11.1.3", f'Label "{name[:50]}" is visually hidden: a visible label, title or visible text is required.', f)
                self.add("review", "11.2", "11.2.1", f'Label "{name[:60]}": check relevance and that it is adjacent to the field (11.4).', f)
            req = f.has("required") or f.get("aria-required") == "true"
            if req:
                if not (re.search(r"[*]|obligatoire|required|mandatory", name, re.I) or form_note):
                    self.add("review", "11.10", "11.10.2", f'Required field "{name[:40]}" (required/aria-required) without a visible mandatory indication in its label or a form-level note.', f)
            else:
                self.add("info", "11.10", "11.10.1", f'Field "{name[:40]}" is not marked required: if it is mandatory, add a visible indication and required/aria-required.', f)
            fmt_type = (f.get("type") or "").lower() in ("email", "date", "tel", "url", "number", "time") or f.has("pattern")
            desc_ids = (f.get("aria-describedby") or "").split()
            desc = norm(" ".join(text_of(self.byid[i], self.byid) for i in desc_ids if i in self.byid))
            if fmt_type and not re.search(r"(format|ex\.?|exemple|example|jj|mm|aaaa|dd|yyyy|@|\+352|\+33)", name + " " + desc, re.I):
                self.add("review", "11.10", "11.10.5", f'Field "{name[:40]}" expects a specific type/format ({f.get("type") or "pattern"}): the expected format must be indicated visibly before input.', f)
            probe = " ".join(filter(None, [f.get("name"), f.get("id"), (f.get("type") or ""), name])).lower()
            ac = (f.get("autocomplete") or "").strip().lower()
            if ac and ac != "off":
                toks = [t for t in ac.split() if not t.startswith("section-")]
                if not all(t in AUTOCOMPLETE_TOKENS for t in toks):
                    self.add("fail", "11.13", "11.13.1", f'autocomplete="{ac}" is not a valid token.', f)
            elif PERSONAL_FIELD_RE.search(probe) and (f.get("type") or "").lower() not in ("checkbox", "radio", "search", "password") and f.tag != "select":
                self.add("review", "11.13", "11.13.1", f'Field "{name[:40]}" seems to collect user data but has no autocomplete attribute (NC if the data is about the user).', f)
            elif (f.get("type") or "").lower() == "password" and not ac:
                self.add("review", "11.13", "11.13.1", "Password field without autocomplete (current-password / new-password).", f)
        # groups
        groups = {}
        for f in fields:
            if f.tag == "input" and (f.get("type") or "").lower() in ("radio", "checkbox") and f.get("name"):
                groups.setdefault(f.get("name"), []).append(f)
        for name, members in groups.items():
            if len(members) >= 2:
                fs = members[0].closest("fieldset")
                grp = fs is not None or any(a.role() in ("group", "radiogroup") for a in members[0].ancestors())
                if not grp:
                    self.add("fail", "11.5", "11.5.1", f'{len(members)} {members[0].get("type")} buttons "{name}" are not grouped (fieldset/legend or role=group|radiogroup with a name).', members[0])
        for fs in self.body.find_all("fieldset"):
            lg = [c for c in fs.children if c.tag == "legend"]
            if not lg:
                self.add("fail", "11.6", "11.6.1", "<fieldset> without <legend>.", fs)
            elif not norm(text_of(lg[0], self.byid)):
                self.add("fail", "11.7", "11.7.1", "Empty <legend>.", fs)
        for n in self.body.elements():
            if n.role() in ("group", "radiogroup") and not (norm(n.get("aria-label")) or norm(n.get("aria-labelledby"))):
                self.add("fail", "11.6", "11.6.1", f'role="{n.role()}" without aria-label/aria-labelledby (no legend).', n)
        # buttons
        buttons = [n for n in self.body.elements() if n.tag == "button" or (n.tag == "input" and (n.get("type") or "").lower() in ("submit", "reset", "button", "image")) or n.role() == "button"]
        self.inventory["buttons"] = len(buttons)
        for b in buttons:
            if b.hidden():
                continue
            name, src = accessible_name(b, self.byid, self.labels_for)
            scripted = b.tag != "input" and b.closest("form") is None   # a button outside a form is a scripted component: 7.1
            crit = "7.1" if scripted else "11.9"
            if not name:
                self.add("fail", crit, "7.1.1" if scripted else "11.9.1", "Button without accessible name (icon-only button needs aria-label, visually hidden text or svg title).", b)
            else:
                vis = text_of(b, self.byid)
                if b.get("aria-label") and vis and vis.lower() not in name.lower():
                    self.add("fail", crit, "7.1.3" if scripted else "11.9.2", f'Button aria-label "{name[:40]}" does not contain its visible label "{vis[:40]}".', b)
                elif src == "browser default":
                    self.add("review", "11.9", "11.9.1", f'<input type="{b.get("type")}"> without value: browser default name "{name}" is rarely relevant.', b)
        for lab in self.body.find_all("label"):
            if lab.get("for") and lab.get("for") not in self.byid:
                self.add("fail", "11.1", "11.1.2", f'<label for="{lab.get("for")}"> references no element id.', lab)

    def check_scripts(self):
        handlers = ("onclick", "onkeydown", "onkeyup", "onkeypress", "onmousedown", "onmouseup", "ondblclick", "onmouseover", "onfocus", "onblur", "onchange", "oninput")
        def is_focusable(e):
            native = e.tag in FOCUSABLE_TAGS and not (e.tag == "a" and not e.has("href")) and not (e.tag == "input" and (e.get("type") or "").lower() == "hidden")
            ti = (e.get("tabindex") or "").strip()
            return native or (ti.lstrip("-").isdigit() and not ti.startswith("-"))
        for n in self.body.elements():
            # aria-hidden (on the element or an ancestor) with a keyboard-reachable element: checked before hidden() skips it
            if n.aria_hidden() and not n.css_hidden() and is_focusable(n):
                self.add("fail", "7.1", "7.1.1", 'Focusable element with aria-hidden="true" (on it or an ancestor): reachable by keyboard but hidden from assistive technologies.', n)
            if n.hidden():
                continue
            role = n.role()
            if role and role not in ARIA_ROLES:
                self.add("fail", "7.1", "7.1.1", f'Unknown ARIA role "{role}": no role is exposed to assistive technologies.', n)
            focusable = is_focusable(n)
            interactive = any(n.has(h) for h in ("onclick", "onmousedown", "onmouseup", "ondblclick")) or role in WIDGET_ROLES
            if interactive and not focusable and n.tag not in ("option", "label"):
                if role in ("option", "menuitem", "tab", "treeitem", "gridcell", "radio") and n.parent is not None and (n.parent.get("tabindex") or n.parent.has("aria-activedescendant")):
                    continue
                what = "role=" + role if role in WIDGET_ROLES else "a mouse handler"
                if any(c.tag and is_focusable(c) for c in n.iter() if c is not n):
                    self.add("review", "7.3", "7.3.1", f'Element with {what} is not keyboard focusable itself but contains a focusable element (link, button, field): check that this element triggers the same action (7.3.1 second condition); NC otherwise.', n)
                else:
                    self.add("fail", "7.3", "7.3.1", f'Element with {what} is not keyboard focusable (no tabindex="0", not a native control): NC unless an equivalent keyboard-accessible control exists.', n)
            if role in NAMED_ROLES and role not in ("img",) and not n.hidden():
                name, _ = accessible_name(n, self.byid, self.labels_for)
                # link and button are reported under 6.2 / 11.9 / 7.1 by check_links and check_forms
                if not name and role not in ("form", "region", "table", "grid", "tree", "listbox", "menu", "menubar", "toolbar", "tablist", "radiogroup", "button", "link"):
                    self.add("fail", "7.1", "7.1.1", f'role="{role}" without accessible name: the name is not exposed to assistive technologies.', n)
            for a in ("aria-labelledby", "aria-describedby", "aria-controls", "aria-owns", "aria-activedescendant", "aria-details", "aria-errormessage", "aria-flowto"):
                ids = (n.get(a) or "").split()
                missing = [i for i in ids if i not in self.byid]
                if missing:
                    self.add("fail", "7.1", "7.1.1", f'{a} references missing id(s): {", ".join(missing)}.', n)
            if n.has("onmouseover") and not n.has("onfocus"):
                self.add("review", "7.3", "7.3.1", "onmouseover without keyboard equivalent (onfocus).", n)
            if n.tag in ("a", "button", "input", "select", "textarea") and n.has("onfocus") and re.search(r"blur\(\)", n.get("onfocus") or ""):
                self.add("fail", "7.3", "7.3.2", "Script removes focus (blur()) from an element receiving it.", n)
            if role in ("dialog", "alertdialog"):
                self.add("review", "7.1", "7.1.1", f'Dialog "{accessible_name(n, self.byid, self.labels_for)[0][:40]}": check aria-modal/inert on background, focus moved in on open and restored on close, Escape closes (7.3, 12.9).', n)
            if role in ("alert", "status", "log") or n.get("aria-live"):
                self.add("info", "7.5", "7.5.1", f"Live region ({role or 'aria-live=' + (n.get('aria-live') or '')}): check status messages are rendered by AT.", n)
            if n.tag in ("details", "dialog"):
                self.add("info", "7.1", "7.1.2", f"<{n.tag}> native component: check rendering in the test environment.", n)
        scripts = [s for s in self.root.find_all("script") if not s.get("type") or "javascript" in (s.get("type") or "").lower() or "module" in (s.get("type") or "").lower()]
        if scripts:
            self.add("info", "7.1", None, f"{len(scripts)} script(s): components generated or controlled by JavaScript must be tested with a screen reader (7.1.2) and with the keyboard (7.3); check context changes (7.4) and status messages (7.5).")

    def check_media(self):
        media = [n for n in self.body.find_all("audio", "video") if not n.hidden()]
        self.inventory["media"] = len(media)
        for n in media:
            if n.has("autoplay") and not n.has("muted"):
                if n.has("controls"):
                    self.add("review", "4.10", "4.10.1", f"<{n.tag}> autoplays with sound: controls exist, check the sound can be stopped/volume controlled independently within 3 s.", n)
                else:
                    self.add("fail", "4.10", "4.10.1", f"<{n.tag}> autoplays with sound and has no controls.", n)
            if not n.has("controls"):
                self.add("review", "4.11", "4.11.1", f"<{n.tag}> without native controls: check custom controls are keyboard operable and AT compatible (4.11, 4.13).", n)
            if n.tag == "video":
                tracks = [t for t in n.find_all("track") if (t.get("kind") or "subtitles").lower() in ("captions", "subtitles")]
                desc = [t for t in n.find_all("track") if (t.get("kind") or "").lower() == "descriptions"]
                self.add("review" if not tracks else "info", "4.3", "4.3.1", ("No captions track: if the video has speech, synchronised captions are required (4.3) and a transcript or audio description (4.1)." if not tracks else f"{len(tracks)} caption track(s): check relevance (4.4)."), n)
                if not desc:
                    self.add("review", "4.5", "4.5.1", "No audio-description track: needed if visual information is not available in the soundtrack (4.5, AA).", n)
            else:
                self.add("review", "4.1", "4.1.1", "Audio-only media: a text transcript is required if it conveys information (4.1).", n)
            self.add("review", "4.7", "4.7.1", f"<{n.tag}>: the media must be clearly identifiable (title/adjacent text).", n)
        if media:
            self.add("info", "4.1", None, "Time-based media found: criteria 4.1 to 4.13 (and 4.14 to 4.18 in RAWeb 1.1) apply.")
        for n in self.body.find_all("object", "embed"):
            if not (n.get("type") or "").lower().startswith("image/"):
                self.add("review", "4.8", "4.8.1", f"<{n.tag}> non-image content: needs an alternative (4.8/4.9), keyboard control (4.12) and AT compatibility (4.13).", n)

    def check_preconditions(self):
        """Applicability signals, mirroring the SIP simplified-audit preconditions (simplA11yMonit)."""
        els = [n for n in self.body.elements() if not n.hidden()]
        def is_image_link(n):
            p = n.parent
            return p is not None and p.tag == "a" and len([c for c in p.children if c.tag]) == 1
        imgs = [n for n in els if (n.tag in ("img", "area", "svg", "canvas") or n.role() == "img" or (n.tag == "input" and (n.get("type") or "").lower() == "image") or (n.tag in ("object", "embed") and (n.get("type") or "").lower().startswith("image/"))) and not is_image_link(n)]
        frames = [n for n in els if n.tag in ("iframe", "frame")]
        tables = [n for n in els if n.tag == "table" or n.role() == "table"]
        form_roles = {"progressbar", "slider", "spinbutton", "textbox", "listbox", "searchbox", "combobox", "option", "checkbox", "radio", "switch"}
        fields = [n for n in els if n.tag in ("select", "textarea", "datalist", "optgroup", "option", "output", "progress", "meter") or (n.tag == "input" and (n.get("type") or "text").lower() not in ("hidden", "submit", "reset", "button", "image")) or n.role() in form_roles]
        media = [n for n in els if n.tag in ("audio", "video")] + [f for f in frames if re.search(r"(youtube|youtu\.be|vimeo|dailymotion|soundcloud|spotify)", (f.get("src") or "").lower())]
        pre = []
        pre.append(("1.1, 1.2, 1.3, 1.6, 1.7 (and 1.8, 1.9)", "images (excluding image links)", len(imgs)))
        pre.append(("2.1, 2.2", "frames", len(frames)))
        pre.append(("5.1 to 5.8", "tables", len(tables)))
        pre.append(("11.1 to 11.13", "form controls", len(fields)))
        pre.append(("4.1 to 4.13 (4.18 in RAWeb)", "time-based or embedded media", len(media)))
        self.inventory["preconditions"] = {name: count for _, name, count in pre}
        for crits, name, count in pre:
            if count == 0:
                self.add("info", "0.0", None, f"No {name} on this page: criteria {crits} are candidates for NA (unless such content is injected by scripts).")

    def check_misc(self):
        body_text = text_of(self.body, self.byid)
        if re.search(r"(en rouge|in red|en vert|in green|en gras|in bold|à droite|on the right|à gauche|on the left|ci-dessus|above|ci-dessous|below|rond|round button|carré|square)", body_text, re.I):
            self.add("review", "3.1", "3.1.1", "Text refers to colour, shape or position (e.g. 'in red', 'on the right'): check the information is also given otherwise (3.1 / 10.9).")
        for n in self.body.elements():
            if n.tag in ("input", "button", "a", "select", "textarea") and n.has("title") and not n.get("aria-label"):
                pass
            if n.tag == "abbr" and not norm(n.get("title")):
                self.add("info", "13.5", "13.5.1", "<abbr> without title (in RAWeb 1.1, abbr/title is no longer a compliant method for cryptic content anyway).", n)
        if re.search(r"(captcha|recaptcha|hcaptcha)", "".join(n.get("class") or "" for n in self.body.elements()) + " " + "".join(n.get("src") or "" for n in self.body.find_all("iframe", "script")), re.I):
            self.add("review", "1.4", "1.4.1", "CAPTCHA detected: its alternative must identify its nature (1.4) and an alternative access solution is required (1.5).")
        self.add("info", "3.2", None, "Contrast (3.2, 3.3), focus visibility (10.7), 200 % zoom (10.4), reflow at 320 px (10.11), text spacing (10.12), hover/focus content (10.13), orientation (13.9), gestures (13.10, 13.11) and flashes (13.7) need a rendered page: test them in a browser.")

    def run(self):
        for c in (self.check_page, self.check_images, self.check_frames, self.check_links, self.check_headings, self.check_landmarks,
                  self.check_lists, self.check_tables, self.check_forms, self.check_scripts, self.check_media, self.check_preconditions, self.check_misc):
            try:
                c()
            except Exception as e:  # keep going: one broken check must not hide the others
                self.add("info", "0.0", None, f"check {c.__name__} crashed: {e!r}")
        return self.findings


def crit_key(cid):
    try:
        return tuple(int(x) for x in cid.split("."))
    except ValueError:
        return (999,)


def render_markdown(sc, findings, source, standard, lang):
    std_name = "RGAA 4.1.2" if standard == "rgaa" else "RAWeb 1.1"
    fails = [f for f in findings if f["status"] == "fail"]
    reviews = [f for f in findings if f["status"] == "review"]
    crits_fail = sorted({f["criterion"] for f in fails}, key=crit_key)
    out = [f"# Static pre-check — {source}", "", f"Standard: {std_name}. Findings: **{len(fails)} likely non-conformities** on {len(crits_fail)} criteria ({', '.join(crits_fail)}), {len(reviews)} points to review, {len(findings) - len(fails) - len(reviews)} informational.", "",
           "Limits: static analysis of the delivered HTML only (no rendering, no contrast, no screen reader, no keyboard, no JavaScript behaviour). A criterion without findings is not compliant by default; everything applicable still has to be tested.", ""]
    inv = sc.inventory
    out.append("## Inventory")
    for k, v in inv.items():
        out.append(f"- {k}: {v}")
    out.append("")
    by = {}
    for f in findings:
        by.setdefault(f["criterion"], []).append(f)
    label = {"fail": "FAIL", "review": "REVIEW", "info": "INFO"}
    for cid in sorted(by, key=crit_key):
        lvl, title = sc.titles.get(cid, ("?", ""))
        out.append(f"## {cid} [{lvl}] {title}" if cid != "0.0" else "## Applicability (preconditions)")
        order = {"fail": 0, "review": 1, "info": 2}
        for f in sorted(by[cid], key=lambda x: (order[x["status"]], x["line"] or 0)):
            loc = f" line {f['line']}" if f["line"] else ""
            el = f" `{f['element']}`" if f["element"] else ""
            test = f" (test {f['test']})" if f["test"] else ""
            out.append(f"- **{label[f['status']]}**{test}{loc}:{el} {f['message']}")
        out.append("")
    return "\n".join(out)


def load_stylesheet(href, source, _cache={}):
    """Return the text of a linked stylesheet, or None. URL sources are fetched (same proxy/UA as the page);
    file sources resolve relative hrefs next to the file. Failures are silent: the check is best effort."""
    import urllib.parse
    key = (href, source)
    if key in _cache:
        return _cache[key]
    css = None
    try:
        if re.match(r"^https?://", source) or href.startswith("http"):
            url = urllib.parse.urljoin(source if re.match(r"^https?://", source) else "", href)
            if url.startswith("http"):
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (accessibility-audit static scanner)"})
                with urllib.request.urlopen(req, timeout=30) as resp:
                    css = resp.read(3_000_000).decode("utf-8", errors="replace")
        else:
            path = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(source)), href.split("?")[0].lstrip("/") if href.startswith("/") else href.split("?")[0]))
            if os.path.exists(path) and os.path.getsize(path) < 3_000_000:
                css = open(path, encoding="utf-8", errors="replace").read()
    except Exception:
        css = None
    _cache[key] = css
    return css


def fetch(source, render):
    if re.match(r"^https?://", source):
        if render:
            js = os.path.join(HERE, "render_page.js")
            r = subprocess.run(["node", js, source], capture_output=True, text=True)
            if r.returncode != 0:
                sys.exit(f"render failed: {r.stderr.strip()}")
            return r.stdout
        req = urllib.request.Request(source, headers={"User-Agent": "Mozilla/5.0 (accessibility-audit static scanner)", "Accept-Language": "fr,en;q=0.8,de;q=0.6"})
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                raw = resp.read()
                ct = resp.headers.get_content_charset() or "utf-8"
        except Exception as e:
            sys.exit(f"cannot fetch {source}: {e}. Save the page as HTML (or use render_page.js) and scan the file.")
        try:
            return raw.decode(ct)
        except (LookupError, UnicodeDecodeError):
            return raw.decode("utf-8", errors="replace")
    if not os.path.isfile(source):
        sys.exit(f"{source}: no such file (give an HTML file or an http(s) URL)")
    return open(source, encoding="utf-8-sig", errors="replace").read()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("source", help="HTML file or http(s) URL")
    ap.add_argument("--standard", choices=["raweb", "rgaa"], default="raweb")
    ap.add_argument("--lang", choices=["en", "fr"], default=None)
    ap.add_argument("--render", action="store_true", help="render the URL with a browser first (node + playwright)")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--no-info", action="store_true", help="hide informational findings")
    a = ap.parse_args()
    lang = a.lang or ("fr" if a.standard == "rgaa" else "en")
    html = fetch(a.source, a.render)
    b = TreeBuilder()
    b.feed(html)
    b.close()
    sc = Scanner(b.root, b, a.standard, lang, a.source)
    findings = sc.run()
    if a.no_info:
        findings = [f for f in findings if f["status"] != "info"]
    if a.json:
        print(json.dumps({"source": a.source, "standard": "RGAA 4.1.2" if a.standard == "rgaa" else "RAWeb 1.1", "inventory": sc.inventory, "findings": findings}, ensure_ascii=False, indent=1))
    else:
        print(render_markdown(sc, findings, a.source, a.standard, lang))


if __name__ == "__main__":
    main()
