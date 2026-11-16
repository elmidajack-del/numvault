export async function onRequestPost({ request, env }) {
  try {
    const url = new URL(request.url);
    const raw = (url.searchParams.get("n") || "").trim();

    // Validate arbitrary-length positive integer string (no leading zeros)
    if (!/^[1-9][0-9]*$/.test(raw)) {
      return new Response(JSON.stringify({ error: "Invalid positive integer" }), { status: 400 });
    }

    // 1. Increment view count
    const viewKey = `views_${raw}`;
    const current = parseInt((await env.FACTS_KV.get(viewKey)) || "0", 10);
    const updated = current + 1;
    await env.FACTS_KV.put(viewKey, String(updated));

    // 2. Register in global requested index (deduplicated)
    const indexKey = "catalog_index";
    const rawIndex = await env.FACTS_KV.get(indexKey);
    const indexList = rawIndex ? JSON.parse(rawIndex) : [];

    if (!indexList.includes(raw)) {
      indexList.push(raw);
      // Sort numerically using BigInt comparison so huge numbers order accurately
      indexList.sort((a, b) => (BigInt(a) < BigInt(b) ? -1 : BigInt(a) > BigInt(b) ? 1 : 0));
      await env.FACTS_KV.put(indexKey, JSON.stringify(indexList));
    }

    return new Response(JSON.stringify({ views: updated }), {
      headers: { "Content-Type": "application/json" }
    });
  } catch (err) {
    return new Response(JSON.stringify({ error: "Server error" }), { status: 500 });
  }
}