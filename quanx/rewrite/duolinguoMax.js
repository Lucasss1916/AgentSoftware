let body = $response.body;
console.log('=== Duolingo Max Script Started ===');
console.log('Original response length:', body.length);

try {
    let obj = JSON.parse(body);
    console.log('1. JSON parsed successfully');
    console.log('2. Has responses property?', !!obj.responses);
    
    if (obj.responses && obj.responses.length >= 2) {
        console.log('3. responses length >= 2: YES, length =', obj.responses.length);
        
        // 检查第一个response是否有headers
        const firstResponse = obj.responses[0];
        console.log('4. First response has headers?', !!firstResponse.headers);
        
        if (firstResponse.headers) {
            const hasEtag = 'etag' in firstResponse.headers;
            console.log('5. Has etag in headers?', hasEtag);
            console.log('6. Headers keys:', Object.keys(firstResponse.headers));
            
            if (!hasEtag) {
                console.log('7. Proceeding with subscription modification');
                
                const now = Math.floor(Date.now() / 1000);
                console.log('8. Current timestamp:', now);
                
                // 检查是否有body
                console.log('9. First response has body?', !!firstResponse.body);
                console.log('10. Body type:', typeof firstResponse.body);
                
                if (firstResponse.body) {
                    let userdata;
                    try {
                        userdata = JSON.parse(firstResponse.body);
                        console.log('11. Userdata parsed successfully');
                        console.log('12. Userdata keys:', Object.keys(userdata));
                    } catch (parseError) {
                        console.log('11. ERROR parsing userdata:', parseError);
                        $done({ body });
                        return;
                    }
                    
                    // 检查是否已经存在 shopItems
                    console.log('13. Has shopItems?', !!userdata.shopItems);
                    console.log('14. shopItems type:', typeof userdata.shopItems);
                    
                    if (!userdata.shopItems) {
                        userdata.shopItems = [];
                        console.log('15. Created empty shopItems array');
                    } else {
                        console.log('15. shopItems array length:', userdata.shopItems.length);
                    }
                    
                    // 检查是否已经有 gold_subscription
                    const existingGoldSub = userdata.shopItems.find(item => item.id === 'gold_subscription');
                    console.log('16. Already has gold_subscription?', !!existingGoldSub);
                    
                    if (!existingGoldSub) {
                        const newSubscription = {
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
                        };
                        
                        userdata.shopItems.push(newSubscription);
                        console.log('17. Added new subscription:', newSubscription);
                        console.log('18. New shopItems length:', userdata.shopItems.length);
                    }
                    
                    // 设置订阅级别
                    console.log('19. Current subscriberLevel:', userdata.subscriberLevel);
                    userdata.subscriberLevel = 'GOLD';
                    console.log('20. Set subscriberLevel to:', userdata.subscriberLevel);
                    
                    // 设置 trackingProperties
                    if (!userdata.trackingProperties) {
                        userdata.trackingProperties = {};
                        console.log('21. Created trackingProperties object');
                    }
                    
                    userdata.trackingProperties.has_item_immersive_subscription = true;
                    userdata.trackingProperties.has_item_premium_subscription = true;
                    userdata.trackingProperties.has_item_live_subscription = true;
                    userdata.trackingProperties.has_item_gold_subscription = true;
                    userdata.trackingProperties.has_item_max_subscription = true;
                    
                    console.log('22. Updated trackingProperties:', userdata.trackingProperties);
                    
                    // 更新响应体
                    obj.responses[0].body = JSON.stringify(userdata);
                    body = JSON.stringify(obj);
                    
                    console.log('23. Response modified successfully');
                    console.log('24. New response length:', body.length);
                } else {
                    console.log('9. ERROR: First response has no body');
                }
            } else {
                console.log('7. Skipping modification (has etag)');
            }
        } else {
            console.log('4. ERROR: First response has no headers');
        }
    } else {
        console.log('3. responses length < 2 or no responses property');
        if (obj.responses) {
            console.log('   Responses length:', obj.responses.length);
        }
    }
} catch (e) {
    console.log('ERROR in main try-catch:', e);
    console.log('Error stack:', e.stack);
}

console.log('=== Duolingo Max Script Ended ===');
$done({ body });
