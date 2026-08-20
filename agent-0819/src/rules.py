from dataclasses import dataclass
import re


@dataclass(frozen=True)
class Rule:
    category: str
    severity: str
    topic: str
    pattern: str
    message: str
    suggestion: str
    query: str
    flags: int = re.IGNORECASE


RULES = [
    Rule("react-effect-dependencies", "high", "react", r"useEffect\([\s\S]*?,\s*\[\s*\]\s*\)", "Effect 使用外部值但依赖数组为空。", "补齐依赖，或重构 Effect 以消除不稳定依赖。", "React useEffect dependencies stale closure cleanup"),
    Rule("react-unstable-key", "medium", "react", r"key\s*=\s*\{\s*(?:index|i)\s*\}", "React 列表使用数组下标作为 key。", "改用实体稳定 ID。", "React list stable key index reconciliation"),
    Rule("vue-missing-key", "medium", "vue", r"<[^>]+v-for=(?:(?!:key)[^>])*>", "Vue v-for 缺少稳定 :key。", "为列表项绑定实体稳定 ID。", "Vue v-for stable key list"),
    Rule("vue-reactivity", "high", "vue", r"const\s*\{[^}]+\}\s*=\s*reactive\(", "直接解构 reactive 对象可能丢失响应性。", "使用 toRefs/toRef 或直接读取响应式对象。", "Vue reactive destructuring toRefs reactivity"),
    Rule("typescript-any", "medium", "typescript", r"(?::|as)\s*any\b", "any 关闭了这条数据链路的类型检查。", "改为 unknown，并在边界使用类型守卫或 Schema。", "TypeScript avoid any unknown narrowing"),
    Rule("typescript-null-assertion", "medium", "typescript", r"(?:querySelector\([^\n]+\)|\b\w+)!", "非空断言缺少运行时保证。", "显式处理 null/undefined 或提供可验证守卫。", "TypeScript non-null assertion strictNullChecks null safety"),
    Rule("performance-heavy-import", "medium", "performance", r"import\s+.+\s+from\s+['\"](?:monaco-editor|echarts|lodash)['\"]", "重依赖被同步打入当前入口。", "按路由或功能使用动态 import，并比较首包体积。", "performance code splitting dynamic import heavy bundle"),
    Rule("performance-image", "low", "performance", r"<img\s+(?![^>]*loading=)(?![^>]*(?:width=|aspect-ratio))[^>]*>", "图片缺少懒加载或稳定尺寸信息。", "非首屏图片增加 lazy，并设置尺寸或宽高比。", "image performance lazy loading dimensions layout shift"),
    Rule("security-token-storage", "high", "security", r"localStorage\.setItem\([^\n]*(?:token|session|auth)", "敏感凭据被写入 localStorage。", "评估 HttpOnly Cookie、短时令牌与撤销策略。", "security localStorage token HttpOnly Cookie XSS"),
    Rule("security-xss", "high", "security", r"(?:dangerouslySetInnerHTML|v-html|\.innerHTML\s*=)", "代码绕过了框架默认文本转义。", "使用白名单 HTML 清洗并增加恶意输入测试。", "security XSS innerHTML v-html sanitization"),
    Rule("security-hardcoded-secret", "high", "security", r"(?:api[_-]?key|secret)\s*[:=]\s*['\"](?:sk-|[A-Za-z0-9_-]{16,})", "前端代码中疑似硬编码密钥。", "立即轮换并移动到服务端代理。", "frontend hardcoded API key secret dependency security"),
]


def match_rules(diff_text: str) -> list[Rule]:
    added = "\n".join(line[1:] for line in diff_text.splitlines() if line.startswith("+") and not line.startswith("+++"))
    return [rule for rule in RULES if re.search(rule.pattern, added, rule.flags)]
