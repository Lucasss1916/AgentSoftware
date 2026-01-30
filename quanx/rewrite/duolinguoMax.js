/**
 * Duolingo Max Rewrite for Quantumult X
 * 功能：处理 GZIP 压缩并强制开启 Max/Gold 订阅
 */

const isRequest = typeof $request !== "undefined" && typeof $response === "undefined";

if (isRequest) {
    // --- 请求头处理：强制服务器返回非压缩的明文 JSON ---
    let headers = $request.headers;
    delete headers['Accept-Encoding'];
    delete headers['accept-encoding'];
    $done({ headers });
} else {
    // --- 响应体处理：修改订阅数据 ---
    let body = $response.body;

    if (!body) {
        $done({});
    }

    try {
        let obj = JSON.parse(body);

        if (obj.responses && Array.isArray(obj.responses)) {
            let modified = false;

            obj.responses.forEach((resp, index) => {
                // 检查 body 是否存在且包含用户关键数据
                if (resp.body && (resp.body.includes('subscriberLevel') || resp.body.includes('shopItems'))) {
                    try {
                        let userdata = JSON.parse(resp.body);
                        const now = Math.floor(Date.now() / 1000);

                        // 1. 设置订阅等级
                        userdata.subscriberLevel = 'GOLD';
                        userdata.hasPlus = true;

                        // 2. 注入订阅信息到 shopItems
                        if (!userdata.shopItems) userdata.shopItems = [];
                        
                        // 检查是否已经存在订阅，防止重复注入
                        const hasSub = userdata.shopItems.some(item => item.id && item.id.includes('subscription'));
                        
                        if (!hasSub) {
                            userdata.shopItems.push({
                                "id": "gold_subscription",
                                "purchaseDate": now - 86400, // 昨天
                                "purchasePrice": 0,
                                "subscriptionInfo": {
                                    "expectedExpiration": now + 31536000, // 一年后
                                    "productId": "com.duolingo.DuolingoMobile.subscription.Gold.TwelveMonth.24Q2Max.168",
                                    "renewer": "APPLE",
                                    "renewing": true,
                                    "tier": "twelve_month",
                                    "type": "gold"
                                }
                            });
                        }

                        // 3. 开启所有权益属性
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

                        // 4. 写回数据
                        obj.responses[index].body = JSON.stringify(userdata);
                        modified = true;
                    } catch (e) {
                        console.log("解析子响应体失败: " + e);
                    }
                }
            });

            if (modified) {
                body = JSON.stringify(obj);
            }
        }
        $done({ body });
    } catch (e) {
        console.log("多邻国主脚本运行错误: " + e);
        $done({});
    }
}
