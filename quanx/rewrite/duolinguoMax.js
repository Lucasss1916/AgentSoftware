/**
 * Duolingo Max - Final QX Logic
 * 修复 Responses Count 为 1 时失效的问题
 */

const isRequest = typeof $request !== "undefined" && typeof $response === "undefined";

if (isRequest) {
    let headers = $request.headers;
    delete headers['Accept-Encoding'];
    delete headers['accept-encoding'];
    delete headers['If-None-Match'];
    $done({ headers });
} else {
    let body = $response.body;
    if (!body) $done({});

    try {
        let obj = JSON.parse(body);
        let modified = false;

        if (obj.responses && Array.isArray(obj.responses)) {
            // 遍历所有 responses，不再限制长度必须 >= 2
            obj.responses.forEach((item, index) => {
                if (item.body && (item.body.includes('subscriberLevel') || item.body.includes('shopItems'))) {
                    console.log(`[Duolingo] 修改第 ${index} 个子响应体...`);
                    let userdata = JSON.parse(item.body);
                    const now = Math.floor(Date.now() / 1000);

                    // 1. 会员等级与 Plus 状态
                    userdata.subscriberLevel = 'GOLD';
                    userdata.hasPlus = true;

                    // 2. 商店订阅项注入
                    if (!userdata.shopItems) userdata.shopItems = [];
                    const hasGold = userdata.shopItems.some(i => i.id && i.id.includes('gold'));
                    if (!hasGold) {
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
                    }

                    // 3. 开启全部会员权限标志
                    if (!userdata.trackingProperties) userdata.trackingProperties = {};
                    ["has_item_immersive_subscription", "has_item_premium_subscription", "has_item_gold_subscription", "has_item_max_subscription"].forEach(k => {
                        userdata.trackingProperties[k] = true;
                    });

                    obj.responses[index].body = JSON.stringify(userdata);
                    modified = true;
                }
            });
        }

        if (modified) {
            console.log('[Duolingo] 修改完成，返回数据');
            $done({ body: JSON.stringify(obj) });
        } else {
            console.log('[Duolingo] 未发现符合特征的子响应体');
            $done({ body });
        }

    } catch (e) {
        console.log('[Duolingo] 解析报错: ' + e);
        $done({ body: $response.body });
    }
}
