try {
  const obj = JSON.parse($response.body);

  function getArg(name, defVal) {
    if (!$argument) return defVal;
    const re = new RegExp("(^|&)" + name + "=([^&]*)(&|$)");
    const m = $argument.match(re);
    return m ? decodeURIComponent(m[2]) : defVal;
  }

  const mins = parseInt(getArg("timer_mins", "60"), 10);
  const seconds = mins * 60;

  if (!isNaN(seconds) && seconds > 0 && Array.isArray(obj.liveOpsChallenges)) {
    obj.liveOpsChallenges.forEach((challenge) => {
      if (challenge.initialTime) challenge.initialTime = seconds;
      if (Array.isArray(challenge.initialLevelTimes)) {
        challenge.initialLevelTimes = challenge.initialLevelTimes.map(() => seconds);
      }
      if (Array.isArray(challenge.initialSessionTimes)) {
        challenge.initialSessionTimes = challenge.initialSessionTimes.map(() => seconds);
      }
    });
  }

  $done({ body: JSON.stringify(obj) });
} catch (e) {
  $done({ body: $response.body });
}
