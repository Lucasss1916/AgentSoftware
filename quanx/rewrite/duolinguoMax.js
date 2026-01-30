let body = $response.body;

if (!body) $done({});

try {
    let obj = JSON.parse(body);
    if (obj.responses) {
        // 遍历 responses 找到包含 user 数据的那个
        obj.responses.forEach((resp, index) => {
            if (resp.body && resp.body.includes('subscriberLevel')) {
                let userdata = JSON.parse(resp.body);
                const now = Math.floor(Date.now() / 1000);
                
                // 核心修改
                userdata.subscriberLevel = 'GOLD';
                userdata.hasPlus = true;
                
                if (!userdata.shopItems) userdata.shopItems = [];
                userdata.shopItems.push({
                    id: 'gold_subscription',
                    purchaseDate: now - 172800,
                    subscriptionInfo: {
                        expectedExpiration: now + 31536000,
                        productId: "com.duolingo.DuolingoMobile.subscription.Gold.TwelveMonth.24Q2Max.168",
                        renewer: 'APPLE',
                        renewing: true,
                        tier: 'twelve_month',
                        type: 'gold'
                    }
                });

                if (!userdata.trackingProperties) userdata.trackingProperties = {};
                ["has_item_immersive_subscription", "has_item_premium_subscription", "has_item_gold_subscription", "has_item_max_subscription"].forEach(p => {
                    userdata.trackingProperties[p] = true;
                });

                obj.responses[index].body = JSON.stringify(userdata);
            }
        });
        body = JSON.stringify(obj);
    }
    $done({ body });
} catch (e) {
    console.log("Duolingo Parse Error: " + e);
    $done({});
}
