/*
 * Duolingo Surge Argument Controller
 * * 使用 Surge 参数控制功能 (argument):
 * 格式: key=value&key2=value2
 * * 可用参数:
 * 1. clear: (true/false) 是否开启秒过/清空题目。默认: true
 * 2. xp: (数字) 经验倍数。设置大于1即开启。默认: 1 (不加倍)
 * 3. time: (数字) 自定义限时挑战时长(分钟)。设置大于0即开启。默认: 0 (不修改)
 * 4. unlock: (true/false) 是否尝试解锁所有关卡。默认: false
 * * 示例 argument 写法:
 * clear=true&xp=2&time=60
 * (意为：开启秒过，经验2倍，限时挑战改为60分钟)
 */

// --- 1. 解析 Surge 参数 ---
function getArgs() {
    let args = {
        clear: flase,   // 默认不开启秒过
        xp: 1,         // 默认经验不加倍
        time: 0,       // 默认不修改时间
        unlock: false  // 默认不修改解锁状态
    };

    if (typeof $argument !== "undefined" && $argument) {
        let params = $argument.split("&");
        params.forEach(param => {
            let [key, val] = param.split("=");
            if (key && val) {
                // 处理布尔值
                if (val === "true") val = true;
                else if (val === "false") val = false;
                // 处理数字
                else if (!isNaN(val)) val = Number(val);
                
                args[key] = val;
            }
        });
    }
    return args;
}

const config = getArgs();

// --- 2. 主逻辑 ---
try {
  let obj = JSON.parse($response.body);

  // === 功能 A: 经验加倍 (XP Multiplier) ===
  // 参数: xp (例如: xp=2)
  if (config.xp > 1) {
    const multiplyXP = (o) => {
      for (let k in o) {
        // 查找 xp 或 amount 字段 (排除太大的数字防止误伤ID)
        if (typeof o[k] === 'number' && (k.toLowerCase().includes('xp') || k === 'amount')) {
           if(o[k] > 0 && o[k] < 1000) o[k] = Math.floor(o[k] * config.xp);
        } else if (typeof o[k] === 'object' && o[k] !== null) {
          multiplyXP(o[k]);
        }
      }
    };
    multiplyXP(obj);
  }

  // === 功能 B: 自定义挑战时间 (Timer) ===
  // 参数: time (例如: time=60)
  if (config.time > 0) {
    const newTime = config.time * 60; // 分钟转秒
    const modifyTimer = (o) => {
       for (let k in o) {
         if ((k === 'duration' || k === 'timer' || k === 'timeLimit') && typeof o[k] === 'number') {
            o[k] = newTime;
         } else if (typeof o[k] === 'object' && o[k] !== null) {
            modifyTimer(o[k]);
         }
       }
    };
    modifyTimer(obj);
  }

  // === 功能 C: 解锁所有关卡 (Unlock All) ===
  // 参数: unlock (例如: unlock=true)
  if (config.unlock) {
    const unlock = (o) => {
      for (let k in o) {
        if (k === 'locked' && o[k] === true) {
          o[k] = false;
        } else if (k === 'state' && o[k] === 'LOCKED') {
          o[k] = 'ACTIVE';
        } else if (typeof o[k] === 'object' && o[k] !== null) {
          unlock(o[k]);
        }
      }
    };
    unlock(obj);
  }

  // === 功能 D: 直接通关/秒过 (Instant Clear) ===
  // 参数: clear (例如: clear=true)
  if (config.clear) {
    const type = obj.type;
    // 跳过配对赛和升级挑战
    const skipTypes = ["SIDE_QUEST_RAMP_UP_PRACTICE", "MATCH_PRACTICE"];
    
    if (type && !skipTypes.includes(type)) {
      const pools = [
          'challenges',
          'adaptiveChallenges',
          'adaptiveInterleavedChallenges',
          'mistakesReplacementChallenges'
      ];
      pools.forEach(pool => {
          if (obj[pool] && obj[pool].length > 0) obj[pool] = [];
      });
    }
    
    // 处理 Audio 课程
    if (obj.metadata && obj.metadata.type === "duoradio") {
      if (obj.elements && obj.elements.length > 0) obj.elements = [];
    }
  }

  $done({ body: JSON.stringify(obj) });
} catch (e) {
  console.log("Duolingo Script Error: " + e);
  $done({});
}
