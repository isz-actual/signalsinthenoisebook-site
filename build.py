#!/usr/bin/env python3
"""Static site generator for signalsinthenoisebook.com.
Edit page content in PAGES below, run `python3 build.py`, output goes to _site/.
GitHub Actions builds and deploys on every push to main.
"""
import json, os, html, shutil

SITE = "https://www.signalsinthenoisebook.com"
FU = SITE + "/assets/img/"  # images live in /assets/img (downloaded from Framer by fetch_images.py)
BUY = "https://books2read.com/signals-in-the-noise"
CAL = "https://calendly.com/tim-reed-isz/30min"
NEWS = "https://www.thenorthernsignal.com/"
POD = "https://open.spotify.com/episode/7EvJzyGvM8SOkeVFV3g3KO"
EMAIL = "contact@iszpress.com"
BOOK_TITLE = "Signals in the Noise: Security, Technology, and the Hidden Patterns of Modern Risk"
AUTHOR = "Timothy E. Reed, CPP"

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "_site")

NAV = [("/", "Home"), ("/about-the-book", "About the Book"), ("/inside-the-book", "Inside the Book"),
       ("/boards-leaders", "Boards & Leaders"), ("/newsletter-podcast", "Newsletter & Podcast")]
FOOT = [("About", [("/about-the-book", "About the Book"), ("/inside-the-book", "Inside the Book"), ("/boards-leaders", "Boards & Leaders")]),
        ("Media", [("/newsletter-podcast", "Newsletter & Podcast"), ("/advisory", "Advisory"), ("/isz-press", "ISZ Press")]),
        ("Contact", [("/contact", "Contact"), (BUY, "Get the Book"), ("/about-the-author", "About the Author"), ("/privacy-policy", "Privacy Policy")])]

PERSON = {"@type": "Person", "@id": SITE + "/about-the-author#person", "name": "Timothy E. Reed",
          "honorificSuffix": "CPP", "alternateName": "Tim Reed",
          "jobTitle": "Security strategist, author, and advisor", "url": SITE + "/about-the-author",
          "knowsAbout": ["Corporate security", "AI governance", "Risk management", "Physical security",
                         "Intelligence", "Board risk oversight", "Supply chain security"],
          "sameAs": [NEWS]}  # TODO: add LinkedIn and other profile URLs
ORG = {"@type": "Organization", "@id": SITE + "/isz-press#org", "name": "ISZ Press",
       "alternateName": "Ice Station Zebra Press", "url": SITE + "/isz-press", "email": EMAIL}
BOOK = {"@type": "Book", "@id": SITE + "/#book", "name": BOOK_TITLE, "alternateName": "Signals in the Noise",
        "author": {"@id": PERSON["@id"]}, "publisher": {"@id": ORG["@id"]},
        "image": FU + "3ZMCU7NKW0huxlM1k6EkWJE45nI.jpg", "url": SITE + "/about-the-book",
        "isbn": "9798993667614", "inLanguage": "en", "datePublished": "2026", "wordCount": 38000,
        "description": "A field guide for security leaders, boards, and executives on finding real signals in AI-driven noise, governing algorithmic risk, and building organizational clarity.",
        "about": ["AI governance", "Security leadership", "Risk management", "Board oversight", "Signal detection"],
        "audience": {"@type": "Audience", "audienceType": "CSOs, CISOs, board directors, technology founders and operators"},
        "offers": {"@type": "Offer", "url": BUY, "availability": "https://schema.org/InStock"}}
        # TODO: add "bookFormat"/"workExample" entries per format (ebook, paperback, audiobook) with their own ISBNs

def esc(s): return html.escape(s, quote=True)

def ld(*items):
    return '<script type="application/ld+json">' + json.dumps({"@context": "https://schema.org", "@graph": list(items)}, ensure_ascii=False) + "</script>"

def crumbs(path, name):
    items = [{"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"}]
    if path != "/":
        items.append({"@type": "ListItem", "position": 2, "name": name, "item": SITE + path})
    return {"@type": "BreadcrumbList", "itemListElement": items}

def btn(href, label, ghost=False):
    ext = href.startswith("http")
    attrs = ' target="_blank" rel="noopener"' if ext else ""
    return f'<a class="btn{" ghost" if ghost else ""}" href="{esc(href)}"{attrs}>{esc(label)}</a>'

