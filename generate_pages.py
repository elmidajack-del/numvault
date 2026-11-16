import os
import math

# --- CONFIGURATION ---
START_NUM = 1
END_NUM = 1000
OUTPUT_DIR = "numbers"
DOMAIN_URL = "https://numvault.pages.dev"  # Update to your live domain

# --- CUSTOM FACTS TEMPLATE DICTIONARY ---
CUSTOM_FACTS = {
    1: [
        "The multiplicative identity for integers, real numbers, and complex numbers.",
        "The first Fibonacci number (and the second), triangular number, and square/cube number.",
        "The only positive integer with exactly one positive divisor."
    ],
    2: [
        "The smallest prime number and the only even prime.",
        "The base of the binary numeral system used across modern computing.",
        "The first Sophie Germain prime (since 2 × 2 + 1 = 5 is also prime)."
    ],
    42: [
        "The 'Answer to the Ultimate Question of Life, the Universe, and Everything' in Douglas Adams' Hitchhiker's Guide.",
        "The fifth Catalan number and a pronic number (6 × 7)."
    ]
}

def get_divisors(n: int) -> list[int]:
    small, large = [], []
    for i in range(1, math.isqrt(n) + 1):
        if n % i == 0:
            small.append(i)
            if i != n // i:
                large.append(n // i)
    return small + large[::-1]

def prime_factorization(n: int) -> list[tuple[int, int]]:
    if n <= 1:
        return []
    factors = []
    temp = n
    count = 0
    while temp % 2 == 0:
        count += 1
        temp //= 2
    if count > 0:
        factors.append((2, count))
        
    d = 3
    max_d = math.isqrt(temp)
    while d <= max_d:
        count = 0
        while temp % d == 0:
            count += 1
            temp //= d
        if count > 0:
            factors.append((d, count))
            max_d = math.isqrt(temp)
        d += 2
        
    if temp > 1:
        factors.append((temp, 1))
    return factors

def format_factorization_html(factors: list[tuple[int, int]]) -> str:
    if not factors:
        return "<code>1</code> (Empty product)"
    parts = []
    for base, exp in factors:
        if exp == 1:
            parts.append(f"{base}")
        else:
            parts.append(f"{base}<sup>{exp}</sup>")
    return f"<code>{' &times; '.join(parts)}</code>"

def get_classification(n: int, factors: list[tuple[int, int]]) -> tuple[str, str, str]:
    if n == 1:
        return "Unit (Neither Prime nor Composite)", "#262c38", "#4f8cff"
    if len(factors) == 1 and factors[0][1] == 1:
        return "Prime", "#1e3329", "#4ade80"
    total_prime_factors = sum(exp for _, exp in factors)
    if total_prime_factors == 2:
        return "Composite (Semiprime)", "#33261e", "#fb923c"
    return "Composite", "#33261e", "#fb923c"

def to_base(n: int, base: int) -> str:
    digits = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    if n == 0:
        return "0"
    res = []
    while n > 0:
        res.append(digits[n % base])
        n //= base
    return "".join(reversed(res))

def get_facts_for_number(n: int, divisors: list[int]) -> list[str]:
    if n in CUSTOM_FACTS:
        return CUSTOM_FACTS[n]
    
    facts = []
    if math.isqrt(n) ** 2 == n and n > 1:
        facts.append(f"{n:,} is a perfect square ({math.isqrt(n):,}²).")
    
    proper_div_sum = sum(divisors[:-1])
    if proper_div_sum == n and n > 1:
        facts.append(f"{n:,} is a perfect number (equal to the sum of its proper divisors).")
    elif proper_div_sum > n:
        facts.append(f"{n:,} is an abundant number.")
    elif n > 1:
        facts.append(f"{n:,} is a deficient number.")
        
    if not facts:
        facts.append(f"A positive integer with {len(divisors):,} total divisors.")
    return facts

def render_site_shell(title: str, description: str, body_content: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} — NumVault</title>
  <meta name="description" content="{description}">
  <meta name="robots" content="index, follow">
  <style>
    :root {{ 
      --bg: #0f1115; --card: #181b21; --border: #2a2f3a; 
      --text: #e6e8ec; --muted: #9aa0aa; --accent: #4f8cff; 
    }}
    * {{ box-sizing: border-box; }}
    body {{ 
      font-family: system-ui, -apple-system, sans-serif; 
      background: var(--bg); color: var(--text); 
      margin: 0; padding: 2rem 1rem; line-height: 1.6; 
    }}
    .container {{ max-width: 780px; margin: 0 auto; }}
    header.site-header {{ 
      display: flex; justify-content: space-between; align-items: center; 
      margin-bottom: 2rem; padding-bottom: 1rem; border-bottom: 1px solid var(--border); 
    }}
    header.site-header a {{ color: var(--text); text-decoration: none; font-weight: 600; font-size: 1.1rem; }}
    header.site-header a:hover {{ color: var(--accent); }}
    footer.site-footer {{ 
      text-align: center; margin-top: 3rem; font-size: 0.85rem; color: var(--muted); 
      border-top: 1px solid var(--border); padding-top: 1.5rem; display: flex; justify-content: space-between; align-items: center;
    }}
    .card {{ background: var(--card); border: 1px solid var(--border); border-radius: 8px; padding: 1.5rem; margin-bottom: 1rem; }}
    h1 {{ margin: 0 0 0.25rem 0; font-size: 2.5rem; font-variant-numeric: tabular-nums; }}
    .badge {{ display: inline-block; padding: 0.2rem 0.6rem; border-radius: 4px; font-size: 0.85rem; font-weight: 600; }}
    table {{ width: 100%; border-collapse: collapse; margin-top: 0.5rem; }}
    td {{ padding: 0.5rem 0; border-bottom: 1px solid var(--border); vertical-align: top; }}
    td:first-child {{ color: var(--muted); width: 35%; }}
    code {{ font-family: ui-monospace, monospace; background: #111318; padding: 0.15rem 0.4rem; border-radius: 4px; word-break: break-all; }}
    select, input {{ background: #111318; color: var(--text); border: 1px solid var(--border); padding: 0.4rem 0.8rem; border-radius: 4px; font-size: 0.95rem; width: 100%; }}
    input:focus, select:focus {{ outline: 2px solid var(--accent); border-color: transparent; }}
    .nav-links {{ display: flex; justify-content: space-between; margin-bottom: 1.5rem; font-size: 0.9rem; }}
    .nav-links a {{ color: var(--accent); text-decoration: none; }}
    .btn {{ background: var(--accent); color: #fff; border: none; padding: 0.4rem 1rem; border-radius: 4px; font-weight: 600; cursor: pointer; width: auto; }}
    .btn:hover {{ opacity: 0.9; }}
    ul li {{ margin-bottom: 0.5rem; }}
  </style>
</head>
<body>
  <div class="container">
    <header class="site-header">
      <a href="../index.html">NumVault 🗄️</a>
      <span style="color: var(--muted); font-size: 0.9rem;">Pure Integer Catalog</span>
    </header>

    {body_content}

    <footer class="site-footer">
      <span>NumVault &copy; 2026</span>
      <span id="visit-counter" style="color: var(--accent); font-weight: 500;">Views: Loading...</span>
    </footer>
  </div>

  <script>
    async function trackVisits() {{
      const slug = window.location.pathname.split("/").filter(Boolean).pop().replace(".html", "");
      const counterEl = document.getElementById("visit-counter");
      try {{
        const response = await fetch(`https://api.countapi.xyz/hit/numvault_catalog/${{slug}}`);
        if (response.ok) {{
          const data = await response.json();
          counterEl.textContent = `👁️ Views: ${{data.value.toLocaleString()}}`;
          return;
        }}
      }} catch (e) {{}}
      
      const key = `numvault_views_${{slug}}`;
      let views = parseInt(localStorage.getItem(key) || "0") + 1;
      localStorage.setItem(key, views);
      counterEl.textContent = `👁️ Views: ${{views.toLocaleString()}} (Local)`;
    }}
    trackVisits();
  </script>
</body>
</html>
"""

def build_number_page(n: int, start: int, end: int) -> str:
    divisors = get_divisors(n)
    factors = prime_factorization(n)
    badge_text, badge_bg, badge_color = get_classification(n, factors)
    facts = get_facts_for_number(n, divisors)
    
    prev_link = f'<a href="{n-1}.html">&larr; {n-1:,}</a>' if n > start else '<span>&larr; Prev</span>'
    next_link = f'<a href="{n+1}.html">{n+1:,} &rarr;</a>' if n < end else '<span>Next &rarr;</span>'
    
    divisors_display = divisors[:100] if len(divisors) > 100 else divisors
    divisors_str = ", ".join(map(str, divisors_display))
    if len(divisors) > 100:
        divisors_str += f" ... (showing 100 of {len(divisors):,} total divisors)"

    base_map_js = ", ".join(f'{b}: "{to_base(n, b)}"' for b in range(2, 37))
    facts_html = "".join(f"<li>{fact}</li>" for fact in facts)
    description = f"Explore number {n:,}: prime factorization, {len(divisors):,} divisors, base representations, and mathematical properties on NumVault."

    content = f"""
    <div class="nav-links">
      {prev_link}
      <a href="../index.html">Index</a>
      {next_link}
    </div>

    <div class="card">
      <h1>{n:,}</h1>
      <span class="badge" style="background: {badge_bg}; color: {badge_color};">{badge_text}</span>
    </div>

    <div class="card">
      <h2>Properties &amp; Factorization</h2>
      <table>
        <tr><td>Prime Factorization</td><td>{format_factorization_html(factors)}</td></tr>
        <tr><td>Divisors</td><td><code>{divisors_str}</code></td></tr>
        <tr><td>Divisor Count &tau;(n)</td><td>{len(divisors):,}</td></tr>
        <tr><td>Divisor Sum &sigma;(n)</td><td>{sum(divisors):,}</td></tr>
        <tr><td>Parity</td><td>{"Even" if n % 2 == 0 else "Odd"}</td></tr>
      </table>
    </div>

    <div class="card">
      <h2>Base Representations</h2>
      <table>
        <tr><td>Binary (Base 2)</td><td><code>{to_base(n, 2)}</code></td></tr>
        <tr><td>Octal (Base 8)</td><td><code>{to_base(n, 8)}</code></td></tr>
        <tr><td>Hexadecimal (Base 16)</td><td><code>{to_base(n, 16)}</code></td></tr>
        <tr><td>Base 36</td><td><code>{to_base(n, 36)}</code></td></tr>
        <tr>
          <td>
            <label for="base-select">Custom Base (2–36):</label>
            <select id="base-select" onchange="updateBase()">
              {"".join(f'<option value="{b}" {"selected" if b == 12 else ""}>Base {b}</option>' for b in range(2, 37))}
            </select>
          </td>
          <td><code id="custom-base-val">{to_base(n, 12)}</code></td>
        </tr>
      </table>
    </div>

    <div class="card">
      <h2>Notable Facts &amp; Properties</h2>
      <ul>
        {facts_html}
      </ul>
    </div>

    <script>
      const bases = {{{base_map_js}}};
      function updateBase() {{
        const b = document.getElementById('base-select').value;
        document.getElementById('custom-base-val').textContent = bases[b];
      }}
    </script>
    """
    return render_site_shell(f"Number {n:,}", description, content)

def build_index_page(start: int, end: int) -> str:
    content = f"""
    <div class="card" style="text-align: center; padding: 2rem;">
      <h2 style="margin-top: 0;">Search &amp; Jump to Integer</h2>
      <p style="color: var(--muted); margin-bottom: 1.5rem;">Enter any integer between {start:,} and {end:,} to view its public record:</p>
      <form onsubmit="jumpToNumber(event)" style="display: flex; gap: 0.5rem; justify-content: center; max-width: 400px; margin: 0 auto;">
        <input type="number" id="jump-input" min="{start}" max="{end}" placeholder="e.g. 42" required />
        <button type="submit" class="btn">Search</button>
      </form>
    </div>

    <div class="card">
      <h2>Quick Catalog Directory</h2>
      <p style="color: var(--muted); font-size: 0.9rem;">Quick links to numbers {start:,} through {end:,}:</p>
      <ul style="display: grid; grid-template-columns: repeat(auto-fill, minmax(80px, 1fr)); gap: 0.5rem; list-style: none; padding: 0; margin-top: 1rem;">
        {"".join(f'<li><a href="numbers/{n}.html" style="display: block; background: #111318; border: 1px solid var(--border); padding: 0.5rem; text-align: center; border-radius: 4px; color: var(--accent); text-decoration: none;">{n:,}</a></li>' for n in range(start, min(start + 300, end + 1)))}
      </ul>
    </div>

    <script>
      function jumpToNumber(e) {{
        e.preventDefault();
        const num = document.getElementById('jump-input').value;
        if (num) {{
          window.location.href = 'numbers/' + num + '.html';
        }}
      }}
    </script>
    """
    
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>NumVault — Public Integer Catalog</title>
  <meta name="description" content="Explore pure positive integers, prime factorizations, divisors, and base representations on NumVault.">
  <meta name="robots" content="index, follow">
  <style>
    :root {{ --bg: #0f1115; --card: #181b21; --border: #2a2f3a; --text: #e6e8ec; --muted: #9aa0aa; --accent: #4f8cff; }}
    body {{ font-family: system-ui, sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 2rem 1rem; line-height: 1.6; }}
    .container {{ max-width: 780px; margin: 0 auto; }}
    .card {{ background: var(--card); border: 1px solid var(--border); border-radius: 8px; padding: 1.5rem; margin-bottom: 1rem; }}
    input, button {{ background: #111318; color: var(--text); border: 1px solid var(--border); padding: 0.4rem 0.8rem; border-radius: 4px; font-size: 0.95rem; width: 100%; }}
    .btn {{ background: var(--accent); color: #fff; border: none; font-weight: 600; cursor: pointer; width: auto; }}
  </style>
</head>
<body>
  <div class="container">
    <header style="margin-bottom: 2rem; border-bottom: 1px solid var(--border); padding-bottom: 1rem;">
      <h1>NumVault 🗄️</h1>
      <span style="color: var(--muted);">Public Integer Catalog &amp; Number Theory Engine</span>
    </header>
    {content}
  </div>
</body>
</html>
"""

def generate_sitemap(start: int, end: int) -> str:
    """Generates an XML sitemap for search engines (Google, Bing) to index every page."""
    urls = []
    urls.append(f"<url><loc>{DOMAIN_URL}/index.html</loc><priority>1.0</priority></url>")
    for n in range(start, end + 1):
        urls.append(f"<url><loc>{DOMAIN_URL}/numbers/{n}.html</loc><priority>0.8</priority></url>")
    
    urlset = "".join(urls)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urlset}\n</urlset>'

def main():
    nums_dir = OUTPUT_DIR
    os.makedirs(nums_dir, exist_ok=True)
    
    for n in range(START_NUM, END_NUM + 1):
        filepath = os.path.join(nums_dir, f"{n}.html")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(build_number_page(n, START_NUM, END_NUM))
            
    # Generate index.html
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(build_index_page(START_NUM, END_NUM))
        
    # Generate sitemap.xml for public search indexing
    with open("sitemap.xml", "w", encoding="utf-8") as f:
        f.write(generate_sitemap(START_NUM, END_NUM))
        
    print(f"Generated public site with sitemap.xml and search box for range {START_NUM:,} to {END_NUM:,}!")

if __name__ == "__main__":
    main()