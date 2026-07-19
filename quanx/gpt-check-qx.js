/**
 * GPT 检测(适配 Quantumult X 版)
 *
 * 基于 Surge/Loon 版脚本改写。
 *
 * 注意:
 * 1. QX 不像 Surge/Loon 那样支持直接把“内联节点描述”塞进请求里。
 * 2. 这里改为通过 QX 的 `opts.policy` 指定策略/节点名发起请求。
 * 3. 因此这个脚本依赖 QX 能用节点名称命中对应代理。若只是在预览阶段运行、
 *    或节点名称与最终写入 QX 的 tag 不一致，检测可能失败。
 *
 * 参数
 * - [timeout] 请求超时(单位: 毫秒) 默认 5000
 * - [retries] 重试次数 默认 1
 * - [retry_delay] 重试延时(单位: 毫秒) 默认 1000
 * - [concurrency] 并发数 默认 10
 * - [client] GPT 检测的客户端类型. 默认 iOS
 * - [method] 请求方法. 默认 get
 * - [gpt_prefix] 显示前缀. 默认为 "[GPT] "
 * 注: 节点上总是会添加一个 _gpt 字段, 可用于脚本筛选. 新增 _gpt_latency 字段, 指响应延迟
 * - [cache] 使用缓存, 默认不使用缓存
 * - [disable_failed_cache/ignore_failed_error] 禁用失败缓存. 即不缓存失败结果
 *
 * 关于缓存时长
 * 当使用相关脚本时, 若在对应的脚本中使用参数(一般为 cache, 值设为 true 即可)开启缓存
 * 可在前端(>=2.16.0) 配置各项缓存的默认时长
 * 持久化缓存数据在 JSON 里
 * 可以在脚本的前面添加一个脚本操作, 实现保留 1 小时的缓存:
 * async function operator() {
 *   scriptResourceCache._cleanup(undefined, 1 * 3600 * 1000)
 * }
 */

async function operator(proxies = [], targetPlatform, context) {
  const $ = $substore
  const { isQX } = $.env
  if (!isQX) throw new Error('仅支持 Quantumult X')

  const cacheEnabled = $arguments.cache
  const disableFailedCache = $arguments.disable_failed_cache || $arguments.ignore_failed_error
  const cache = scriptResourceCache
  const gptPrefix = $arguments.gpt_prefix ?? '[GPT] '
  const method = $arguments.method || 'get'
  const url = $arguments.client === 'Android' ? 'https://android.chat.openai.com' : 'https://ios.chat.openai.com'
  const concurrency = parseInt($arguments.concurrency || 10, 10)

  await executeAsyncTasks(
    proxies.map(proxy => () => check(proxy)),
    { concurrency }
  )

  return proxies

  async function check(proxy) {
    const id = cacheEnabled
      ? `gpt:qx:${url}:${JSON.stringify(
          Object.fromEntries(
            Object.entries(proxy).filter(([key]) => !/^(name|collectionName|subName|id|_.*)$/i.test(key))
          )
        )}`
      : undefined

    try {
      const qxNode = ProxyUtils.produce([proxy], 'QX')
      if (!qxNode) {
        $.info(`[${proxy.name}] 跳过: 当前节点无法输出为 QX`)
        return
      }

      const policyName = extractQxPolicyName(qxNode) || proxy.name
      const cached = cacheEnabled ? cache.get(id) : undefined

      if (cached) {
        if (cached.gpt) {
          proxy.name = `${gptPrefix}${proxy.name}`
          proxy._gpt = true
          proxy._gpt_latency = cached.gpt_latency
          $.info(`[${proxy.name}] 使用成功缓存`)
          return
        }
        if (!disableFailedCache) {
          $.info(`[${proxy.name}] 使用失败缓存`)
          return
        }
        $.info(`[${proxy.name}] 不使用失败缓存`)
      }

      const startedAt = Date.now()
      const res = await http({
        method,
        headers: {
          'User-Agent':
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3.1 Mobile/15E148 Safari/604.1',
        },
        url,
        opts: {
          policy: policyName,
        },
      })

      const status = parseInt(res.status ?? res.statusCode ?? 200, 10)
      let body = String(res.body ?? res.rawBody ?? '')
      try {
        body = JSON.parse(body)
      } catch (error) {}

      const msg = body?.error?.code || body?.error?.error_type || body?.cf_details
      const latency = Date.now() - startedAt
      $.info(`[${proxy.name}] status: ${status}, msg: ${msg}, latency: ${latency}, policy: ${policyName}`)

      if (status === 403 && !/unsupported_country/.test(String(msg || ''))) {
        proxy.name = `${gptPrefix}${proxy.name}`
        proxy._gpt = true
        proxy._gpt_latency = latency
        if (cacheEnabled) {
          $.info(`[${proxy.name}] 设置成功缓存`)
          cache.set(id, { gpt: true, gpt_latency: latency })
        }
      } else if (cacheEnabled) {
        $.info(`[${proxy.name}] 设置失败缓存`)
        cache.set(id, {})
      }
    } catch (error) {
      $.error(`[${proxy.name}] ${error.message ?? error}`)
      if (cacheEnabled) {
        $.info(`[${proxy.name}] 设置失败缓存`)
        cache.set(id, {})
      }
    }
  }

  async function http(options = {}) {
    const requestMethod = options.method || 'get'
    const timeout = parseFloat(options.timeout || $arguments.timeout || 5000)
    const retries = parseFloat(options.retries ?? $arguments.retries ?? 1)
    const retryDelay = parseFloat(options.retry_delay ?? $arguments.retry_delay ?? 1000)

    let count = 0
    const request = async () => {
      try {
        return await $.http[requestMethod]({ ...options, timeout })
      } catch (error) {
        if (count < retries) {
          count += 1
          const delay = retryDelay * count
          await $.wait(delay)
          return request()
        }
        throw error
      }
    }

    return request()
  }

  function extractQxPolicyName(qxNode) {
    const text = Array.isArray(qxNode) ? qxNode.join('\n') : String(qxNode)
    const matched = text.match(/(?:^|,\s*)tag\s*=\s*(.+?)\s*$/m)
    return matched?.[1]?.trim()
  }

  function executeAsyncTasks(tasks, { wrap, result, concurrency = 1 } = {}) {
    return new Promise((resolve, reject) => {
      try {
        let running = 0
        const results = []
        let index = 0

        function executeNextTask() {
          while (index < tasks.length && running < concurrency) {
            const taskIndex = index++
            const currentTask = tasks[taskIndex]
            running += 1

            currentTask()
              .then(data => {
                if (result) {
                  results[taskIndex] = wrap ? { data } : data
                }
              })
              .catch(error => {
                if (result) {
                  results[taskIndex] = wrap ? { error } : error
                }
              })
              .finally(() => {
                running -= 1
                executeNextTask()
              })
          }

          if (running === 0) {
            resolve(result ? results : undefined)
          }
        }

        executeNextTask()
      } catch (error) {
        reject(error)
      }
    })
  }
}