def cards(items, h="h3"):
    out = ['<div class="cards">']
    for img, title, text in items:
        out.append(f'<article class="card"><img src="{FU}{img}" alt="{esc(title.rstrip("."))}" loading="lazy" width="600" height="400">'
                   f'<{h}>{esc(title)}</{h}><p>{esc(text)}</p></article>')
    out.append("</div>")
    return "\n".join(out)

def faq(qs):
    body = "".join(f"<details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>" for q, a in qs)
    schema = {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q,
              "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in qs]}
    return f'<section class="faq"><h2>Frequently asked questions</h2>{body}</section>', schema

def cta(h, p, b):
    return f'<section class="cta"><h2>{esc(h)}</h2><p>{esc(p)}</p>{b}</section>'

def page(path, title, desc, body, schema=(), og_img="3ZMCU7NKW0huxlM1k6EkWJE45nI.jpg", name=None):
    url = SITE + (path if path != "/" else "/")
    nav = "".join(f'<a href="{h}"{" aria-current=\"page\"" if h == path else ""}>{esc(t)}</a>' for h, t in NAV)
    foot = "".join(f'<div><h2 class="fh">{c}</h2>' + "".join(
        f'<a href="{esc(h)}"{" target=\"_blank\" rel=\"noopener\"" if h.startswith("http") else ""}>{esc(t)}</a>' for h, t in links) + "</div>"
        for c, links in FOOT)
    graph = [crumbs(path, name or title)] + list(schema)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{url}">
<meta name="author" content="{esc(AUTHOR)}">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta property="og:type" content="{'book' if path in ('/', '/about-the-book') else 'website'}">
<meta property="og:site_name" content="Signals in the Noise">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{FU}{og_img}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(desc)}">
<meta name="twitter:image" content="{FU}{og_img}">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap">
<link rel="stylesheet" href="/assets/style.css">
<link rel="alternate" type="text/plain" href="/llms.txt" title="LLM summary">
{ld(*graph)}
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site"><nav aria-label="Main">{nav}</nav></header>
<main id="main">
{body}
</main>
<footer class="site"><div class="fcols">{foot}</div>
<p class="legal">&copy; 2026 Ice Station Zebra, LLC. <em>Signals in the Noise</em> is published by ISZ Press.</p></footer>
</body>
</html>
"""

PAGES = {}

# ---------- HOME ----------
f_home, s_home = faq([
    ("What is Signals in the Noise about?",
     "Signals in the Noise is a field guide for security leaders, boards, and executives. It explains how AI and automation flood organizations with information, and how leaders can separate real risk signals from noise to make clearer decisions."),
    ("Who wrote Signals in the Noise?",
     "Timothy E. Reed, CPP, a corporate security leader with more than 26 years of experience in physical security, intelligence, risk management, robotics, and AI. It is published by ISZ Press."),
    ("Who should read it?",
     "CSOs, CISOs, board directors, and technology founders and operators who are responsible for security, risk, or AI governance decisions."),
    ("Where can I buy the book?",
     "Signals in the Noise is available from Amazon and other major retailers. Bulk orders are also available."),
])
PAGES["/"] = page("/", "Signals in the Noise | A Field Guide to AI, Security, and Modern Risk",
    "Signals in the Noise by Timothy E. Reed, CPP is a field guide for security leaders and boards on cutting through AI-driven noise, governing algorithmic risk, and deciding with clarity.",
    f"""<section class="hero">
<img src="{FU}fdq8kmXa78ZPRx8HYiVwNlec.png" alt="Signals in the Noise: Security, Technology, and the Hidden Patterns of Modern Risk, book cover art" width="1200" height="720" fetchpriority="high">
<h1>Signals in the Noise: Security, Technology, and the Hidden Patterns of Modern Risk</h1>
<p class="lede">A field guide for security leaders and boards by Timothy E. Reed, CPP. AI increases visibility but not clarity. This book shows leaders how to find the signals that matter.</p>
<div class="btns">{btn(BUY, "Get the Book")}{btn("/inside-the-book", "Explore Chapters", True)}</div>
</section>
<section><h2>The problem leaders face</h2>
{cards([("LmYKwtB6thLI4GB21Bfg8rgLxI.jpeg", "Information overload.", "AI increases visibility, but not clarity. Leaders need stronger filtering."),
        ("vb8rys5VY7qXrIzCRcjxy4jDpf8.jpeg", "Operational blind spots.", "Automation outpaces governance across supply chains, identity, and IP pathways."),
        ("1EIPdmLc4WBBlbcjz6pUGmeCYQ.jpeg", "Competing realities.", "Synthetic data, algorithmic confidence, and fractured trust complicate decisions.")])}
