# -*- coding: utf-8 -*-
"""RILAB-O > Lecture > Robotics 노션 페이지를 md + figures 로 내려받는다."""
import json, os, re, time, urllib.request, urllib.parse

BASE = "https://rilab.notion.site"
ROOT = "d2dd5984-a6e3-4ef3-9549-adc5dde9e717"
OUT  = r"F:\work\lecture\material\로봇공학\자료원본"
FIG  = os.path.join(OUT, "figures")

os.makedirs(FIG, exist_ok=True)
log = []

# ---------- 노션 공개 API ----------
def post(path, body):
    req = urllib.request.Request(BASE + path, data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"})
    err = None
    for _ in range(3):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read().decode())
        except Exception as e:
            err = e; time.sleep(2)
    raise err

def load_page(pid):
    blocks, cursor, chunk = {}, {"stack": []}, 0
    while True:
        r = post("/api/v3/loadPageChunk", {"pageId": pid, "limit": 100,
                 "cursor": cursor, "chunkNumber": chunk, "verticalColumns": False})
        for k, v in r.get("recordMap", {}).get("block", {}).items():
            val = v.get("value", {}); val = val.get("value", val)
            if val: blocks[k] = val
        cursor = r.get("cursor", {"stack": []}); chunk += 1
        if not cursor.get("stack"): break
    return blocks

# ---------- 파일명 ----------
def safe(name, maxlen=80):
    name = re.sub(r'[\\/:*?"<>|\r\n\t]', "_", name).strip().rstrip(".")
    return (name or "untitled")[:maxlen]

# ---------- 리치 텍스트 ----------
def rich(items, blocks):
    out = []
    for it in items or []:
        txt = it[0]
        fmts = it[1] if len(it) > 1 else []
        link = None
        for f in fmts:
            t = f[0]
            if t == "e":
                txt = "$" + f[1] + "$"
            elif t == "p":
                ref = blocks.get(f[1], {})
                nm = "".join(x[0] for x in ref.get("properties", {}).get("title", [])) or "페이지"
                txt = "[[" + nm + "]]"
            elif t == "d":
                d = f[1]
                txt = d.get("start_date", "") + (("~" + d["end_date"]) if d.get("end_date") else "")
            elif t == "u":
                txt = "@user"
        for f in fmts:
            t = f[0]
            if t == "c": txt = "`" + txt + "`"
            elif t == "b": txt = "**" + txt + "**"
            elif t == "i": txt = "*" + txt + "*"
            elif t == "s": txt = "~~" + txt + "~~"
            elif t == "_": txt = "<u>" + txt + "</u>"
            elif t == "a": link = f[1]
        if link:
            txt = "[" + txt + "](" + link + ")"
        out.append(txt)
    return "".join(out)

def plain(items):
    return "".join(x[0] for x in (items or []))

# ---------- 이미지/파일 ----------
def download(src, bid, space, dest):
    if src.startswith("http") and "amazonaws.com" not in src and "notion" not in src:
        url = src
    else:
        url = BASE + "/image/" + urllib.parse.quote(src, safe="") + "?table=block&id=" + bid + "&cache=v2"
        if src.startswith("attachment:"):
            url += "&spaceId=" + space
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=300) as r:
        data = r.read()
    if data[:1] == b"<" or data[:9].lower().startswith(b"<!doctype"):
        raise ValueError("HTML 응답(차단 페이지)")     # 이미지가 아니라 안내 페이지가 온 경우
    with open(dest, "wb") as f:
        f.write(data)
    return len(data)

# ---------- 블록 -> 마크다운 ----------
class Ctx:
    def __init__(self, prefix):
        self.prefix = prefix
        self.n = 0
        self.subpages = []

