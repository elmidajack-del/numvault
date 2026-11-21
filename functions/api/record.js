export async function onRequestPost({ request, env }) {
  try {
    if (!env.FACTS_KV) {
      return new Response(JSON.stringify({ error: "FACTS_KV binding missing" }), {
        status: 500,
        headers: { "Content-Type": "application/json" }
      });
    }

    const url = new URL(request.url);
    const raw = (url.searchParams.get("n") || "").trim();

    if (!/^[1-9][0-9]*$/.test(raw)) {
      return new Response(JSON.stringify({ error: "Invalid integer" }), {
        status: 400,
        headers: { "Content-Type": "application/json" }
      });
    }

    const [rawViews, rawFacts, rawProps, rawIndex, rawTop] = await Promise.all([
      env.FACTS_KV.get(`views_${raw}`),
      env.FACTS_KV.get(`num_${raw}`),
      env.FACTS_KV.get(`props_${raw}`),
      env.FACTS_KV.get("catalog_index"),
      env.FACTS_KV.get("top_viewed")
    ]);

    const updatedViews = parseInt(rawViews || "0", 10) + 1;
    const writes = [env.FACTS_KV.put(`views_${raw}`, String(updatedViews))];

    const indexList = rawIndex ? JSON.parse(rawIndex) : [];
    if (!indexList.includes(raw)) {
      indexList.push(raw);
      indexList.sort((a, b) => (BigInt(a) < BigInt(b) ? -1 : BigInt(a) > BigInt(b) ? 1 : 0));
      writes.push(env.FACTS_KV.put("catalog_index", JSON.stringify(indexList)));
    }

    const topList = rawTop ? JSON.parse(rawTop) : [];
    const idx = topList.findIndex(item => item.number === raw);
    if (idx !== -1) topList[idx].views = updatedViews;
    else topList.push({ number: raw, views: updatedViews });

    topList.sort((a, b) =>
      b.views !== a.views ? b.views - a.views : BigInt(a.number) < BigInt(b.number) ? -1 : 1
    );
    if (topList.length > 25) topList.length = 25;
    writes.push(env.FACTS_KV.put("top_viewed", JSON.stringify(topList)));

    await Promise.all(writes);

    return new Response(JSON.stringify({
      views: updatedViews,
      facts: rawFacts ? JSON.parse(rawFacts) : [],
      props: rawProps ? JSON.parse(rawProps) : null
    }), {
      headers: { "Content-Type": "application/json" }
    });
  } catch (err) {
    return new Response(JSON.stringify({ error: "Server error" }), {
      status: 500,
      headers: { "Content-Type": "application/json" }
    });
  }
}