</section>
<section><h2>Who the book is for</h2>
{cards([("EtKNdzuOonNYlOdnyDpcGRtL5U.jpeg", "CSOs & CISOs.", "Security leaders facing new risk frontiers."),
        ("XMnUkuqrkos2jrKL0oK1he52u4.jpeg", "Boards & Directors.", "Governance, oversight, and risk strategy."),
        ("Frc3e5PAm3ZqIaJJQEM8NTJzszM.jpeg", "Tech founders & operators.", "Building the future with clarity and discipline.")])}
</section>
{f_home}
{cta("Explore chapters.", "Preview the full table of contents and concepts.", btn("/inside-the-book", "Explore Chapters"))}""",
    [BOOK, PERSON, ORG, {"@type": "WebSite", "@id": SITE + "/#site", "url": SITE + "/", "name": "Signals in the Noise", "publisher": {"@id": ORG["@id"]}}, s_home],
    og_img="fdq8kmXa78ZPRx8HYiVwNlec.png", name="Home")

# ---------- ABOUT THE BOOK ----------
f_about, s_about = faq([
    ("How long is Signals in the Noise?", "About 38,000 words, written at a grade 12 reading level for busy professionals."),
    ("What is the ISBN for Signals in the Noise?", "ISBN 979-8993667614."),
    ("What will I learn from the book?", "How to identify real signals, design organizational clarity, avoid algorithmic traps, build cognitive resilience, and govern AI-driven complexity."),
    ("What topics do the chapters cover?", "Information overload, weaponized ambiguity, the blind spots of machine analysis, modern tradecraft, behavioral signatures, cognitive countermeasures, signal architecture, ethics, and emerging risks."),
])
PAGES["/about-the-book"] = page("/about-the-book", "About the Book | Signals in the Noise by Timothy E. Reed",
    "What Signals in the Noise covers: why AI creates noise instead of clarity, how leaders detect real risk signals, and how the book moves from information overload to human tradecraft.",
    f"""<section class="hero split">
<img src="{FU}3ZMCU7NKW0huxlM1k6EkWJE45nI.jpg" alt="Signals in the Noise book cover" width="600" height="900" fetchpriority="high">
<div><p class="eyebrow">About the Book</p>
<h1>Signals in the Noise</h1>
<p class="lede">A modern field guide for leaders.</p>
<div class="btns">{btn(BUY, "Get the Book")}</div></div>
</section>
<section class="prose"><h2>The core idea</h2>
<p>In an era where everything is observable yet less certain, <em>Signals in the Noise</em> shows how AI generates overwhelming noise, making leadership harder. The book argues that clarity, not technology, is the essential tool leaders must wield for security and resilience.</p>
<p>Only disciplined thought and strong signal detection can cut through increasing amounts of algorithmic confusion. This guide helps leaders find actionable insight where others see only overload.</p></section>
<section><h2>What you'll learn</h2>
{cards([("5rWtlU2czqFdjEjS93dE6ZeTmA.jpg", "Finding real signals.", "How to identify real signals and design organizational clarity to strengthen decision making."),
        ("ataJvCzgC7rJadWLh8EzeJ1z5Jw.jpg", "Avoiding traps.", "Counter information saturation, avoid algorithmic traps, and build lasting cognitive resilience."),
        ("MzSNq9P3zYWNEkBBYEP3XyoU4.jpg", "Governance mastery.", "Learn to govern AI-driven complexity and decode behavioral patterns and risk signals.")])}
