/**
 * Duolingo Max Unlock - QX Edition (Ported from Egern/Loon)
 * 适配 TestFlight 版与正式版
 */

const isRequest = typeof $request !== "undefined" && typeof $response === "undefined";

if (isRequest) {
    // --- 【请求阶段】强制要求服务器返回明文，解决 GZIP 乱码导致 JSON.parse 报错的问题 ---
    let headers = $request.headers;
    delete headers['Accept-Encoding'];
    delete headers['accept-encoding'];
    $done({ headers });
} else {
    // --- 【响应阶段】Egern 原始逻辑适配 ---
    let body = $response.body;
    if (!body) {
        $done({});
    }

    try {
        let obj = JSON.parse(body);

        // 镜像 Egern 逻辑：检查 responses 数组且排除 Etag 缓存
        if (obj.responses && obj.responses.length >= 2) {
            const firstResponse = obj.responses[0];
            
            // 只有当不是 304 缓存（没有 etag）且有 body 时才修改
            if (firstResponse.body && (!firstResponse.headers || !('etag' in firstResponse.headers))) {
                const now = Math.floor(Date.now() / 1000);
                let userdata = JSON.parse(firstResponse.body);

                // 1. 注入商店订阅项
                if (!userdata.shopItems) userdata.shopItems = [];
                userdata.shopItems.push({
                    id: 'gold_subscription',
                    purchaseDate: now - 172800,
                    purchasePrice: 0,
                    subscriptionInfo: {
                        expectedExpiration: now + 31536000,
                        productId: "com.duolingo.DuolingoMobile.subscription.Gold.TwelveMonth.24Q2Max.168",
                        renewer: 'APPLE',
                        renewing: true,
                        tier: 'twelve_month',
                        type: 'gold'
                    }
                });

                // 2. 核心等级修改
                userdata.subscriberLevel = 'GOLD';
                userdata.hasPlus = true; // 强制开启 Plus 布尔值

                // 3. 追踪属性修改 (Tracking Properties)
                if (!userdata.trackingProperties) userdata.trackingProperties = {};
                const premiumKeys = [
                    "has_item_immersive_subscription",
                    "has_item_premium_subscription",
                    "has_item_live_subscription",
                    "has_item_gold_subscription",
                    "has_item_max_subscription"
                ];
                premiumKeys.forEach(key => {
                    userdata.trackingProperties[key] = true;
                });

                // 4. 写回结构
                obj.responses[0].body = JSON.stringify(userdata);
                body = JSON.stringify(obj);
            }
        }
        $done({ body });
    } catch (e) {
        console.log("Duolingo Unlock Error: " + e);
        // 出错时返回原始 Body，确保 App 不会网络报错
        $done({ body: $response.body });
    }
}
