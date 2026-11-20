function modPow(base, exp, mod) {
  let result = 1n;
  base %= mod;
  while (exp > 0n) {
    if (exp & 1n) result = (result * base) % mod;
    exp >>= 1n;
    base = (base * base) % mod;
  }
  return result;
}

function isProbablePrime(n) {
  if (n < 2n) return false;
  if (n === 2n || n === 3n || n === 5n) return true;
  if (n % 2n === 0n || n % 3n === 0n || n % 5n === 0n) return false;
  const smallPrimes = [7n, 11n, 13n, 17n, 19n, 23n, 29n, 31n, 37n, 41n, 43n, 47n];
  for (const p of smallPrimes) {
    if (n === p) return true;
    if (n % p === 0n) return false;
  }
  let d = n - 1n, r = 0n;
  while ((d & 1n) === 0n) { d >>= 1n; r++; }
  const witnesses = [2n, 3n, 5n, 7n, 11n, 13n, 17n, 19n, 23n, 29n, 31n, 37n];
  for (const a of witnesses) {
    if (a >= n) break;
    let x = modPow(a, d, n);
    if (x === 1n || x === n - 1n) continue;
    let comp = true;
    for (let i = 1n; i < r; i++) {
      x = (x * x) % n;
      if (x === n - 1n) { comp = false; break; }
    }
    if (comp) return false;
  }
  return true;
}

function iRoot(n, k) {
  if (n < 2n) return n;
  const bitLen = BigInt(n.toString(2).length);
  let low = 1n << ((bitLen - 1n) / BigInt(k));
  let high = (1n << ((bitLen + BigInt(k) - 1n) / BigInt(k))) + 1n;
  while (low <= high) {
    const mid = (low + high) >> 1n;
    const p = mid ** BigInt(k);
    if (p === n) return mid;
    if (p < n) low = mid + 1n;
    else high = mid - 1n;
  }
  return high;
}

function isPerfectSquare(n) {
  if (n < 0n) return false;
  const r = iRoot(n, 2);
  return r * r === n;
}

function isPerfectPower(n) {
  if (n < 4n) return false;
  const maxExp = n.toString(2).length;
  for (let b = 2; b <= maxExp; b++) {
    const a = iRoot(n, b);
    if (a >= 2n && (a ** BigInt(b)) === n) return true;
  }
  return false;
}

function matchesMathClass(rawStr, mathClass) {
  if (mathClass === "any") return true;
  const n = BigInt(rawStr);
  if (mathClass === "prime") return isProbablePrime(n);
  if (mathClass === "mersenne") {
    const plusOne = n + 1n;
    return n >= 3n && ((plusOne & (plusOne - 1n)) === 0n);
  }
  if (mathClass === "fibonacci") {
    const fiveNSq = 5n * n * n;
    return isPerfectSquare(fiveNSq + 4n) || isPerfectSquare(fiveNSq - 4n);
  }
  if (mathClass === "power") return isPerfectPower(n);
  return true;
}

export async function onRequestGet({ request, env }) {
  try {
    const url = new URL(request.url);
    const page = Math.max(1, parseInt(url.searchParams.get("page") || "1", 10));
    const limit = Math.min(250, Math.max(10, parseInt(url.searchParams.get("limit") || "100", 10)));
    const group = url.searchParams.get("group") || "all";
    const mathClass = url.searchParams.get("class") || "any";

    const [rawIndex, rawTop, rawRecent] = await Promise.all([
      env.FACTS_KV.get("catalog_index"),
      env.FACTS_KV.get("top_viewed"),
      env.FACTS_KV.get("recent_facts")
    ]);

    const communityList = rawIndex ? JSON.parse(rawIndex) : [];
    const communitySet = new Set(communityList);

    const mergedSet = new Set(communityList);
    for (let i = 1; i <= 100; i++) mergedSet.add(String(i));

    const allSorted = Array.from(mergedSet).sort((a, b) => {
      const ba = BigInt(a), bb = BigInt(b);
      return ba < bb ? -1 : ba > bb ? 1 : 0;
    });

    const counts = {
      all: allSorted.length,
      small: 0,
      medium: 0,
      large: 0,
      huge: 0,
      community: communityList.length
    };

    const filtered = [];
    for (const n of allSorted) {
      const len = n.length;
      if (len <= 3) counts.small++;
      else if (len <= 10) counts.medium++;
      else if (len <= 30) counts.large++;
      else counts.huge++;

      const matchGroup =
        group === "all" ||
        (group === "small" && len <= 3) ||
        (group === "medium" && len >= 4 && len <= 10) ||
        (group === "large" && len >= 11 && len <= 30) ||
        (group === "huge" && len >= 31) ||
        (group === "community" && communitySet.has(n));

      if (matchGroup && matchesMathClass(n, mathClass)) {
        filtered.push(n);
      }
    }

    const totalPages = Math.max(1, Math.ceil(filtered.length / limit));
    const safePage = Math.min(page, totalPages);
    const start = (safePage - 1) * limit;
    const items = filtered.slice(start, start + limit).map(n => ({
      n,
      c: communitySet.has(n) ? 1 : 0
    }));

    return new Response(JSON.stringify({
      items,
      counts,
      page: safePage,
      totalPages,
      totalFiltered: filtered.length,
      topViewed: rawTop ? JSON.parse(rawTop).slice(0, 10) : [],
      recentFacts: rawRecent ? JSON.parse(rawRecent).slice(0, 10) : []
    }), {
      headers: {
        "Content-Type": "application/json",
        "Cache-Control": "public, max-age=30"
      }
    });
  } catch (err) {
    return new Response(JSON.stringify({ error: "Server error" }), { status: 500 });
  }
}