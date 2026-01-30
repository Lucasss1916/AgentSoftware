/**
 * Duolingo Max - QX Debug Version
 */

const isRequest = typeof $request !== "undefined" && typeof $response === "undefined";

if (isRequest) {
    console.log('--- Duolingo Request Start ---');
    let headers = $request.headers;
    
    // 强制删除所有可能导致压缩或缓存的头
    delete headers['Accept-Encoding'];
    delete headers['accept-encoding'];
    delete headers['If-None-Match'];
    delete headers['if-none-match'];
    
    console.log('Headers modified: GZIP and Etag-check disabled');
    $done({ headers });

} else {
    console.log('--- Duolingo Response Start ---');
    let body = $response.body;

    if (!body) {
        console.log('Error: Response body is empty');
        $done({});
    }

    try {
        let obj = JSON.parse(body);
        console.log('Step 1: Main JSON parsed. Responses count: ' + (obj.responses ? obj.responses.length : 0));

        if (obj.responses && obj.responses.length >= 2) {
            console.log('Step 2: Checking first response item...');
            let firstResp = obj.responses[0];

            if (firstResp.body) {
                console.log('Step 3: Found sub-body, attempting to parse...');
                let userdata = JSON.parse(firstResp.body);

                // 核心修改逻辑
                userdata.subscriberLevel = 'GOLD';
                userdata.hasPlus = true;
                
                if (!userdata.shopItems) userdata.shopItems = [];
                const now = Math.floor(Date.now() / 1000);
                
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
                ["has_item_immersive_subscription", "has_item_premium_subscription", "has_item_gold_subscription", "has_item_max_subscription"].forEach(k => {
                    userdata.trackingProperties[k] = true;
                });

                console.log('Step 4: Userdata modified successfully');

                // 写回
                obj.responses[0].body = JSON.stringify(userdata);
                body = JSON.stringify(obj);
                console.log('Step 5: Final body re-assembled');
            } else {
                console.log('Notice: First response item has no body (might be 304)');
            }
        } else {
            console.log('Notice: Responses structure not as expected');
        }

        $done({ body });

    } catch (e) {
        console.log('!!! Main Catch Error: ' + e);
        // 如果报错，检查是否是二进制乱码
        if (body && body.length > 0) {
            console.log('Body preview (first 50 chars): ' + body.slice(0, 50));
        }
        $done({ body: $response.body });
    }
}
