/**
 * Duolingo Max - QX 专用版
 * 适配 Quantumult X
 */

const isRequest = typeof $request !== "undefined" && typeof $response === "undefined";

if (isRequest) {
    // 请求阶段：移除压缩头
    let headers = Object.assign({}, $request.headers);
    delete headers['Accept-Encoding'];
    delete headers['accept-encoding'];
    delete headers['If-None-Match'];
    delete headers['if-none-match'];
    $done({ headers });
    
} else {
    // 响应阶段：修改数据
    try {
        let body = $response.body;
        if (!body) {
            $done({});
            return;
        }
        
        let obj = JSON.parse(body);
        let modified = false;
        
        // 检查 batch 响应结构
        if (obj.responses && Array.isArray(obj.responses)) {
            
            for (let i = 0; i < obj.responses.length; i++) {
                let item = obj.responses[i];
                
                // 跳过有 etag 的响应
                if (item.headers && item.headers.etag) {
                    continue;
                }
                
                if (item.body) {
                    try {
                        let userdata = JSON.parse(item.body);
                        
                        // 检查是否是用户数据（包含用户相关字段）
                        let keys = Object.keys(userdata);
                        let isUserData = keys.includes('streak') || 
                                        keys.includes('username') || 
                                        keys.includes('learningLanguage') ||
                                        keys.includes('fromLanguage') ||
                                        keys.includes('courses') ||
                                        keys.includes('currentCourseId') ||
                                        keys.length > 10;
                        
                        if (isUserData) {
                            const now = Math.floor(Date.now() / 1000);
                            
                            // 添加 shopItems
                            if (!userdata.shopItems) {
                                userdata.shopItems = [];
                            }
                            
                            // 检查是否已有订阅
                            let hasGold = userdata.shopItems.some(item => item.id === 'gold_subscription');
                            
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
                            
                            // 设置订阅等级
                            userdata.subscriberLevel = 'GOLD';
                            
                            // 设置追踪属性
                            if (!userdata.trackingProperties) {
                                userdata.trackingProperties = {};
                            }
                            userdata.trackingProperties.has_item_immersive_subscription = true;
                            userdata.trackingProperties.has_item_premium_subscription = true;
                            userdata.trackingProperties.has_item_live_subscription = true;
                            userdata.trackingProperties.has_item_gold_subscription = true;
                            userdata.trackingProperties.has_item_max_subscription = true;
                            
                            // 更新响应
                            obj.responses[i].body = JSON.stringify(userdata);
                            modified = true;
                            
                            console.log('[Duolingo] ✅ 已解锁 Max！Index: ' + i);
                        }
                        
                    } catch (e) {
                        // 解析失败，跳过
                    }
                }
            }
        }
        
        // 检查顶级用户数据（/users/ 端点）
        if (obj.hasPlus !== undefined || obj.subscriberLevel !== undefined || obj.shopItems !== undefined) {
            const now = Math.floor(Date.now() / 1000);
            
            if (!obj.shopItems) {
                obj.shopItems = [];
            }
            
            let hasGold = obj.shopItems.some(item => item.id === 'gold_subscription');
            
            if (!hasGold) {
                obj.shopItems.push({
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
            
            obj.subscriberLevel = 'GOLD';
            obj.hasPlus = true;
            
            if (!obj.trackingProperties) {
                obj.trackingProperties = {};
            }
            obj.trackingProperties.has_item_immersive_subscription = true;
            obj.trackingProperties.has_item_premium_subscription = true;
            obj.trackingProperties.has_item_live_subscription = true;
            obj.trackingProperties.has_item_gold_subscription = true;
            obj.trackingProperties.has_item_max_subscription = true;
            
            modified = true;
            console.log('[Duolingo] ✅ 已解锁 Max（顶级数据）！');
        }
        
        if (modified) {
            $done({ body: JSON.stringify(obj) });
        } else {
            $done({ body });
        }
        
    } catch (e) {
        console.log('[Duolingo] 错误: ' + e.message);
        $done({});
    }
}
