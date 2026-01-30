/*
Duolingo Max for Quantumult X
*/

let body = $response.body;

// 1. 兼容二进制 body 处理
if (typeof body === 'undefined' || body === null) {
    $done({});
}

try {
    let obj = JSON.parse(body);

    // 2. 增强逻辑判断 (去掉对 responses 长度的严格要求，增加容错)
    if (obj.responses && obj.responses.length > 0) {
        
        // 检查第一个 response 是否包含 body 且不是由缓存(etag)产生的
        const firstResp = obj.responses[0];
        if (firstResp.body && (!firstResp.headers || !firstResp.headers.etag)) {
            
            let userdata = JSON.parse(firstResp.body);
            const now = Math.floor(Date.now() / 1000);

            // 3. 修改订阅数据
            userdata.subscriberLevel = 'GOLD';
            userdata.hasPlus = true; // 强制开启 Plus 状态
            
            if (!userdata.shopItems) userdata.shopItems = [];
            
            // 避免重复添加
            const hasGold = userdata.shopItems.some(item => item.id === 'gold_subscription');
            if (!hasGold) {
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
            }

            // 4. 增强 Tracking 属性修改
            if (!userdata.trackingProperties) userdata.trackingProperties = {};
            const props = [
                "has_item_immersive_subscription",
                "has_item_premium_subscription",
                "has_item_live_subscription",
                "has_item_gold_subscription",
                "has_item_max_subscription"
            ];
            props.forEach(p => userdata.trackingProperties[p] = true);

            // 回填数据
            obj.responses[0].body = JSON.stringify(userdata);
            body = JSON.stringify(obj);
        }
    }
    $done({ body });
} catch (e) {
    console.log("Duolingo Max Error: " + e);
    $done({ body }); // 报错时返回原体，避免 App 崩溃
}
