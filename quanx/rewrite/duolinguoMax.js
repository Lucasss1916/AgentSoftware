/**
 * Duolingo Max - 全面抓包版
 * 拦截所有 duolingo 请求，找到用户数据
 */

const isRequest = typeof $request !== "undefined" && typeof $response === "undefined";

if (isRequest) {
    let headers = Object.assign({}, $request.headers);
    delete headers['Accept-Encoding'];
    delete headers['accept-encoding'];
    delete headers['If-None-Match'];
    delete headers['if-none-match'];
    $done({ headers });
    
} else {
    let body = $response.body;
    let url = $request.url;
    
    if (!body || body.length === 0) {
        $done({});
        return;
    }

    try {
        let obj = JSON.parse(body);
        
        // 方式1: 检查 responses 数组结构
        if (obj.responses && Array.isArray(obj.responses)) {
            obj.responses.forEach((item, index) => {
                if (item.body) {
                    try {
                        let innerObj = JSON.parse(item.body);
                        let keys = Object.keys(innerObj);
                        
                        // 检查是否包含用户/订阅相关字段
                        if (keys.includes('subscriberLevel') || 
                            keys.includes('shopItems') || 
                            keys.includes('username') ||
                            keys.includes('hasPlus') ||
                            keys.includes('streak')) {
                            
                            console.log('[Duolingo] ⭐⭐⭐ 找到用户数据！⭐⭐⭐');
                            console.log('[Duolingo] URL: ' + url);
                            console.log('[Duolingo] Index: ' + index);
                            console.log('[Duolingo] 字段: ' + keys.slice(0, 20).join(', '));
                            console.log('[Duolingo] subscriberLevel: ' + innerObj.subscriberLevel);
                            console.log('[Duolingo] hasPlus: ' + innerObj.hasPlus);
                            console.log('[Duolingo] username: ' + innerObj.username);
                        }
                    } catch (e) {}
                }
            });
        }
        
        // 方式2: 直接检查顶级对象
        let topKeys = Object.keys(obj);
        if (topKeys.includes('subscriberLevel') || 
            topKeys.includes('shopItems') || 
            topKeys.includes('username') ||
            topKeys.includes('hasPlus')) {
            
            console.log('[Duolingo] ⭐⭐⭐ 顶级用户数据！⭐⭐⭐');
            console.log('[Duolingo] URL: ' + url);
            console.log('[Duolingo] 字段: ' + topKeys.slice(0, 20).join(', '));
            console.log('[Duolingo] subscriberLevel: ' + obj.subscriberLevel);
            console.log('[Duolingo] hasPlus: ' + obj.hasPlus);
        }
        
        $done({ body });
        
    } catch (e) {
        // 非 JSON 响应，忽略
        $done({ body });
    }
}