</section>
<section class="prose"><h2>Readability and format</h2>
<p><em>Signals in the Noise</em> is approximately 38,000 words, written at a grade 12 readability level. The pacing is brisk, and the writing prioritizes clarity and utility for busy professionals.</p>
<p>With practical examples and executive-level framing, the book is accessible while keeping a modern, enterprise-grade tone.</p>
<h2>How the book is structured</h2>
<p>The book moves from the challenge of information overload through ambiguity, operational blind spots, and algorithmic pitfalls toward effective human tradecraft. It takes readers step by step from confusion to mastery.</p>
<p>Later chapters cover signal architecture, ethics, and emerging risks. Together they form a roadmap from algorithmic fog to actionable clarity for security leaders and decision makers.</p></section>
{f_about}
{cta("Buy the book", "Available from Amazon and major retailers. Bulk orders welcome.", btn(BUY, "Amazon / Retailers / Bulk Orders"))}""",
    [BOOK, PERSON, ORG, s_about], name="About the Book")

# ---------- INSIDE THE BOOK ----------
chapters = [("crPWAVfvizv4XQLxaFCnjdVp6xU.png", "The Overload Condition.", "Explores today's relentless information stream and how leaders can filter signals from noise in modern security."),
            ("wRIyeuS8kLyEpZYsWRph4ttC4I.png", "Weaponized Ambiguity.", "Discusses the dangers of intentional uncertainty and manipulation, and tactics to regain clarity and trust."),
            ("J7ehMP2Q6ilABUzDNNT8vuob9M.png", "Machine's Blind Spots.", "Examines where algorithms fail, why human oversight matters, and the limits of machine-driven analysis."),
            ("Wm6naNeeDwbTjVmrhraUdCF4I.png", "Tradecraft Reborn.", "Shows how classic tradecraft evolves in the age of AI and automated signals, blending human and machine expertise."),
            ("arjVbgxLwqQOudWlMPP3FoYzQ.png", "Behavioral Signatures.", "Unpacks the digital fingerprints left by behavior, and how they add detection layers in chaotic systems."),
            ("AJfvIPmowqUAeG5akRgXikpvosY.png", "Cognitive Countermeasures.", "Covers mental techniques and frameworks leaders can use to combat overload and deceptive signals.")]
toc = {"@type": "ItemList", "name": "Signals in the Noise: selected chapters", "itemListElement": [
    {"@type": "ListItem", "position": i + 1, "name": t.rstrip(".")} for i, (_, t, _) in enumerate(chapters)]}
PAGES["/inside-the-book"] = page("/inside-the-book", "Inside the Book | Chapters of Signals in the Noise",
    "Chapter guide to Signals in the Noise: The Overload Condition, Weaponized Ambiguity, Machine's Blind Spots, Tradecraft Reborn, Behavioral Signatures, and Cognitive Countermeasures.",
    f"""<section class="hero">
<img src="{FU}ZyKu4pY5nwPiDHdbK0lD0a55Ukw.jpeg" alt="Abstract signal visualization" width="1200" height="600" fetchpriority="high">
<h1>Explore the book.</h1>
<p class="lede">Six of the ideas at the center of <em>Signals in the Noise</em>.</p>
<div class="btns">{btn(BUY, "Get the Book")}</div></section>
<section><h2>Chapters</h2>{cards(chapters)}</section>
{cta("Ready to read it?", "Available from Amazon and major retailers.", btn(BUY, "Get the Book"))}""",
    [toc, BOOK], og_img="ZyKu4pY5nwPiDHdbK0lD0a55Ukw.jpeg", name="Inside the Book")

# ---------- BOARDS ----------
f_board, s_board = faq([
    ("What is the Board Edition of Signals in the Noise?", "An 8 to 12 page executive PDF that condenses the book for directors, with clarity frameworks and fast-read guides for governance decisions."),
    ("What questions should a board ask about AI risk?", "What information should be escalated to the board in real time, how the board verifies the quality of algorithmic controls, and whether escalation and communications are ready for synthetic risk events."),
    ("Does Tim Reed brief boards directly?", "Yes. Custom board briefings and executive offsites on risk, AI, and resilience can be scheduled through this site."),
])
PAGES["/boards-leaders"] = page("/boards-leaders", "Boards & Leaders | AI Risk Oversight and Board Briefings",
    "Board-level guidance on AI and algorithmic risk: the Signals in the Noise Board Edition, custom board briefings, executive offsites, and signal and risk architecture reviews.",
    f"""<section class="hero">
