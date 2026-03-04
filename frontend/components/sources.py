"""
Source citations — redesigned Perplexity-style cards.
"""
import streamlit as st


_DOMAIN_BADGE = {
    "tax": '<span class="lf-badge domain-tax">TAX</span>',
    "finance": '<span class="lf-badge domain-finance">FINANCE</span>',
    "legal": '<span class="lf-badge domain-legal">LEGAL</span>',
}

_ORIGIN_BADGE = {
    "system": '<span class="lf-badge system">SYSTEM</span>',
    "user":   '<span class="lf-badge user">YOUR FILE</span>',
}

_DOMAIN_ICON = {"tax": "💰", "finance": "🏦", "legal": "📜", "user_upload": "📎"}


def render_sources(sources: list, key_prefix: str = "src"):
    """Render collapsible source panel beneath an answer."""
    if not sources:
        return

    # Inline citation chips
    chips_html = '<div style="margin-top:0.6rem; display:flex; flex-wrap:wrap; gap:0.3rem;">'
    for s in sources:
        ref = s.get("reference_id", "?")
        name = s.get("source", "Unknown")
        short = name[:24] + "…" if len(name) > 24 else name
        chips_html += (
            f'<span class="lf-source-inline">[{ref}] {short}</span>'
        )
    chips_html += "</div>"
    st.markdown(chips_html, unsafe_allow_html=True)

    # Expandable full cards
    with st.expander(f"📚 {len(sources)} source{'s' if len(sources) > 1 else ''}", expanded=False):
        for s in sources:
            _render_card(s)


def _render_card(source: dict):
    ref = source.get("reference_id", "?")
    name = source.get("source", "Unknown")
    domain = source.get("domain", "unknown")
    origin = source.get("origin", "system")
    score = float(source.get("relevance_score") or source.get("rerank_score") or 0)
    excerpt = source.get("excerpt", "")

    icon = _DOMAIN_ICON.get(domain, "📄")
    domain_badge = _DOMAIN_BADGE.get(domain, f'<span class="lf-badge">{domain.upper()}</span>')
    origin_badge = _ORIGIN_BADGE.get(origin, _ORIGIN_BADGE["system"])

    score_class = "high" if score >= 0.65 else ("mid" if score >= 0.35 else "low")
    score_pct = min(int(score * 100), 100)

    st.markdown(
        f"""<div class="lf-source-card">
          <div class="lf-source-card-header">
            <div class="lf-source-title">[{ref}] {icon} {name}</div>
            <div style="display:flex;gap:0.35rem;">{domain_badge}{origin_badge}</div>
          </div>
          <div class="lf-score-bar">
            <div class="lf-score-fill {score_class}" style="width:{score_pct}%"></div>
          </div>
          <div class="lf-source-meta">
            <span>Score: {score:.3f}</span>
          </div>
          {'<div class="lf-source-excerpt">'+excerpt[:300]+('…' if len(excerpt)>300 else '')+'</div>' if excerpt else ''}
        </div>""",
        unsafe_allow_html=True,
    )
