/*
 * Duolingo BoxJS Controller
 * 对应 BoxJS 设置 ID：
 * - duolingo_instant_clear (秒过)
 * - duolingo_xp_boost (经验加倍开关)
 * - duolingo_multiplier (经验倍数)
 * - duolingo_timer_switch (时间增强开关)
 * - duolingo_timer_mins (自定义时间)
 * - duolingo_unlock_all (解锁关卡)
 */

// --- 1. 读取 BoxJS 配置的辅助函数 ---
function getVal(key, defaultVal) {
  const val = $prefs ? $prefs.valueForKey(key) : $persistentStore.read(key);
  if (!val) return defaultVal;
  // 处理 BoxJS 存储布尔值可能为字符串的情况
  if (val === 'true') return true;
  if (val === 'false') return false;
  return val;
}

const config = {
  instantClear: getVal('duolingo_instant_clear', false),
  xpBoost: getVal('duolingo_xp_boost', false),
  xpMulti: parseInt(getVal('duolingo_multiplier', '1')),
  timerSwitch: getVal('duolingo_timer_switch', false),
  timerMins: parseInt(getVal('duolingo_timer_mins', '60')),
  unlockAll: getVal('duolingo_unlock_all', false)
};

// --- 2. 主逻辑 ---
try {
  let obj = JSON.parse($response.body);

  // === 功能 A: 经验加倍 (XP Boost) ===
  if (config.xpBoost && config.xpMulti > 1) {
    // 递归查找并修改可能的 XP 字段 (baseXp, xp, amount)
    // 注意：多邻国服务端校验严格，此修改可能仅显示有效或特定模式有效
    const multiplyXP = (o) => {
      for (let k in o) {
        if (typeof o[k] === 'number' && (k.toLowerCase().includes('xp') || k === 'amount')) {
           // 避免修改到非 XP 的 amount，这里仅作简单处理，可根据实际抓包优化
           if(o[k] > 0 && o[k] < 1000) o[k] = o[k] * config.xpMulti;
        } else if (typeof o[k] === 'object' && o[k] !== null) {
          multiplyXP(o[k]);
        }
      }
    };
    multiplyXP(obj);
  }

  // === 功能 B: 自定义挑战时间 (Timer) ===
  if (config.timerSwitch) {
    const newTime = config.timerMins * 60; // 转换为秒
    const modifyTimer = (o) => {
       for (let k in o) {
         // 常见的时间字段: duration, timer, timeLimit
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
  if (config.unlockAll) {
    const unlock = (o) => {
      for (let k in o) {
        if (k === 'locked' && o[k] === true) {
          o[k] = false;
        } else if (k === 'state' && o[k] === 'LOCKED') {
          o[k] = 'ACTIVE'; // 或 'COMPLETED'
        } else if (typeof o[k] === 'object' && o[k] !== null) {
          unlock(o[k]);
        }
      }
    };
    unlock(obj);
  }

  // === 功能 D: 直接通关/秒过 (Instant Clear) - 原有逻辑优化 ===
  if (config.instantClear) {
    const type = obj.type;
    // 保留原本的防误伤逻辑：跳过配对赛和升级挑战
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
  // 出错时保持原样，避免断网
  console.log("Duolingo Script Error: " + e);
  $done({});
}