<img src="{FU}sBIG9QmZd1mtsowWu1ug6FpVs.jpeg" alt="Boardroom" width="1200" height="600" fetchpriority="high">
<h1>The board's new risk surface.</h1>
<p class="lede">Modern algorithms. New exposures.</p>
<div class="btns">{btn(CAL, "Schedule a Board Briefing")}</div></section>
<section><h2>Three questions every board should ask</h2>
{cards([("sBBsCvPWjdesJyucGMmzWZOtsSI.jpeg", "Accountability.", "What information should be escalated to the board in real time?"),
        ("tZlE1T5kAlc2JlHW1dEOa4d3Lg.jpeg", "AI oversight.", "How does the board verify the quality of algorithmic controls?"),
        ("ZyKu4pY5nwPiDHdbK0lD0a55Ukw.jpeg", "Incident playbooks.", "Are escalation and communications ready for synthetic risk events?")])}
</section>
<section class="prose"><h2>Board Edition overview</h2>
<p>The <em>Signals in the Noise</em> Board Edition delivers insights for directors in an 8 to 12 page, executive-level PDF. It equips oversight leaders with actionable analysis, clarity frameworks, and fast-read guides for real governance challenges.</p>
<p>Designed for board meetings, the PDF summarizes the core of the book for immediate use, from algorithmic risk to signal governance.</p>
<p>{btn(CAL, "Request the Board Edition")}</p></section>
<section><h2>Work with boards and leadership teams</h2>
{cards([("XOAj05CUZ5W6I1i0JqwtIJ3eDdg.jpeg", "Briefings.", "Custom board presentations on enterprise security and strategic governance."),
        ("zIC7g318ji0kYct7x0j5o2LKAMM.jpeg", "Offsites.", "Executive offsites on risk, AI, and organization-wide resilience."),
        ("HRznLIO1QqMG5HeT6giBaA8EYUo.jpeg", "Signal & risk architecture.", "Reviews that translate board obligations into monitoring, reporting, and escalation design. Move beyond compliance to resilience-driven oversight.")])}
</section>
{f_board}
{cta("Upgrade your oversight.", "Book a 30-minute conversation about your board's needs.", btn(CAL, "Schedule a Board Briefing"))}""",
    [{"@type": "Service", "name": "Board briefings on AI and security risk", "provider": {"@id": PERSON["@id"]},
      "areaServed": "Worldwide", "audience": {"@type": "Audience", "audienceType": "Boards of directors"}}, PERSON, s_board],
    og_img="sBIG9QmZd1mtsowWu1ug6FpVs.jpeg", name="Boards & Leaders")

# ---------- NEWSLETTER ----------
PAGES["/newsletter-podcast"] = page("/newsletter-podcast", "Newsletter & Podcast | The Northern Signal and The Ice Flow",
    "Subscribe to The Northern Signal, concise leadership briefings on AI, risk, and clarity, and listen to The Ice Flow Podcast, short intelligence episodes for boards and leaders.",
    f"""<section class="hero"><h1>Newsletter &amp; podcast.</h1>
<p class="lede">Ongoing briefings from the author of <em>Signals in the Noise</em>.</p></section>
<section>
{cards([("PYpSHMq8ECCtw8wxYhjUYwnQ6UM.png", "The Northern Signal.", "Concise leadership briefings on AI, risk, and clarity. Executive-level insights delivered to your inbox."),
        ("3fKjhadWKqmdbn2lXlbmrFqIhS8.png", "The Ice Flow Podcast.", "Short, sharp intelligence episodes for boards and leaders, with insights from security and AI experts.")], "h2")}
