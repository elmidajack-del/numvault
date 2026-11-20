export async function onRequestGet({ request, env }) {
  const url = new URL(request.url);
  const num = (url.searchParams.get("n") || "").trim();

  if (!/^[1-9][0-9]*$/.test(num)) {
    return new Response(JSON.stringify(null), {
      headers: { "Content-Type": "application/json" }
    });
  }

  const cached = await env.FACTS_KV.get(`props_${num}`);
  return new Response(cached || "null", {
    headers: { "Content-Type": "application/json" }
  });
}

export async function onRequestPost({ request, env }) {
  try {
    const body = await request.json();
    const num = String(body.number || "").trim();
    const props = body.props;

    if (!/^[1-9][0-9]*$/.test(num) || !props || typeof props !== "object") {
      return new Response(JSON.stringify({ error: "Invalid payload" }), { status: 400 });
    }

    const key = `props_${num}`;
    // Only write if not already cached (immutable mathematical properties)
    const existing = await env.FACTS_KV.get(key);
    if (!existing) {
      await env.FACTS_KV.put(key, JSON.stringify(props));
    }

    return new Response(JSON.stringify({ success: true }), {
      headers: { "Content-Type": "application/json" }
    });
  } catch (err) {
    return new Response(JSON.stringify({ error: "Server error" }), { status: 500 });
  }
}