/**
 * Duolingo Max - 抓包调试版
 * 用于分析 API 返回的数据结构
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
    
    if (!body || body.length === 0) {
        $done({});
        return;
    }

    try {
        let obj = JSON.parse(body);
        
        if (obj.responses && Array.isArray(obj.responses)) {
            console.log('[Duolingo] ========== 开始分析 ==========');
            console.log('[Duolingo] responses 数量: ' + obj.responses.length);
            
            obj.responses.forEach((item, index) => {
                console.log(`[Duolingo] --- responses[${index}] ---`);
                
                if (item.body) {
                    // 打印 body 的前 500 个字符，看看里面有什么
                    console.log(`[Duolingo] body 预览: ${item.body.substring(0, 500)}`);
                    
                    // 尝试解析并列出所有顶级字段
                    try {
                        let innerObj = JSON.parse(item.body);
                        let keys = Object.keys(innerObj);
                        console.log(`[Duolingo] 字段列表: ${keys.join(', ')}`);
                        
                        // 检查是否有用户相关字段
                        if (innerObj.id || innerObj.username || innerObj.email) {
                            console.log('[Duolingo] ⭐ 发现用户数据！');
                            console.log('[Duolingo] id: ' + innerObj.id);
                            console.log('[Duolingo] username: ' + innerObj.username);
                            console.log('[Duolingo] subscriberLevel: ' + innerObj.subscriberLevel);
                            console.log('[Duolingo] hasPlus: ' + innerObj.hasPlus);
                        }
                        
                    } catch (e) {
                        console.log(`[Duolingo] body 不是 JSON`);
                    }
                } else {
                    console.log(`[Duolingo] 无 body`);
                }
            });
            
            console.log('[Duolingo] ========== 分析结束 ==========');
        }
        
        $done({ body });
        
    } catch (e) {
        console.log('[Duolingo] 解析失败: ' + e.message);
        $done({ body });
    }
}
