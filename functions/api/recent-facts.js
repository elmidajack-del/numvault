export async function onRequestGet({ env }) {
  try {
    const raw = await env.FACTS_KV.get("recent_facts");
    const list = raw ? JSON.parse(raw) : [];
    return new Response(JSON.stringify(list), {
      headers: { "Content-Type": "application/json" }
    });
  } catch (err) {
    return new Response(JSON.stringify([]), {
      headers: { "Content-Type": "application/json" }
    });
  }
}