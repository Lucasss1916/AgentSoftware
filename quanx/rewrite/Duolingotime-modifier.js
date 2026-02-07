/*
 * Duolingo Surge Script - Optimized
 * Role: Full Stack Developer Expert Fix
 * 
 * * Surge Argument Configuration:
 * format: clear=true&xp=2&time=60&unlock=false
 */

// --- 1. 参数解析 (增强健壮性) ---
function getArgs() {
    let args = {
        clear: false,    // 修正：默认为 true (根据您的注释习惯)
        xp: 1,
        time: 0,
        unlock: false
    };

    // 增加异常捕获，防止 $argument 未定义导致报错
    try {
        if (typeof $argument !== "undefined" && $argument) {
            let params = $argument.split("&");
            params.forEach(param => {
                let [key, val] = param.split("=");
                if (key && val) {
                    key = key.trim();
                    val = val.trim();
                    if (val === "true") val = true;
                    else if (val === "false") val = false;
                    else if (!isNaN(val)) val = Number(val);
                    args[key] = val;
                }
            });
        }
    } catch (e) {
        console.log("Argument Parse Error: " + e);
    }
    return args;
}

const config = getArgs();

// --- 2. 递归遍历工具 (核心优化) ---
// 将递归逻辑抽象，减少代码重复，并增加层级保护
function traverse(obj, callback) {
    if (typeof obj !== 'object' || obj === null) return;
    
    for (let k in obj) {
        // 执行回调处理当前节点
        callback(obj, k);
        
        // 递归深入
        if (typeof obj[k] === 'object' && obj[k] !== null) {
            traverse(obj[k], callback);
        }
    }
}

// --- 3. 主逻辑 ---
try {
    if (!$response.body) {
        $done({});
    }
    
    let obj = JSON.parse($response.body);

    // === 功能 A: 经验加倍 (XP Multiplier) ===
    if (config.xp > 1) {
        traverse(obj, (parent, key) => {
            // 更严格的匹配：必须是 number，且名称严格匹配 xp 或 amount，防止误伤
            if (typeof parent[key] === 'number') {
                const lowerKey = key.toLowerCase();
                // 排除 id, index 等明显非经验字段，并限制数值范围防止修改 user_id
                if ((lowerKey === 'xp' || lowerKey === 'amount') && parent[key] > 0 && parent[key] < 5000) {
                    parent[key] = Math.floor(parent[key] * config.xp);
                }
            }
        });
    }

    // === 功能 B: 自定义挑战时间 (Timer) ===
    if (config.time > 0) {
        const newTime = config.time * 60; // 分钟转秒
        traverse(obj, (parent, key) => {
            if (typeof parent[key] === 'number') {
                if (key === 'duration' || key === 'timer' || key === 'timeLimit') {
                    parent[key] = newTime;
                }
            }
        });
    }

    // === 功能 C: 解锁所有关卡 (Unlock All) ===
    if (config.unlock) {
        traverse(obj, (parent, key) => {
            if (key === 'locked' && parent[key] === true) {
                parent[key] = false;
            } else if (key === 'state' && parent[key] === 'LOCKED') {
                parent[key] = 'ACTIVE';
            }
        });
    }

    // === 功能 D: 直接通关/秒过 (Instant Clear) ===
    // 注意：此功能高度依赖 API 版本，如果导致白屏，请在参数中关闭 clear=false
    if (config.clear) {
        const type = obj.type;
        // 跳过不应被清空的特殊题型
        const skipTypes = ["SIDE_QUEST_RAMP_UP_PRACTICE", "MATCH_PRACTICE"];
        
        if (!type || !skipTypes.includes(type)) {
            const pools = [
                'challenges',
                'adaptiveChallenges',
                'adaptiveInterleavedChallenges',
                'mistakesReplacementChallenges'
            ];
            
            pools.forEach(pool => {
                if (obj[pool] && Array.isArray(obj[pool])) {
                    // 策略：不完全清空，可能导致白屏。
                    // 很多脚本选择清空，如果遇到白屏，可尝试改为保留最后一个元素：
                    // if (obj[pool].length > 0) obj[pool] = [obj[pool][0]]; 
                    obj[pool] = []; 
                }
            });
            
            // 针对 sessionStart 结构的额外处理
            if (obj.sessionElementSolutions && Array.isArray(obj.sessionElementSolutions)) {
                 obj.sessionElementSolutions = [];
            }
        }
        
        // 处理 Audio 课程
        if (obj.metadata && obj.metadata.type === "duoradio") {
             if (obj.elements && Array.isArray(obj.elements)) obj.elements = [];
        }
    }

    $done({ body: JSON.stringify(obj) });

} catch (e) {
    console.log("Duolingo Script Error: " + e);
    // 出错时原样返回，保证 App 不会因为脚本错误而断网
    $done({});
}
