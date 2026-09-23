#!/usr/bin/env python3
"""mermaid_page.py: build an HTML page that parses and renders every mermaid block.

Usage: python3 .claude/skills/zenn-post-review/scripts/mermaid_page.py <slug> <out_dir>

Writes <out_dir>/mermaid_check.html. Serve out_dir with `python3 -m http.server`,
open the page in the browser pane, and read the tab title:
"m0:ok | m1:ERR <message> | ...". file:// pages cannot be inspected, so serve it.
"""
import html
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        return 2
    text = (REPO / "articles" / f"{sys.argv[1]}.md").read_text()
    blocks = re.findall(r"```mermaid\n(.*?)```", text, re.S)
    body = "".join(
        f'<h3>m{i} ({len(b)} chars{", OVER 2000" if len(b) > 2000 else ""})</h3>'
        f'<pre class="mermaid" id="m{i}">{html.escape(b)}</pre>'
        for i, b in enumerate(blocks)
    )
    page = f"""<!doctype html><meta charset="utf-8"><title>checking</title>
<script src="https://cdn.jsdelivr.net/npm/mermaid@10.9.1/dist/mermaid.min.js"></script>
{body}
<script>
mermaid.initialize({{startOnLoad:false}});
(async()=>{{
  const r=[];
  for(const el of document.querySelectorAll('.mermaid')){{
    try{{await mermaid.parse(el.textContent);r.push(el.id+':ok')}}
    catch(e){{r.push(el.id+':ERR '+String(e.message).slice(0,160))}}
  }}
  await mermaid.run();
  document.title=r.join(' | ');
}})();
</script>"""
    out = Path(sys.argv[2]) / "mermaid_check.html"
    out.write_text(page)
    print(f"{len(blocks)} block(s) -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
