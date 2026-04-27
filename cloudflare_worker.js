/**
 * Cloudflare Worker — OAuth proxy cho FB Auto Post Tool
 *
 * Mục đích:
 * - Giấu FB_APP_SECRET khỏi tool desktop (an toàn khi ship .exe cho khách)
 * - Tool gửi {code, redirect_uri} → Worker exchange → trả về long-lived token
 *
 * Deploy:
 * 1. Tạo account Cloudflare (free): https://dash.cloudflare.com/sign-up
 * 2. Vào Workers & Pages → Create → Worker → Copy code này paste vào
 * 3. Settings → Variables → thêm secret:
 *      - FB_APP_ID = 809805552199715
 *      - FB_APP_SECRET = abc123... (từ FB Dashboard)
 * 4. Save & Deploy → URL dạng https://xxx.workers.dev
 * 5. Copy URL paste vào .env của tool: OAUTH_BACKEND_URL=https://xxx.workers.dev
 *
 * Free tier: 100K request/ngày — đủ cho hàng nghìn user.
 */

export default {
  async fetch(request, env, ctx) {
    if (request.method === "OPTIONS") {
      return new Response(null, { headers: corsHeaders() });
    }
    if (request.method !== "POST") {
      return jsonResponse({ error: "Only POST allowed" }, 405);
    }

    let body;
    try {
      body = await request.json();
    } catch {
      return jsonResponse({ error: "Invalid JSON body" }, 400);
    }

    const code = body.code;
    const redirectUri = body.redirect_uri;
    if (!code || !redirectUri) {
      return jsonResponse({ error: "Missing code or redirect_uri" }, 400);
    }

    if (!env.FB_APP_ID || !env.FB_APP_SECRET) {
      return jsonResponse({ error: "Worker chưa cấu hình FB_APP_ID / FB_APP_SECRET" }, 500);
    }

    try {
      // Step 1: code → short-lived user token
      const exchangeUrl = new URL("https://graph.facebook.com/v19.0/oauth/access_token");
      exchangeUrl.searchParams.set("client_id", env.FB_APP_ID);
      exchangeUrl.searchParams.set("client_secret", env.FB_APP_SECRET);
      exchangeUrl.searchParams.set("redirect_uri", redirectUri);
      exchangeUrl.searchParams.set("code", code);

      const exRes = await fetch(exchangeUrl.toString());
      const exData = await exRes.json();
      if (!exRes.ok || !exData.access_token) {
        return jsonResponse({
          error: `Exchange failed: ${exData.error?.message || JSON.stringify(exData)}`,
        }, 400);
      }
      const shortToken = exData.access_token;

      // Step 2: short → long-lived (60 ngày)
      const longUrl = new URL("https://graph.facebook.com/v19.0/oauth/access_token");
      longUrl.searchParams.set("grant_type", "fb_exchange_token");
      longUrl.searchParams.set("client_id", env.FB_APP_ID);
      longUrl.searchParams.set("client_secret", env.FB_APP_SECRET);
      longUrl.searchParams.set("fb_exchange_token", shortToken);

      const longRes = await fetch(longUrl.toString());
      const longData = await longRes.json();

      let finalToken = shortToken;
      let isLongLived = false;
      if (longRes.ok && longData.access_token) {
        finalToken = longData.access_token;
        isLongLived = true;
      }

      return jsonResponse({
        access_token: finalToken,
        is_long_lived: isLongLived,
        expires_in: longData.expires_in || exData.expires_in || 0,
      });
    } catch (err) {
      return jsonResponse({ error: `Worker error: ${err.message}` }, 500);
    }
  },
};

function corsHeaders() {
  return {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
  };
}

function jsonResponse(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      "Content-Type": "application/json",
      ...corsHeaders(),
    },
  });
}