</section>
{cta("Join or listen.", "Subscribe to the newsletter or catch the latest episode.", btn(NEWS, "Join Newsletter") + btn(POD, "Listen to the Podcast", True))}""",
    [{"@type": "Periodical", "name": "The Northern Signal", "url": NEWS, "author": {"@id": PERSON["@id"]}},
     {"@type": "PodcastSeries", "name": "The Ice Flow Podcast", "url": POD, "author": {"@id": PERSON["@id"]}}],
    og_img="PYpSHMq8ECCtw8wxYhjUYwnQ6UM.png", name="Newsletter & Podcast")

# ---------- ADVISORY ----------
PAGES["/advisory"] = page("/advisory", "Advisory | Keynotes, Board Briefings, and AI Strategy Sessions",
    "Book Timothy E. Reed, CPP for board briefings, keynotes, AI strategy sessions, and signal workshops. Virtual, half-day, full-day, and multi-session formats.",
    f"""<section class="hero"><h1>Briefings, keynotes, and strategic advisory sessions.</h1>
<p class="lede">Custom sessions on AI, risk, and modern security for executives and boards.</p>
<div class="btns">{btn(CAL, "Request an Advisory Call")}</div></section>
<section>
{cards([("fhCIfZWRBqZ7HKt9055HjQbE3A.jpeg", "Board briefings.", "Targeted leadership and board sessions on AI, risk, and modern security."),
        ("f4Yl71QwBChN0wMZ1jtcHJVOU.jpeg", "AI strategy.", "Working sessions on AI risk, opportunity, and strategic governance."),
        ("1iWJNDfQnABy2K7waQxrXnQFwI.jpeg", "Signal workshops.", "Enterprise workshops on signal architecture and operational clarity in complex environments."),
        ("Tpwd0oysHmSfEO8VpgJldjx09UQ.jpeg", "Session formats.", "Virtual 60 to 90 minutes, half-day, full-day, and multi-session engagements."),
        ("i0hOEDWj9sHO9IMT7EUz5uvv8.jpeg", "Tailored delivery.", "Every session is built around your organization's executive and board needs.")])}
</section>
{cta("Request an advisory call", "Connect to discuss your leadership needs.", btn(CAL, "Book Now"))}""",
    [{"@type": "Service", "name": "Security and AI governance advisory", "provider": {"@id": PERSON["@id"]},
      "serviceType": ["Keynote speaking", "Board briefings", "AI strategy sessions", "Signal workshops"]}, PERSON],
    og_img="fhCIfZWRBqZ7HKt9055HjQbE3A.jpeg", name="Advisory")

# ---------- ISZ PRESS ----------
PAGES["/isz-press"] = page("/isz-press", "ISZ Press | Independent Imprint for Security and Risk Intelligence",
    "ISZ Press (Ice Station Zebra Press) publishes clarity-driven, executive-level books on security, risk, and AI, including the flagship title Signals in the Noise.",
    f"""<section class="hero"><h1>Ice Station Zebra Press</h1>
<p class="lede">Independent imprint for modern security and risk intelligence.</p>
<div class="btns">{btn(CAL, "Discuss a Project")}</div></section>
<section>
{cards([("UoH3CVfZcSfwqOvK67GLgBfc.jpeg", "Our purpose.", "ISZ Press publishes clarity-driven, executive-level books on security, risk, and AI for leaders, boards, and advisors."),
        ("g3e76Ea4xwdHo9pDxAw1FyCPM.jpeg", "Flagship title.", "Signals in the Noise is our flagship book, guiding decision makers through AI-driven risk with precision."),
        ("LfueiJOpGZ51tEStQlYA6HjQjc.jpeg", "Work with us.", "We collaborate with authors and organizations to create the next essential guide for leaders.")])}
</section>
{cta("Ready for a conversation?", "Bring your idea to the next chapter.", btn(CAL, "Discuss a Project"))}""",
    [ORG, BOOK], og_img="UoH3CVfZcSfwqOvK67GLgBfc.jpeg", name="ISZ Press")

# ---------- CONTACT ----------
PAGES["/contact"] = page("/contact", "Contact | Signals in the Noise and ISZ Press",
    "Contact ISZ Press about Signals in the Noise: speaking, board briefings, media, rights, and bulk orders. Email contact@iszpress.com or book a call.",
    f"""<section class="hero"><h1>Get in touch.</h1>
