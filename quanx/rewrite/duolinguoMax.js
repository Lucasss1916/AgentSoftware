const url = $request.url;

if ($response.body) {
    try {
        let obj = JSON.parse($response.body);
        
        // 检查 responses 数组是否存在且长度足够
        if (!obj.responses || obj.responses.length < 2 || 
            (obj.responses[0].headers && 'etag' in obj.responses[0].headers)) {
            $done({});
            return;
        }
        
        const now = Math.floor(Date.now() / 1000);
        const userdata = JSON.parse(obj.responses[0].body);
        
        // 初始化 shopItems 数组
        if (!userdata.shopItems) {
            userdata.shopItems = [];
        }
        
        // 添加 Gold 订阅信息
        const goldSubscription = {
            id: 'gold_subscription',
            purchaseDate: now - 172800,
            purchasePrice: 0,
            subscriptionInfo: {
                expectedExpiration: now + 31536000, // 1年后
                productId: "com.duolingo.DuolingoMobile.subscription.Gold.TwelveMonth.24Q2Max.168",
                renewer: 'APPLE',
                renewing: true,
                tier: 'twelve_month',
                type: 'gold'
            }
        };
        
        // 检查是否已存在 gold_subscription
        const existingIndex = userdata.shopItems.findIndex(item => item.id === 'gold_subscription');
        if (existingIndex !== -1) {
            userdata.shopItems[existingIndex] = goldSubscription;
        } else {
            userdata.shopItems.push(goldSubscription);
        }
        
        // 设置用户等级
        userdata.subscriberLevel = 'GOLD';
        
        // 初始化 trackingProperties
        if (!userdata.trackingProperties) {
            userdata.trackingProperties = {};
        }
        
        // 设置订阅标志
        const subscriptionFlags = [
            'has_item_immersive_subscription',
            'has_item_premium_subscription', 
            'has_item_live_subscription',
            'has_item_gold_subscription',
            'has_item_max_subscription'
        ];
        
        subscriptionFlags.forEach(flag => {
            userdata.trackingProperties[flag] = true;
        });
        
        // 更新响应体
        obj.responses[0].body = JSON.stringify(userdata);
        
        // 返回修改后的响应
        $done({
            body: JSON.stringify(obj)
        });
        
    } catch (e) {
        console.log(`Duolingo Max 解锁脚本错误: ${e}`);
        $done({});
    }
} else {
    $done({});
}