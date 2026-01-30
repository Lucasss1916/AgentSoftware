/**
 * Duolingo Max - Debug Version
 */

const isRequest = typeof $request !== "undefined" && typeof $response === "undefined";

if (isRequest) {
    console.log('[Duolingo] ===== 请求拦截触发 =====');
    console.log('[Duolingo] URL: ' + $request.url);
    
    let headers = Object.assign({}, $request.headers);
    delete headers['Accept-Encoding'];
    delete headers['accept-encoding'];
    delete headers['If-None-Match'];
    delete headers['if-none-match'];
    
    console.log('[Duolingo] 已移除压缩和缓存头');
    $done({ headers });
    
} else {
    console.log('[Duolingo] ===== 响应拦截触发 =====');
    console.log('[Duolingo] URL: ' + $request.url);
    console.log('[Duolingo] Status: ' + $response.status);
    console.log('[Duolingo] Body Length: ' + ($response.body ? $response.body.length : 0));
    
    let body = $response.body;
    
    if (!body || body.length === 0) {
        console.log('[Duolingo] ❌ 响应体为空');
        $done({});
        return;
    }
    
    // 检查是否是压缩数据
    if (body.charCodeAt(0) === 0x1f || body.charCodeAt(0) === 0x8b) {
        console.log('[Duolingo] ❌ 响应体仍是 GZIP 压缩格式');
        $done({});
        return;
    }

    try {
        let obj = JSON.parse(body);
        let modified = false;
        
        console.log('[Duolingo] ✓ JSON 解析成功');
        console.log('[Duolingo] responses 存在: ' + (obj.responses ? 'YES' : 'NO'));
        
        if (obj.responses && Array.isArray(obj.responses)) {
            console.log('[Duolingo] responses 数量: ' + obj.responses.length);
            
            obj.responses.forEach((item, index) => {
                console.log(`[Duolingo] --- 检查 responses[${index}] ---`);
                console.log(`[Duolingo] 有 body: ${item.body ? 'YES' : 'NO'}`);
                
                if (item.body) {
                    const hasSubscriber = item.body.includes('subscriberLevel');
                    const hasShopItems = item.body.includes('shopItems');
                    console.log(`[Duolingo] 包含 subscriberLevel: ${hasSubscriber}`);
                    console.log(`[Duolingo] 包含 shopItems: ${hasShopItems}`);
                    
                    if (hasSubscriber || hasShopItems) {
                        try {
                            let userdata = JSON.parse(item.body);
                            const now = Math.floor(Date.now() / 1000);
                            
                            console.log(`[Duolingo] 原 subscriberLevel: ${userdata.subscriberLevel}`);
                            
                            // 修改会员状态
                            userdata.subscriberLevel = 'GOLD';
                            userdata.hasPlus = true;
                            
                            // 注入订阅
                            if (!userdata.shopItems) userdata.shopItems = [];
                            const hasGold = userdata.shopItems.some(i => i.id && i.id.includes('gold'));
                            
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
                                console.log('[Duolingo] ✓ 已注入 gold_subscription');
                            }
                            
                            // 设置权限标志
                            if (!userdata.trackingProperties) userdata.trackingProperties = {};
                            userdata.trackingProperties.has_item_immersive_subscription = true;
                            userdata.trackingProperties.has_item_premium_subscription = true;
                            userdata.trackingProperties.has_item_live_subscription = true;
                            userdata.trackingProperties.has_item_gold_subscription = true;
                            userdata.trackingProperties.has_item_max_subscription = true;
                            
                            obj.responses[index].body = JSON.stringify(userdata);
                            modified = true;
                            
                            console.log(`[Duolingo] ✓ responses[${index}] 修改完成`);
                            
                        } catch (parseErr) {
                            console.log(`[Duolingo] ❌ responses[${index}].body 解析失败: ${parseErr}`);
                        }
                    }
                }
            });
        }
        
        if (modified) {
            console.log('[Duolingo] ===== 修改成功，返回数据 =====');
            $done({ body: JSON.stringify(obj) });
        } else {
            console.log('[Duolingo] ===== 未修改，原样返回 =====');
            $done({ body });
        }
        
    } catch (e) {
        console.log('[Duolingo] ❌ JSON 解析失败: ' + e.message);
        console.log('[Duolingo] Body 前100字符: ' + body.substring(0, 100));
        $done({ body });
    }
}
