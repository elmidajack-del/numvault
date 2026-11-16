export async function onRequestPost({ request, env }) {
  try {
    const url = new URL(request.url);
    const num = parseInt(url.searchParams.get("n"), 10);

    if (!num || num < 1) {
      return new Response(JSON.stringify({ error: "Invalid number" }), { status: 400 });
    }

    const key = `views_${num}`;
    const current = parseInt((await env.FACTS_KV.get(key)) || "0", 10);
    const updated = current + 1;

    await env.FACTS_KV.put(key, String(updated));

    return new Response(JSON.stringify({ views: updated }), {
      headers: { "Content-Type": "application/json" }
    });
  } catch (err) {
    return new Response(JSON.stringify({ error: "Server error" }), { status: 500 });
  }
}