def render(ids, blocks, ctx, indent=0):
    lines, num = [], 0
    prev = None
    pad = "    " * indent
    for bid in ids:
        b = blocks.get(bid)
        if not b or not b.get("alive", True): continue
        t = b.get("type")
        props = b.get("properties", {}) or {}
        title = props.get("title", [])
        kids = b.get("content", [])

        if t not in ("numbered_list",) and prev == "numbered_list":
            num = 0
        if t == "page":
            nm = plain(title)
            ctx.subpages.append((nm, bid))
            lines.append(pad + "- 하위 문서: **" + nm + "** (별도 md 파일 참고)")
            continue
        if t in ("table_of_contents", "breadcrumb"): continue
        if t == "divider":
            lines.append(""); lines.append("---"); lines.append(""); continue
        # 목록 뒤에 바로 문단이 오면 목록에 딸려 붙으므로 빈 줄로 끊는다
        if prev in ("bulleted_list", "numbered_list", "to_do") and t not in ("bulleted_list", "numbered_list", "to_do"):
            lines.append("")

        if t == "header":             lines.append("# " + rich(title, blocks))
        elif t == "sub_header":       lines.append("## " + rich(title, blocks))
        elif t == "sub_sub_header":   lines.append("### " + rich(title, blocks))
        elif t == "text":
            s = rich(title, blocks)
            lines.append(pad + s if s.strip() else "")
        elif t == "bulleted_list":
            lines.append(pad + "- " + rich(title, blocks))
        elif t == "numbered_list":
            num += 1
            lines.append(pad + str(num) + ". " + rich(title, blocks))
        elif t == "to_do":
            chk = "x" if plain(props.get("checked", [])) == "Yes" else " "
            lines.append(pad + "- [" + chk + "] " + rich(title, blocks))
        elif t == "quote":
            lines.append(pad + "> " + rich(title, blocks).replace("\n", "\n" + pad + "> "))
        elif t == "callout":
            icon = (b.get("format", {}) or {}).get("page_icon", "")
            if not isinstance(icon, str) or len(icon) > 4: icon = ""
            lines.append(pad + "> " + icon + " " + rich(title, blocks).replace("\n", "\n" + pad + "> "))
        elif t == "code":
            lang = plain(props.get("language", [])).lower().replace(" ", "")
            if lang in ("plaintext", ""): lang = "text"
            lines.append(pad + "```" + lang)
            for ln in plain(title).split("\n"): lines.append(pad + ln)
            lines.append(pad + "```")
        elif t == "equation":
            lines.append(pad + "$$"); lines.append(pad + plain(title)); lines.append(pad + "$$")
        elif t == "toggle":
            lines.append(pad + "<details><summary>" + rich(title, blocks) + "</summary>")
            lines.append("")
            lines += render(kids, blocks, ctx, indent)
            lines.append("")
            lines.append(pad + "</details>")
            kids = []
        elif t in ("image", "video", "file", "pdf", "audio"):
            src = plain(props.get("source", [])) or (b.get("format", {}) or {}).get("display_source", "")
            cap = rich(props.get("caption", []), blocks)
            if t != "image" and "amazonaws" not in src and "notion" not in src:
                # 유튜브 등 외부 영상은 내려받지 않고 링크만 남긴다
                lines.append(pad + "- 외부 영상/자료: [" + src + "](" + src + ")")
                continue
            name = plain(props.get("title", [])) or os.path.basename(urllib.parse.urlparse(src).path) or "file"
            ctx.n += 1
            ext = os.path.splitext(name)[1] or os.path.splitext(urllib.parse.urlparse(src).path)[1] or ".png"
            fname = ctx.prefix + "_" + ("%02d" % ctx.n) + ext.lower()
            dest = os.path.join(FIG, fname)
            try:
                sz = download(src, bid, b.get("space_id", ""), dest)
                log.append((fname, sz, t))
                if t == "image":
                    lines.append(pad + "![" + (cap or name) + "](figures/" + fname + ")")
                else:
                    lines.append(pad + "[" + t + " 첨부: " + (cap or name) + "](figures/" + fname + ")")
            except Exception as e:
                log.append((fname, -1, t + " FAIL " + str(e) + " " + src[:120]))
                lines.append(pad + "![" + (cap or name) + "](" + src + ")  <!-- 원격 이미지: 내려받기 실패 -->")
            if cap and t == "image":
                lines.append("")
                lines.append(pad + "*" + cap + "*")
        elif t == "bookmark":
            url = plain(props.get("link", []))
            lines.append(pad + "- [" + (plain(title) or url) + "](" + url + ")")
        elif t in ("embed", "tweet", "gist", "figma", "drive"):
            lines.append(pad + "- embed: " + plain(props.get("source", [])))
        elif t in ("column_list", "column"):
            lines += render(kids, blocks, ctx, indent); kids = []
        elif t in ("collection_view", "collection_view_page"):
            lines.append(pad + "<!-- 노션 데이터베이스 뷰(변환 생략) -->")
        elif t == "table":
            fmt = b.get("format", {}) or {}
            cols = fmt.get("table_block_column_order", [])
            hdr = fmt.get("table_block_column_header", False)
            rows = []
            for rid in kids:
                rb = blocks.get(rid, {})
                rp = rb.get("properties", {}) or {}
                rows.append([rich(rp.get(c, []), blocks).replace("\n", "<br>").replace("|", "\\|") for c in cols])
            if rows:
                # 마크다운 표는 헤더가 필수라 첫 행을 헤더로 올린다(노션 헤더 설정과 무관)
                head, body = rows[0], rows[1:]
                lines.append("| " + " | ".join(head) + " |")
                lines.append("|" + "|".join([" --- "] * len(cols)) + "|")
                for r in body:
                    lines.append("| " + " | ".join(r) + " |")
            kids = []
        elif t is None:
            continue
        else:
            lines.append(pad + "<!-- 미지원 블록: " + str(t) + " -->")

        if kids and t != "table":
            step = 1 if t in ("bulleted_list", "numbered_list", "to_do") else 0
            sub = render(kids, blocks, ctx, indent + step)
            if sub: lines += sub
        # 목록을 뺀 블록은 뒤에 빈 줄을 둬야 마크다운에서 문단이 분리된다
        if t not in ("bulleted_list", "numbered_list", "to_do"):
            lines.append("")
        prev = t
    return lines

