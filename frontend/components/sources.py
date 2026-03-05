"""
Source citations with expandable cards and citation-claim highlights.
"""

import streamlit as st

_DOMAIN_BADGE = {
    "tax": '<span class="lf-badge tax">TAX</span>',
    "finance": '<span class="lf-badge fin">FINANCE</span>',
    "legal": '<span class="lf-badge leg">LEGAL</span>',
}
_ORIGIN_BADGE = {
    "system": '<span class="lf-badge sys">SYSTEM</span>',
    "user": '<span class="lf-badge usr">YOUR FILE</span>',
}
_ICON = {"tax": "T", "finance": "F", "legal": "L", "user_upload": "U"}


def render_sources(sources: list, key_prefix: str = "s"):
    if not sources:
        return

    chips = "".join(
        f'<span class="lf-src-chip">[{s.get("reference_id","?")}] '
        f'{s.get("source","Unknown")[:22]}{"..." if len(s.get("source","")) > 22 else ""}</span>'
        for s in sources
    )
    st.markdown(f'<div class="lf-src-chips">{chips}</div>', unsafe_allow_html=True)

    with st.expander(
        f"{len(sources)} source{'s' if len(sources) > 1 else ''}",
        expanded=False,
    ):
        for s in sources:
            _card(s)


def _card(s: dict):
    ref = s.get("reference_id", "?")
    name = s.get("source", "Unknown")
    domain = s.get("domain", "unknown")
    origin = s.get("origin", "system")
    score = float(s.get("relevance_score") or s.get("rerank_score") or 0)
    excerpt = s.get("excerpt", "")
    citation_spans = s.get("citation_spans", [])

    icon = _ICON.get(domain, "D")
    dbadge = _DOMAIN_BADGE.get(domain, f'<span class="lf-badge">{domain.upper()}</span>')
    obadge = _ORIGIN_BADGE.get(origin, _ORIGIN_BADGE["system"])
    sc = "hi" if score >= 0.65 else ("md" if score >= 0.35 else "lo")
    pct = min(int(score * 100), 100)
    claims = ", ".join(c.get("claim", "")[:80] for c in citation_spans[:3])

    st.markdown(
        f"""<div class="lf-src-card">
          <div class="lf-src-top">
            <div class="lf-src-name">[{ref}] {icon} {name}</div>
            <div class="lf-badge-wrap">{dbadge}{obadge}</div>
          </div>
          <div class="lf-score-bar">
            <div class="lf-score-fill {sc}" style="width:{pct}%"></div>
          </div>
          <div class="lf-src-meta">Relevance score: {score:.3f}</div>
          {'<div class="lf-src-excerpt">' + excerpt[:300] + ('...' if len(excerpt) > 300 else '') + '</div>' if excerpt else ''}
          {'<div class="lf-src-meta">Cited claims: ' + claims + '</div>' if claims else ''}
        </div>""",
        unsafe_allow_html=True,
    )
