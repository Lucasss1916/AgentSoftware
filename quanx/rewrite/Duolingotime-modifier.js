/*
 * Duolingo Surge Script - Core Modifier
 * Author: Lucasss1916 & Gemini
 * 
 * Arguments:
 * clear=true   // 开启秒过 (移除题目内容)
 * xp=2         // 经验倍率 (1为不修改)
 * time=60      // 挑战时间 (单位：分钟，脚本会自动转为秒)
 * unlock=false // 解锁灰色关卡 (视觉)
 */

// --- 1. 参数解析 ---
function getArgs() {
    let args = {
        clear: false,
        xp: 1,
        time: 0,
        unlock: false
    };

    try {
        if (typeof $argument !== "undefined" && $argument) {
            // console.log(`[Duolingo] Raw Args: ${$argument}`);
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
        console.log(`[Duolingo] Args Parse Error: ${e}`);
    }
    return args;
}

// --- 2. 递归遍历工具 ---
function traverse(obj, callback) {
    if (typeof obj !== 'object' || obj === null) return;
    for (let k in obj) {
        callback(obj, k);
        if (typeof obj[k] === 'object' && obj[k] !== null) {
            traverse(obj[k], callback);
        }
    }
}

// --- 3. 主逻辑 ---
const config = getArgs();

try {
    if (typeof $response === "undefined" || !$response.body) {
        $done({});
    }

    let obj = JSON.parse($response.body);

    // === 功能 A: 经验加倍 (XP Multiplier) ===
    // 只有当 xp > 1 时才执行遍历，节省性能
    if (config.xp > 1) {
        traverse(obj, (parent, key) => {
            if (typeof parent[key] === 'number') {
                const lowerKey = key.toLowerCase();
                // 限制最大值防止封号，排除 id 等字段
                if ((lowerKey === 'xp' || lowerKey === 'amount') && parent[key] > 0 && parent[key] < 5000) {
                    parent[key] = Math.floor(parent[key] * config.xp);
                }
            }
        });
    }

    // === 功能 B: 自定义挑战时间 (Timer) ===
    // 输入为分钟，转换为秒
    if (config.time > 0) {
        const timeInSeconds = config.time * 60; 
        traverse(obj, (parent, key) => {
            if (typeof parent[key] === 'number') {
                // 匹配 duration(通常是秒), timer, timeLimit
                if (key === 'duration' || key === 'timer' || key === 'timeLimit') {
                    parent[key] = timeInSeconds;
                }
                // 针对某些特定题型的倒计时字段
                if (key === 'expectedDuration') {
                    parent[key] = timeInSeconds;
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
    if (config.clear) {
        const type = obj.type;
        // 白名单：跳过不应被清空的特殊题型 (如配对题可能会卡死)
        const skipTypes = ["MATCH_PRACTICE"]; 
        
        if (!type || !skipTypes.includes(type)) {
            const pools = [
                'challenges',
                'adaptiveChallenges',
                'adaptiveInterleavedChallenges',
                'mistakesReplacementChallenges',
                'elements' // 某些新版结构
            ];
            
            pools.forEach(pool => {
                if (obj[pool] && Array.isArray(obj[pool])) {
                    obj[pool] = []; 
                }
            });
            
            // 处理 Session 结构
            if (obj.sessionElementSolutions && Array.isArray(obj.sessionElementSolutions)) {
                 obj.sessionElementSolutions = [];
            }
        }
        
        // 处理 Audio 课程 (duoradio)
        if (obj.metadata && obj.metadata.type === "duoradio") {
             if (obj.elements && Array.isArray(obj.elements)) obj.elements = [];
        }
    }

    $done({ body: JSON.stringify(obj) });

} catch (e) {
    console.log(`[Duolingo] Script Error: ${e}`);
    $done({});
}