# ---------- 페이지 저장 ----------
saved = []
def export(pid, num_prefix, parent_title=None):
    blocks = load_page(pid)
    b = blocks.get(pid, {})
    title = plain(b.get("properties", {}).get("title", []))
    ctx = Ctx(num_prefix)
    body = render(b.get("content", []), blocks, ctx)
    fname = num_prefix + "_" + safe(title) + ".md"
    header = ["# " + title, "",
              "> 출처: 노션 RILAB-O > Lecture > Robotics > " + title,
              "> 원본 링크: https://rilab.notion.site/" + pid.replace("-", ""), ""]
    if parent_title:
        header.insert(3, "> 상위 문서: " + parent_title)
    text = "\n".join(header + body).rstrip() + "\n"
    text = re.sub(r"\n{3,}", "\n\n", text)
    with open(os.path.join(OUT, fname), "w", encoding="utf-8") as f:
        f.write(text)
    saved.append((num_prefix, fname, title))
    print("saved " + fname + "  (" + str(len(text)) + " chars, " + str(ctx.n) + " files)", flush=True)
    for i, (subname, subid) in enumerate(ctx.subpages, 1):
        export(subid, num_prefix + "-" + str(i), title)

root = load_page(ROOT)
children = root[ROOT]["content"]
for i, cid in enumerate(children, 1):
    export(cid, "%02d" % i)

idx = ["# 로봇공학 강의자료 원본 (노션 백업)", "",
       "노션 `RILAB-O > Lecture > Robotics` 하위 전체 문서를 마크다운으로 내려받은 것이다.",
       "이미지는 모두 `figures/` 폴더에 있고 각 md에서 상대경로로 참조한다.", "",
       "| 번호 | 문서 | 파일 |", "| --- | --- | --- |"]
for num, fname, title in saved:
    idx.append("| " + num + " | " + title + " | [" + fname + "](" + urllib.parse.quote(fname) + ") |")
ok = [x for x in log if x[1] > 0]
fail = [x for x in log if x[1] < 0]
idx += ["", "총 " + str(len(saved)) + "개 문서, 이미지/첨부 " + str(len(ok)) +
        "개 (" + ("%.1f" % (sum(x[1] for x in ok) / 1e6)) + " MB)"]
if fail:
    idx += ["", "## 내려받지 못한 첨부"] + ["- " + x[0] + " (" + x[2] + ")" for x in fail]
with open(os.path.join(OUT, "00_목차.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(idx) + "\n")

print("")
print("문서 " + str(len(saved)) + "개, 첨부 " + str(len(ok)) + "개 성공, " + str(len(fail)) +
      "개 실패, 총 " + ("%.1f" % (sum(x[1] for x in ok) / 1e6)) + " MB")
for x in fail: print("FAIL", x)
