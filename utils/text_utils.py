def clean_section_title(title):
    title = title.strip()
    if len(title) > 100:
        title = title[:97].rstrip() + "..."
    while title and title[-1] in ":.":
        title = title[:-1].strip()
    if not title:
        title = "Untitled Section"
    return title

def clean_repetitive_prefix(summary):
    triggers = [
        "you are a travel planner",
        "summarize the following",
        "summarize 3 detailed"
    ]
    s_lower = summary.lower()
    for t in triggers:
        if s_lower.startswith(t):
            return summary[len(t):].strip()
    return summary