<p class="lede">For speaking, board, media, rights, or bulk order inquiries.</p></section>
<section class="prose">
<h2>How to reach us</h2>
<p>Email <a href="mailto:{EMAIL}">{EMAIL}</a> with your name, organization, topic, and message. For speaking and board briefings, the fastest route is a 30-minute call.</p>
<p>{btn(CAL, "Book a Call")} {btn("mailto:" + EMAIL, "Email Us", True)}</p>
</section>""",
    [{"@type": "ContactPage", "url": SITE + "/contact", "about": {"@id": ORG["@id"]}}, ORG], name="Contact")

# ---------- AUTHOR ----------
PAGES["/about-the-author"] = page("/about-the-author", "Timothy E. Reed, CPP | Author of Signals in the Noise",
    "Timothy E. Reed, CPP is a corporate security leader with 26+ years in physical security, intelligence, risk management, robotics, and AI, and the author of Signals in the Noise.",
    f"""<section class="hero split">
<img src="{FU}CRJLY02NNZkDawjIaEfeqhC6I.jpeg" alt="Timothy E. Reed, CPP" width="600" height="750" fetchpriority="high">
<div><p class="eyebrow">About the Author</p><h1>Timothy E. Reed, CPP</h1>
<p class="lede">Security strategist. Author. Advisor.</p>
<div class="btns">{btn(CAL, "Book Tim for a Briefing")}</div></div></section>
<section class="prose"><h2>About Tim Reed</h2>
<p>Tim Reed, CPP, is a global corporate security leader with more than 26 years of experience in physical security, intelligence, risk management, robotics, and AI. As Director of Security at Aurora, Tim shapes enterprise protection programs and leads innovation where risk and technology meet.</p>
<p>He advises boards, enterprises, and startups, and works with ISZ Press to advance the security field. An author, speaker, and strategist, Tim is sought after for executive briefings and guidance on the future of security.</p>
<p>He is the author of <a href="/about-the-book"><em>Signals in the Noise: Security, Technology, and the Hidden Patterns of Modern Risk</em></a> and writes <a href="{NEWS}" target="_blank" rel="noopener">The Northern Signal</a> newsletter.</p></section>""",
    [{**PERSON, "image": FU + "CRJLY02NNZkDawjIaEfeqhC6I.jpeg"}, {"@type": "ProfilePage", "mainEntity": {"@id": PERSON["@id"]}}, BOOK],
    og_img="CRJLY02NNZkDawjIaEfeqhC6I.jpeg", name="About the Author")

# ---------- PRIVACY ----------
PRIV = [
 ("Overview", ["This Privacy Policy explains how Ice Station Zebra, LLC (“Ice Station Zebra,” “we,” “us,” or “our”) collects, uses, and shares information when you visit www.signalsinthenoisebook.com (the “Site”). We publish a newsletter using beehiiv, and we use beehiiv’s analytics for newsletter performance."]),
 ("Information we collect", ["<strong>A. Information you provide.</strong> We collect information you choose to provide, such as newsletter subscription information (your email address and any optional fields), contact and inquiry information (your name, email address, and message contents), and business context you share voluntarily (organization name, project details, or requests for quotes).",
   "<strong>B. Information collected automatically.</strong> When you visit the Site, our hosting provider may collect log and device data, including IP address, browser type, device type, operating system, pages viewed, and approximate location derived from IP address.",
   "<strong>C. Newsletter analytics (beehiiv).</strong> When we send newsletters, beehiiv analytics may capture engagement signals such as email opens and link clicks. This commonly uses small embedded images, sometimes called tracking pixels or web beacons, which can transmit information such as time, date, and IP address when loaded."]),
 ("How we use information", ["We use information to operate, maintain, and secure the Site; provide the newsletter and manage subscriptions; respond to inquiries; understand performance and improve our content; detect, prevent, and investigate fraud, abuse, and security incidents; and comply with legal obligations."]),
 ("Newsletter communications (beehiiv)", ["If you subscribe to our newsletter, your subscription data is processed through beehiiv as our email service provider. You can opt out at any time using the unsubscribe link in any email. After you unsubscribe, we may retain limited information to honor your opt-out and maintain suppression lists."]),
 ("How we share information", ["We share information only as needed to run the Site and newsletter, including with hosting and infrastructure providers, which may process log data such as IP address and page views; beehiiv, for newsletter delivery and analytics; service providers that help us operate the Site and communications under appropriate confidentiality and security obligations; and government authorities or other parties when required by law or to protect rights, safety, and security.",
   "We do not sell personal information. We do not use your personal information for cross-context behavioral advertising. If that changes, we will update this policy and provide required choices and disclosures."]),
 ("Cookies and similar technologies", ["The Site does not set advertising cookies. Our hosting provider may keep standard server logs. Embedded third-party content, such as booking or podcast links, is governed by those providers’ policies. You can control cookies through your browser settings."]),
 ("Data retention", ["Newsletter data is retained until you unsubscribe, plus a reasonable period for suppression and compliance. Inquiry data is retained as long as necessary to respond and maintain business records. Log data is retained according to provider settings."]),
 ("Your privacy rights", ["Depending on where you live, you may have rights to access, correct, delete, or object to certain processing of your personal information. To submit a request, contact us using the information below. We will take reasonable steps to verify your request. If you are in the EEA or UK, you may also lodge a complaint with your local data protection authority."]),
 ("Children’s privacy", ["The Site and newsletter are not intended for children under 13. We do not knowingly collect personal information from children. If you believe a child has provided personal information, contact us and we will delete it."]),
 ("Security", ["We use reasonable administrative, technical, and organizational safeguards to protect information. No method of transmission or storage is completely secure."]),
 ("International visitors", ["If you access the Site from outside the United States, your information may be transferred to and processed in the United States or other jurisdictions where our service providers operate."]),
 ("Contact us", [f"Questions or requests: <a href=\"mailto:{EMAIL}\">{EMAIL}</a>."]),
]
priv_html = "".join(f"<h2>{i+1}. {h}</h2>" + "".join(f"<p>{p}</p>" for p in ps) for i, (h, ps) in enumerate(PRIV))
PAGES["/privacy-policy"] = page("/privacy-policy", "Privacy Policy | Signals in the Noise",
    "How Ice Station Zebra, LLC collects, uses, and protects information on signalsinthenoisebook.com and The Northern Signal newsletter.",
    f'<section class="prose"><h1>Privacy Policy</h1><p class="muted">Last updated: November 12, 2026</p>{priv_html}</section>', name="Privacy Policy")

# ---------- 404 ----------
PAGES["/404"] = page("/404", "Page not found | Signals in the Noise", "The page you requested does not exist.",
    f'<section class="hero"><h1>Page not found.</h1><p class="lede">That signal was noise.</p><div class="btns">{btn("/", "Go Home")}</div></section>', name="Not found")

# ---------- write ----------
BASE = os.environ.get("BASE", "")
shutil.rmtree(OUT, ignore_errors=True)
shutil.copytree(os.path.join(ROOT, "static"), OUT)
shutil.copytree(os.path.join(ROOT, "assets", "img"), os.path.join(OUT, "assets", "img"))
for path, doc in PAGES.items():
    doc = doc.replace('src="' + SITE + '/assets/img/', 'src="' + BASE + '/assets/img/')
    if BASE:
        doc = doc.replace('href="/', f'href="{BASE}/')
    fn = "index.html" if path == "/" else ("404.html" if path == "/404" else path.strip("/") + "/index.html")
    full = os.path.join(OUT, fn)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, "w").write(doc)

urls = [p for p in PAGES if p != "/404"]
open(os.path.join(OUT, "sitemap.xml"), "w").write(
    '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
    "".join(f"  <url><loc>{SITE}{'' if p=='/' else p}{'/' if p=='/' else ''}</loc><lastmod>2026-11-12</lastmod></url>\n" for p in urls) + "</urlset>\n")
open(os.path.join(OUT, "robots.txt"), "w").write(
    "# Search engines and AI assistants are welcome.\nUser-agent: *\nAllow: /\n\n"
    + "".join(f"User-agent: {b}\nAllow: /\n\n" for b in ["GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-User", "Claude-SearchBot", "PerplexityBot", "Google-Extended", "Applebot-Extended", "Bingbot"])
    + f"Sitemap: {SITE}/sitemap.xml\n")
if not BASE:
    open(os.path.join(OUT, "CNAME"), "w").write("www.signalsinthenoisebook.com\n")
elif os.path.exists(os.path.join(OUT, "CNAME")):
    os.remove(os.path.join(OUT, "CNAME"))
print("built", len(PAGES), "pages ->", os.path.abspath(OUT))
