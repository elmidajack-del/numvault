export async function onRequestGet({ request, env }) {
  const url = new URL(request.url);
  const num = url.searchParams.get("n");
  
  if (!num) {
    return new Response(JSON.stringify([]), { 
      headers: { "Content-Type": "application/json" } 
    });
  }

  // Fetch existing facts array from Cloudflare KV
  const stored = await env.FACTS_KV.get(`num_${num}`);
  return new Response(stored || "[]", {
    headers: { "Content-Type": "application/json" }
  });
}

export async function onRequestPost({ request, env }) {
  try {
    const body = await request.json();
    const num = parseInt(body.number, 10);
    const fact = (body.fact || "").trim();
    const submitter = (body.submitter || "").trim();

    if (!num || num < 1 || !fact) {
      return new Response(JSON.stringify({ error: "Invalid input" }), { status: 400 });
    }

    const formattedFact = submitter ? `${fact} — ${submitter}` : fact;
    const key = `num_${num}`;

    // Read current facts, append new one, and save back to KV
    const existingRaw = await env.FACTS_KV.get(key);
    const existing = existingRaw ? JSON.parse(existingRaw) : [];
    existing.unshift(formattedFact);

    await env.FACTS_KV.put(key, JSON.stringify(existing));

    return new Response(JSON.stringify({ success: true, facts: existing }), {
      headers: { "Content-Type": "application/json" }
    });
  } catch (err) {
    return new Response(JSON.stringify({ error: "Server error" }), { status: 500 });
  }
}