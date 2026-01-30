let body = $response.body;
console.log('=== Duolingo Max Script Started ===');
console.log('Request URL:', $request.url);
console.log('Original response length:', body.length);

// 只显示前500个字符，避免日志太长
if (body.length > 500) {
    console.log('Response preview:', body.substring(0, 500) + '...');
} else {
    console.log('Full response:', body);
}

try {
    let obj = JSON.parse(body);
    console.log('1. JSON parsed successfully');
    
    // 查看对象的所有顶级键
    console.log('Object keys:', Object.keys(obj));
    
    // 检查是否有 responses 属性
    if (obj.responses) {
        console.log('2. Has responses property: YES');
        console.log('3. responses type:', typeof obj.responses);
        console.log('4. responses length:', obj.responses.length);
        
        if (Array.isArray(obj.responses) && obj.responses.length >= 1) {
            console.log('5. Checking first response...');
            const firstResponse = obj.responses[0];
            console.log('6. First response keys:', Object.keys(firstResponse));
            
            // 尝试不同的可能路径
            if (firstResponse.body) {
                console.log('7. Found body in first response');
                try {
                    const userdata = JSON.parse(firstResponse.body);
                    console.log('8. Userdata keys:', Object.keys(userdata));
                    console.log('9. Checking for subscription data...');
                    
                    // 检查当前订阅状态
                    console.log('10. Current subscriberLevel:', userdata.subscriberLevel);
                    console.log('11. Has shopItems?', !!userdata.shopItems);
                    
                    // 尝试修改 - 使用更通用的方法
                    userdata.subscriberLevel = 'GOLD';
                    
                    if (!userdata.shopItems) userdata.shopItems = [];
                    
                    // 添加订阅信息
                    const now = Math.floor(Date.now() / 1000);
                    const subscriptionExists = userdata.shopItems.some(item => 
                        item.id && item.id.includes('gold') || item.id.includes('subscription')
                    );
                    
                    if (!subscriptionExists) {
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
                        console.log('12. Added gold subscription');
                    }
                    
                    // 更新响应
                    obj.responses[0].body = JSON.stringify(userdata);
                    body = JSON.stringify(obj);
                    console.log('13. Response modified successfully');
                    
                } catch (parseError) {
                    console.log('7. ERROR parsing userdata:', parseError);
                }
            } else {
                console.log('7. No body in first response');
                
                // 也许响应结构完全不同，尝试直接修改
                console.log('8. Attempting direct modification...');
                
                // 检查是否是直接的用户数据
                if (obj.user || obj.subscriberLevel) {
                    console.log('9. Found user data at root level');
                    obj.subscriberLevel = 'GOLD';
                    if (!obj.shopItems) obj.shopItems = [];
                    
                    const now = Math.floor(Date.now() / 1000);
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
                    
                    body = JSON.stringify(obj);
                    console.log('10. Direct modification successful');
                }
            }
        }
    } else {
        console.log('2. No responses property found');
        
        // 尝试不同的结构
        if (obj.user) {
            console.log('3. Found user property');
            console.log('4. User object keys:', Object.keys(obj.user));
            
            // 直接修改用户对象
            if (obj.user.subscriberLevel !== undefined) {
                console.log('5. Current subscriberLevel:', obj.user.subscriberLevel);
                obj.user.subscriberLevel = 'GOLD';
                console.log('6. Updated subscriberLevel to GOLD');
                
                body = JSON.stringify(obj);
                console.log('7. Response modified');
            }
        } else if (obj.subscription) {
            console.log('3. Found subscription property');
            console.log('4. Subscription details:', obj.subscription);
        }
    }
    
} catch (e) {
    console.log('ERROR in main try-catch:', e);
    console.log('Error message:', e.message);
}

console.log('=== Duolingo Max Script Ended ===');
$done({ body });
