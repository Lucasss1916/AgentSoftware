async function redirect() {
  // 读取参数并打印日志
  const chosenScheme = $persistentStore.read("Redirect_Scheme");
  if (!chosenScheme) {
    $log.error("参数未配置，请选择一个 Schema！");
    $done();
    return;
  }

  // 构造跳转 URL
  const path = $request.url.replace(/^https?:\/\/t\.me/, "");
  const redirectUrl = `${chosenScheme}://t.me${path}`;
  
  $log.info("跳转目标：", redirectUrl);
  $done({ redirect: redirectUrl });
}

redirect();
