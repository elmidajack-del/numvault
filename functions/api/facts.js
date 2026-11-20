export async function onRequestGet({ request, env }) {
  const url = new URL(request.url);
  const num = (url.searchParams.get("n") || "").trim();

  if (!/^[1-9][0-9]*$/.test(num)) {
    return new Response(JSON.stringify([]), {
      headers: { "Content-Type": "application/json" }
    });
  }

  const stored = await env.FACTS_KV.get(`num_${num}`);
  return new Response(stored || "[]", {
    headers: { "Content-Type": "application/json" }
  });
}

export async function onRequestPost({ request, env }) {
  try {
    const body = await request.json();
    const num = String(body.number || "").trim();
    const fact = (body.fact || "").trim();
    const submitter = (body.submitter || "").trim();

    if (!/^[1-9][0-9]*$/.test(num) || !fact) {
      return new Response(JSON.stringify({ error: "Invalid input" }), { status: 400 });
    }

    const entry = {
      text: fact,
      submitter: submitter || null,
      createdAt: new Date().toISOString()
    };

    // 1. Save to the specific number's fact list
    const key = `num_${num}`;
    const existingRaw = await env.FACTS_KV.get(key);
    const existing = existingRaw ? JSON.parse(existingRaw) : [];
    existing.unshift(entry);
    await env.FACTS_KV.put(key, JSON.stringify(existing));

    // 2. Append to global recent_facts feed (capped at 25 latest entries)
    const recentKey = "recent_facts";
    const recentRaw = await env.FACTS_KV.get(recentKey);
    const recentList = recentRaw ? JSON.parse(recentRaw) : [];
    recentList.unshift({
      number: num,
      text: entry.text,
      submitter: entry.submitter,
      createdAt: entry.createdAt
    });
    if (recentList.length > 25) {
      recentList.length = 25;
    }
    await env.FACTS_KV.put(recentKey, JSON.stringify(recentList));

    return new Response(JSON.stringify({ success: true, entry, facts: existing }), {
      headers: { "Content-Type": "application/json" }
    });
  } catch (err) {
    return new Response(JSON.stringify({ error: "Server error" }), { status: 500 });
  }
}