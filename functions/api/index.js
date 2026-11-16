export async function onRequestGet({ env }) {
  try {
    const rawIndex = await env.FACTS_KV.get("catalog_index");
    const indexList = rawIndex ? JSON.parse(rawIndex) : [];
    return new Response(JSON.stringify(indexList), {
      headers: { "Content-Type": "application/json" }
    });
  } catch (err) {
    return new Response(JSON.stringify([]), {
      headers: { "Content-Type": "application/json" }
    });
  }
}