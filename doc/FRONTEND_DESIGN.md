# 前端设计实现文档（Frontend Design）

> 本文是 [`VIS_DESIGN.md`](VIS_DESIGN.md) 的**实现侧映射**。视觉文档回答「想要什么气质」，本文回答「在 Astro + 原生 CSS 里怎么落成 token、组件和排版」。
> 两者冲突时，以 VIS_DESIGN 的**判断标准（第 11 节）**为准：① 更新后无需重排 ② 一眼可辨非 AI 界面 ③ 风格不干扰阅读路径。

---

## 0. 技术与设计决策摘要

| 维度 | 决策 | 依据 |
|---|---|---|
| 构建 | **Astro**，构建时渲染，输出静态站托管于 GitHub Pages | VIS §9「构建时渲染可接受」；content collections 天然实现「统一结构母版」 |
| 风格层 | **原生 CSS 自定义属性**（design tokens），单一 `tokens.css` | 不引入 Tailwind 工具类噪声；token 即「风格集中点」（VIS §9） |
| 内容层 | **YAML/JSON 数据条目**为主（卡片），homepage 的 about-me 为少量短文 | 站点**无长文**；VIS §8「预设规则驱动差异，而非手工重排」 |
| 语言 | **英文站**，中文仅零星出现在简介/about-me | 字体栈兜底已覆盖，无需独立 CJK 标题字体 |
| 色彩 | **操作色板**：4 主色承担画面，4 强调色限额使用 | 对 VIS §3 的收紧——6 等强度高饱和色无法在持续更新中保持协调（§1.1） |
| 破格 | **确定性破格**：图片侧/强调条侧/偏移由索引派生，绝不手工摆放 | 解决 VIS §5「越界」与 §11「无需重排」的冲突（§4.2） |

> 两处对 VIS_DESIGN 的偏离（色板收紧、破格规则化）是审美兼维护的主动权衡，已在对应小节标注理由。

---

## 1. 风格配置（Design Tokens）

所有 token 定义在 `src/styles/tokens.css` 的 `:root`，全局 `BaseLayout.astro` 引入一次。组件**只消费变量，不写死数值**——这是「风格集中、结构稳定」的技术保证。

### 1.1 色彩：操作色板

> **对 VIS §3 的收紧**：原文列了 6 种荧光色等强度并列。在持续更新场景里，每条新内容若可自由选色，整站很快退化成「只剩噪声」（VIS §3 自己的警告）。
> 做法：把颜色分成**承重的 4 主色**（占画面 ~95%）和**限额的 4 强调色**（点缀、稀有）。这样既保住「酸、亮、不稳」的张力，又有重心。

```css
:root {
  /* ── 主色：承重，几乎所有画面由这 4 色构成 ── */
  --c-anchor: #3b2bf0;   /* 电蓝紫 · 视觉锚点：链接、主结构块、focus */
  --c-acid:   #ccff00;   /* 酸性黄绿 · 唯一最强注意力触发：当前项/关键 CTA/高亮条 */
  --c-ink:    #0e0e0e;   /* 真黑 · 边界、标题、分割线、正文 */
  --c-paper:  #f3ecdd;   /* 暖纸白 · 页面底色（印刷物质感，非玩具白） */

  /* ── 强调色：限额，单屏每色面积 ≤ ~5%，仅用于标记/情绪层 ── */
  --c-rose:   #ff2e6e;   /* 亮玫红 · 警示/情绪强调 */
  --c-pink:   #ffc4dd;   /* 浅粉 · 柔性强调底（薄填充） */
  --c-mint:   #8fefc9;   /* 薄荷绿 · 过渡/调和填充 */
  --c-orange: #ff5a1e;   /* 信号橙 · 警示、"NEW"、错误态 */

  /* ── 派生中性（保留印刷层次，避免纯彩噪声） ── */
  --c-paper-2:    #eae2d0;  /* 次级底：斑马块、引用、图片占位 */
  --c-ink-muted:  #4a4a45;  /* 次级文字：meta、简介（仍偏黑，不用灰雾） */
  --c-hairline:   #0e0e0e;  /* 分割线 = 真黑，不用浅灰 */
}
```

**使用配额规则（写进 code review checklist）：**

| 角色 | 允许的颜色 | 禁止 |
|---|---|---|
| 页面底色 | `--c-paper` / 局部 `--c-paper-2` | 大面积高饱和铺底 |
| 正文 / 标题 / 边界 | `--c-ink` | 用强调色描边正文 |
| 链接 / 主结构 / focus | `--c-anchor` | 用 acid 当大面积底 |
| 当前态 / 关键触发 / 高亮条 | `--c-acid`（**全站克制，越少越响**） | 多处同时 acid |
| 标记 / 情绪点缀 | rose/pink/mint/orange，**单屏总和受限** | 一个模块用满 3 种以上强调色 |

**封面色（accent）取值**来自 frontmatter 的枚举（§3.7），不允许自由 hex，从根上防止「每条内容自己挑色」。

### 1.2 字体与文字气质

VIS §4 要求三层对比：**标题极粗硬** / **正文中性耐读** / **批注呈研究笔记气质**。映射为三套字体栈：

```css
:root {
  /* 标题 · 极粗几何无衬线，海报感 */
  --font-display: "Unbounded", system-ui, sans-serif;
  /* 正文 · 中性清楚的 grotesque（兜底覆盖零星中文） */
  --font-body:    "Schibsted Grotesk", "PingFang SC", "Microsoft YaHei", sans-serif;
  /* 批注/元信息/标签 · 等宽，档案与研究笔记气质 */
  --font-mono:    "Martian Mono", ui-monospace, monospace;
}
```

> **字体选择理由**：刻意避开 Inter/Roboto/Arial/系统字体与已被用滥的 Space Grotesk。
> - **Unbounded**（900/800）——几何、响、有人格，提供编辑布鲁特主义要的「粗硬标题」。
> - **Schibsted Grotesk**——中性但不平庸，简介/about-me 耐读，与 Unbounded 形成强弱对比。
> - **Martian Mono**——技术档案感，专供 meta/标签/年份，强化「研究笔记」层。
> 三者均可由 Fontsource 自托管，构建时打包，无运行时请求。
> 英文站，中文仅零星出现在简介/about-me，由 body 栈的 `PingFang SC`/`YaHei` 兜底即可，**无需独立 CJK 标题字体**。

**字号阶梯**（模块化，海报式大跳变；用 `clamp()` 做响应式）：

```css
:root {
  --fs-hero:   clamp(2.75rem, 8vw, 6.5rem);  /* homepage 巨标题/姓名 · display 900 */
  --fs-h1:     clamp(2rem, 4vw, 3.25rem);    /* 页面标题 · display 800 */
  --fs-h2:     clamp(1.5rem, 2.5vw, 2.25rem);/* 章节 · display 700 */
  --fs-h3:     1.375rem;                     /* 卡片标题 · display 700 */
  --fs-body:   1.0625rem;                    /* 正文 17px · body 400 */
  --fs-small:  0.875rem;                     /* 次要正文 · body 400 */
  --fs-meta:   0.75rem;                      /* meta/标签/年份 · mono 500 + letter-spacing */

  --lh-tight:  1.02;   /* 巨标题：极紧，块面感 */
  --lh-head:   1.1;    /* 标题 */
  --lh-body:   1.6;    /* 正文：阅读路径稳定（VIS §11③） */

  --tracking-meta: 0.08em;  /* mono 标签的字距，强化档案标牌感 */
}
```

字重约定：display 仅用 `700 / 800 / 900`；body 用 `400 / 600`；mono 用 `400 / 500`。**禁止过细字重**（VIS §4）。

### 1.3 间距 · 边界 · 表面

```css
:root {
  /* 间距 · 8px 基准网格 */
  --sp-1: 4px;  --sp-2: 8px;  --sp-3: 12px; --sp-4: 16px;
  --sp-5: 24px; --sp-6: 32px; --sp-7: 48px; --sp-8: 64px; --sp-9: 96px;

  /* 边界 · 布鲁特主义靠边框造层级，不靠柔光 */
  --bd-thin:  2px solid var(--c-ink);
  --bd:       2.5px solid var(--c-ink);
  --bd-thick: 4px solid var(--c-ink);

  /* 圆角 · 全站直角（VIS §6） */
  --radius: 0;

  /* 阴影 · 唯一允许的是「硬位移阴影」，无模糊，像叠放的印刷物 */
  --shadow-hard:    5px 5px 0 var(--c-ink);
  --shadow-hard-lg: 8px 8px 0 var(--c-ink);
  --shadow-accent:  6px 6px 0 var(--c-anchor);  /* featured 卡用彩色硬阴影 */

  /* 容器 */
  --maxw-page: 1280px;   /* 整页最大宽（homepage 用满） */
  --maxw-col:  920px;    /* 单列卡片/正文列上限 */
}
```

> **VIS §6 落地**：层级一律用 `border + 硬位移阴影 + 颜色反差` 构建；**全站禁止** `border-radius > 0`、`filter: blur`、带模糊半径的 `box-shadow`、玻璃/磨砂。写进 lint 约束。

### 1.4 纸感纹理（克制）

为避免「过于平滑的商业界面」（VIS §1），底色叠一层极淡噪点，但不喧宾夺主：

```css
body {
  background-color: var(--c-paper);
  background-image: url("/textures/grain.svg"); /* 极淡 SVG 噪点，opacity 内嵌 ~0.04 */
}
```

噪点是**唯一**的全局纹理。不叠加渐变网格、不用大面积图案底（VIS §7「图形是干预不是填充」）。

---

## 2. 几何标记库（图形语言）

VIS §7：几何元素是**附着在内容上的批注标记**，不是背景装饰、不承担结构。实现为一组**可复用、确定性**的小部件（CSS 伪元素 + 内联 SVG），由组件按规则调用，不手工散布。

| 标记 | 形态 | 用途 | 实现 |
|---|---|---|---|
| **高亮条** `mark-bar` | acid 实心横条 | 标题下/章节起始/当前项 | `::before` 宽块 |
| **斜切角** `mark-clip` | 卡片一角 45° 裁切 | 卡片"被裁切的印刷物"感 | `clip-path: polygon(...)` |
| **外链箭头** `mark-arrow` | 粗短箭头 ↗ | 卡片"跳转外部链接"指向 | 内联 SVG，`currentColor` |
| **星标** `mark-star` | 6 角硬星 | featured 标记 | 内联 SVG |
| **点阵** `mark-dots` | 散点网格 | homepage 留白处的"批注感" | 重复径向渐变伪元素 |

约束：单个内容模块**至多挂 1–2 个标记**；标记颜色仅取 acid 或当前 accent；标记由组件字段或 `nth-child` 规则决定，**模板不接受逐条手填坐标**（VIS §8/§9）。卡片因跳外链，**固定带 `mark-arrow`**。

```css
.mark-bar::before {
  content: ""; display: block;
  width: var(--sp-7); height: 10px;
  background: var(--c-acid); border: var(--bd-thin);
  margin-bottom: var(--sp-3);
}
.mark-clip { clip-path: polygon(0 0, 100% 0, 100% calc(100% - 18px), calc(100% - 18px) 100%, 0 100%); }
```

---

## 3. 组件设计（组件母版）

母版原则（VIS §8）：**一套结构，差异来自预设字段**。卡片组件吃同一套 frontmatter 契约（§3.7），通过有限枚举字段产生可控差异，新增内容自动继承框架。

### 3.1 内容卡 `Card.astro`（project / more 的统一母版）

卡片 = **图片 + 标题 + 简介 + 跳转外部链接**。数量不多 → **单列**；做成图文横排，整卡可点、新标签页打开。

```
┌─[accent 强调条]──────────────────────────────────┐
│ ┌─────────────┐  PROJECT · 2025          ↗  [mono]│
│ │             │  极粗标题                          │  ← display 700
│ │    image    │  一句话简介，body 中性体……        │  ← body, --c-ink-muted
│ │ (16:9 cover)│  #tag  #tag                         │  ← Tag 组件
│ └─────────────┘                                     │
└────────────────────────────────────────────────┘
   └─ 硬位移阴影；偶数项图片移到右侧（确定性破格 §4.2）
```

锚点结构（project / more 共用）：
- **容器**：`<a href={href} target="_blank" rel="noopener noreferrer">`，`--bd` 边框 + `--radius:0` + `--shadow-hard`，底色 `--c-paper`。
- **图片**：`--bd` 黑边，**强制 `aspect-ratio: 16/9` + `object-fit: cover`**——统一裁切，保证母版一致（不同源图不破节奏）。
- **强调条**：顶部 acid/accent 横条；图片左右侧由 `nth-child` 奇偶决定。
- **meta 行**：mono、`--fs-meta`，含 KIND 标牌 + 可选年份 + `mark-arrow`。
- **标题 / 简介 / 标签行**：见上。

差异**只**来自字段：`accent`、`tags`、`featured`（挂星标 + 彩色硬阴影）、`year`。**禁止**为单条卡写独立布局（VIS §8）。

```astro
---
// Card.astro
const { entry, index, kind } = Astro.props;
const { title, summary, href, image, tags, accent = "anchor", featured, year } = entry.data;
---
<a class:list={["card", `accent-${accent}`, { featured }]}
   style={`--i:${index}`} href={href} target="_blank" rel="noopener noreferrer">
  <div class="card__bar"></div>
  <img class="card__img" src={image} alt={title} width="480" height="270" loading="lazy" />
  <div class="card__body">
    <p class="card__meta">{kind.toUpperCase()}{year && ` · ${year}`} <Arrow /></p>
    <h3 class="card__title">{title}</h3>
    <p class="card__summary">{summary}</p>
    <ul class="card__tags">{tags.map(t => <Tag label={t} />)}</ul>
  </div>
</a>
```

### 3.2 标签 `Tag.astro`
mono 文字、直角硬边框、薄填充。默认透明底 + 黑边；hover/active 反相填 acid。

```css
.tag {
  font: 500 var(--fs-meta)/1 var(--font-mono);
  letter-spacing: var(--tracking-meta);
  padding: var(--sp-1) var(--sp-2);
  border: var(--bd-thin); border-radius: 0; text-transform: uppercase;
}
.tag:hover { background: var(--c-acid); }
```

### 3.3 章节标题 `SectionHeader.astro`
编辑杂志式：序号标牌（mono）+ 极粗标题（display）+ 高亮条。可整体相对网格做**确定性偏移**（§4.2）。

```
[ 01 / PROJECTS ]      ← mono 标牌
项目                    ← display 800，左侧挂 mark-bar
```

### 3.4 导航 `Nav.astro`（稳定，不随内容增长）
常驻顶部，直角黑边底栏。条目固定为三栏 `Project / More / CV`（左侧站名/logo 回 Home）。这是**稳定设计、不改动**，因此不套用 §4.2 的增长规则。
- 当前页：acid 高亮底。
- **CV 是下载而非页面**：`<a href="/cv.pdf" download>CV ↓</a>`，无路由。

### 3.5 入口卡 `EntryCard.astro`（homepage 底部主元素）
homepage 底部的**主视觉**：三张大卡 `Project` / `More` / `CV`，**专门版式**（区别于 §3.1 内容卡）。视觉分量大：满列宽、`--fs-h1` 标题、`mark-bar` + 箭头、可铺 accent 实底或大面积 acid。数量固定为 3，可手工编排版式。
- `Project` / `More` → 站内路由，箭头 **→**。
- `CV` → **下载** `/cv.pdf`（`download` 属性），箭头 **↓**，与 Nav 的 CV 按钮指向同一文件。

```
┌────────────────┐ ┌────────────────┐ ┌────────────────┐
│ ▌              │ │ ▌              │ │ ▌              │
│  PROJECT    →  │ │  MORE       →  │ │  CV         ↓  │  ← display, --fs-h1
│  学术项目      │ │  其他作品      │ │  简历下载      │
└────────────────┘ └────────────────┘ └────────────────┘
```

### 3.6 链接列表 `LinkList.astro`（homepage 底部次元素）
「相关网页链接」（GitHub / 邮箱 / 社交等），**次级权重**：横排 **mono 小按钮**（非大卡），直角黑边、外链带 ↗、hover 反相 acid。
**外链可能新增 → 确定排版规则**：所有链接是等高 mono chip，按 `order` 字段排序后自动 `flex-wrap` 横排，换行自然承接，**无需手工摆位**（VIS §8/§9）。视觉上明确低于 EntryCard（更小、无填充底、成排而非成块）。

### 3.7 frontmatter 契约（母版的数据接口）

用 Astro content collections（**content layer / `glob` loader**）+ Zod 校验，**字段即风格旋钮**。内容数据放在**仓库根 `./content/`**（非 `src/content/`）；schema/collections 定义在 `./content/config.ts`，由 `src/content.config.ts` 再导出（Astro 要求 config 落在 `src/`）。project / more 共用 `card` schema，homepage 文案走 `home` schema：

```ts
// content/config.ts  （src/content.config.ts 仅 re-export 此文件）
import { defineCollection, z } from "astro:content";
import { glob } from "astro/loaders";

const accent = z.enum(["anchor", "acid", "rose", "pink", "mint", "orange"]);

const card = z.object({
  title:    z.string(),
  summary:  z.string().max(140),
  href:     z.string().url(),            // 外部跳转链接（必填）
  image:    z.string(),                  // 封面图（/images/...）
  tags:     z.array(z.string()).max(5).default([]),
  accent:   accent.default("anchor"),    // 封面色：仅枚举，禁自由 hex
  featured: z.boolean().default(false),  // 星标 + 彩色硬阴影
  year:     z.coerce.number().optional(),
  order:    z.number().default(0),       // 手控排序（数量少，手排即可）
});

// homepage 文案——index.astro 不再硬编码任何文字
const home = z.object({
  name:    z.string(),
  tagline: z.string(),
  aboutme: z.array(z.string()).default([]),   // 段落数组（末段可为中文）
  links:   z.array(z.object({                 // 首页外链（§3.6）
    label: z.string(), href: z.string(), order: z.number().default(0),
  })).default([]),
});

export const collections = {
  projects: defineCollection({ loader: glob({ pattern: "**/*.yaml", base: "./content/projects" }), schema: card }),
  more:     defineCollection({ loader: glob({ pattern: "**/*.yaml", base: "./content/more" }),     schema: card }),
  home:     defineCollection({ loader: glob({ pattern: "*.yaml",    base: "./content" }),           schema: home }),
};
```

> 新增卡片 = 在 `content/projects|more/` 丢一个 `.yaml`，**同一 schema、同一 Card 母版**，视觉框架自动继承（VIS §8）。每个 collection 可预设默认 accent（projects→anchor、more→orange），减少逐条决策。**homepage 文案在 `content/home.yaml`**（`home` 单例 collection）——`name/tagline/aboutme/links`，`index.astro` 用 `getCollection("home")[0]` 读取，模板零硬编码文案。

---

## 4. 网页排版（布局）

### 4.1 整体策略
- **内容页（project / more）**：居中**单列**，`max-width: --maxw-col`，卡片纵向堆叠——稳定阅读路径与可维护性（VIS §5/§11）。
- **homepage**：用满 `--maxw-page`，**允许手工不对称**（你的要求；且内容不增长、无维护压力，VIS §5 的"装饰允许失衡"在此最适用）。
- 装饰可越界，但越界量是 token 化的负 margin，不手摆坐标。

### 4.2 确定性破格系统 ⭐

> **对 VIS §5「越界/偏移」与 §11「无需重排」冲突的解法**：内容流的破格**绝不手工摆放**，全部由**索引/奇偶派生**。内容无限增长也不会错乱，仍保有"失衡感"。

每个卡片拿到 `--i`（`index`），破格由 `nth-child` 驱动：

```css
/* 图片左右交替——单列里最强的编辑式节奏 */
.card:nth-child(even) { flex-direction: row-reverse; }
.card:nth-child(even) .card__bar { /* 强调条移到另一侧 */ }

/* 每 3 张里第 2 张相对列轴微缩进，制造参差（量固定，不手填） */
.card:nth-child(3n+2) { margin-left: var(--sp-6); }

/* featured：彩色硬阴影 + 星标 */
.card.featured { box-shadow: var(--shadow-accent); }

/* 章节标题相对列左移半格（确定性，全站一致） */
.section-header { margin-left: calc(-1 * var(--sp-6)); }
```

**红线（VIS §9）**：内容流**禁止**旋转、文本环绕、逐条手工拼贴。`transform: rotate()` 仅允许用于 **homepage 的单个静态装饰件**且角度写死在 token。破格规则集中在 `breaks.css`，便于全局调参。

### 4.3 页面清单

| 页面 | 路由 | 布局 | 要点 |
|---|---|---|---|
| **Homepage** | `/` | §10.1 撞色分栏 hero | hero 双栏（蓝紫 2/3 文字 + acid 1/3 酸性肖像，见 §10.1）+ 底部 `EntryCard`×3（主，Project/More → 路由、CV ↓ 下载）+ `LinkList`（次，相关外链）；姓名用 `--fs-hero` |
| **Project** | `/projects` | `SectionHeader` + 单列 Card（§10.2 纹理边栏） | 学术项目卡；卡片跳外链；破格走 §4.2 |
| **More** | `/more` | `SectionHeader` + 单列 Card（§10.2 纹理边栏） | 非学术项目，结构同 Project，仅默认 accent 不同 |
| **CV** | — | 无页面 | Nav 按钮 `download` 直接下载 `/cv.pdf` |

> Homepage 底部明确主次：`EntryCard`×3 为主（大卡、`--fs-h1`，Project/More 站内 → 、CV ↓ 下载，专门版式见 §3.5），`LinkList` 为次（mono 小按钮横排、外链 ↗，见 §3.6）。两者视觉权重拉开，避免底部糊成一团。

### 4.4 about-me 短文排版
- 宽度 `--maxw-col`，`line-height: --lh-body`，body 字体。
- 起始挂一个 `mark-bar`；可在关键句旁用 acid 行内高亮。
- 极短（几行），不做长文层级，无侧边注。

---

## 5. 动效

气质偏印刷物 → **克制**。集中在两处高价值时刻（CSS-only，Astro 默认零 JS）：

1. **首屏一次性 staggered 入场**：homepage 的姓名/图片与首批卡用 `animation-delay` 依次淡入上移（`--i` 派生延迟）。
2. **硬阴影物理 hover**：卡片/按钮 hover 时阴影位移→0、主体 `translate(3px,3px)`，模拟"被按下贴合"——比柔光 hover 更贴纸媒感。

```css
.card { transition: transform .12s steps(2), box-shadow .12s steps(2); } /* steps：机械、非缓动 */
.card:hover { transform: translate(3px, 3px); box-shadow: 2px 2px 0 var(--c-ink); }

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation: none !important; transition: none !important; }
}
```

> 用 `steps()` 而非 ease——硬切的机械感呼应布鲁特主义，避免"柔光商业界面"的顺滑过渡。

---

## 6. 可访问性与性能

- **对比度**：acid #ccff00 / pink / mint 仅配**黑字**；anchor #3b2bf0 / rose 可配白字。所有组合需过 WCAG AA。强调色绝不做正文色。
- **焦点态**：`:focus-visible` 用 `outline: 3px solid var(--c-anchor); outline-offset: 2px`，直角。
- **外链**：卡片/链接 `target="_blank"` 必带 `rel="noopener noreferrer"`，并对屏幕阅读器标注"(opens in new tab)"。
- **字体加载**：Fontsource 自托管 + `font-display: swap` + `preload` 首屏 display 字体子集。
- **图片**：用 Astro `<Image>` 构建时压缩 + 显式宽高 + `aspect-ratio` 防 CLS。
- **零运行时**：Astro 默认不发 JS；本站无筛选/交互需求，保持纯静态。

---

## 7. 文件结构（Astro）

```
src/
  styles/
    tokens.css        ← §1 全部 token（唯一风格集中点）
    base.css          ← reset + body 纸感 + 排版默认 + §10.2 .texture-margins 卡页外壳
    breaks.css        ← §4.2 确定性破格规则（集中便于调参）
  components/
    Card.astro  Tag.astro  SectionHeader.astro
    Nav.astro  EntryCard.astro  LinkList.astro  Markers.astro
  layouts/
    BaseLayout.astro     ← 引入 tokens/base/breaks + Nav，挂全局结构
  content.config.ts      ← 仅 re-export ../content/config（Astro 要求 config 落在 src/）
  pages/
    index.astro          ← homepage（§10.1 撞色分栏 hero + about-me，scoped 样式；文案读 content/home.yaml）
    projects.astro       ← 单列卡列表（§10.2 .texture-margins 外壳）
    more.astro           ← 单列卡列表（§10.2 .texture-margins 外壳）
content/                 ← 内容数据（仓库根，非 src/content）
  config.ts              ← §3.7 schema + collections（glob loader）
  home.yaml              ← homepage 文案（name/tagline/aboutme/links）
  projects/*.yaml        ← 学术项目卡
  more/*.yaml            ← 非学术项目卡
scripts/                 ← 离线构建脚本（非运行时）
  process_portraits.py   ← §10.1 三层错位人像流水线（rembg 抠像 + 灰度/点阵/双色调）
  gen_blotches.py        ← §10.2 撞色曲线斑纹 SVG 生成器（种子可复现）
  requirements.txt       ← 流水线依赖
public/
  cv.pdf                 ← Nav 直接下载
  images/
    portrait{1,2}.jpg        ← 人像源图
    portrait{1,2}-acid.png   ← 流水线产物（hero 用，透明 PNG）
    placeholder-cover.svg    ← 卡片封面占位
  textures/
    grain.svg            ← §1.4 噪点
    blotches.svg         ← §10.2 撞色斑纹（gen_blotches.py 生成）
  fonts/                 ← 自托管字体子集（Fontsource 打包）
```

> §10 的两项强化已**正式纳入**结构：hero 分栏样式落在 `index.astro` 的 scoped `<style>`，卡页纹理外壳落在 `base.css` 的 `.texture-margins`。不再有独立的 `experimental.css`，也无回滚开关。

---

## 8. VIS_DESIGN → 实现 映射表

| VIS 节 | 设计意图 | 本文落点 |
|---|---|---|
| §1 生长的视觉笔记 | 反过度精致 | 纸感噪点 §1.4 · 硬阴影非柔光 §1.3 · steps 动效 §5 |
| §2 Acid×Brutalism | 海报态度 + 目录秩序 | display 字体 §1.2 · 单列守序 §4.1 + 确定性破格 §4.2 |
| §3 色彩 | 主次分明的荧光 | **操作色板** §1.1（收紧 6→4+4） |
| §4 字体三层 | 粗硬/中性/笔记 | 三套字体栈 + 字号阶梯 §1.2 |
| §5 版式越界 | 稳定结构 + 局部失衡 | 单列内容流守序 §4.1 · **确定性破格** §4.2 · homepage 手工不对称 |
| §6 直角硬边 | 边框造层级 | `--radius:0` + `--bd` + `--shadow-hard` §1.3（禁圆角/柔光） |
| §7 几何标记 | 干预非填充 | 标记库 §2（每模块 ≤2 个、规则调用、卡片固定带 ↗） |
| §8 内容母版 | 字段驱动差异 | Card 母版 §3.1 + frontmatter 契约 §3.7 |
| §9 更新折中 | 结构稳定、风格集中 | tokens.css / breaks.css 集中 · content collections 自动继承 |
| §10 参照 | 借手法非复刻 | 编辑式排版 + 破格 + mono 档案层，不做风格练习 |
| §11 判断标准 | 不重排/可辨/不挡阅读 | 母版+确定性破格(不重排) · 操作色板+字体(可辨) · 单列+克制动效(不挡阅读) |

---

## 9. 待定项与风险

1. ✅ **卡片封面比例**：已定 **16:9**（`aspect-ratio: 16/9 + object-fit: cover`，§3.1）。源图非 16:9 一律 cover 裁切。

2. ✅ **homepage 底部主次**：已定 `EntryCard` 为主、`LinkList` 为次（§3.5/§3.6/§4.3）；外链增长走 `flex-wrap` 确定排版，不手摆。

3. **acid 的"唯一最强"纪律靠人守**：建议在 review checklist 写死"单屏 acid 面积上限"，否则强调色会失控（VIS §3 的老问题）。

4. **homepage 手工不对称的边界**：手工自由度高 → 维护成本也高。建议把 homepage 的破格也尽量沉淀成几个固定"版位"，避免每次改版重排（VIS §11①）。

5. **`grain.svg` 噪点强度**需真机校准——纸感与"脏"只隔一线，opacity 建议从 0.03 起调。

---

## 10. 视觉强化（已正式纳入）

> 目的：原「纸色 + 黑字 + 小色标」基线偏素，在两个**局部、静态、与内容无关**的区域加强视觉冲击。两项最初作为可回滚实验试做，验收通过后**已正式并入结构**（不再有 `experimental.css` / `exp-*` 钩子 / 回滚开关）：
> - **§10.1 hero 分栏**：样式落在 `index.astro` 的 scoped `<style>`（首页独占），人像走 `scripts/process_portraits.py` 离线流水线。
> - **§10.2 卡页纹理**：外壳 `.texture-margins` 落在 `base.css`，纹理 `scripts/gen_blotches.py` 离线生成 `public/textures/blotches.svg`。
> - 原则不变：只复用既有 `--c-*`（不新增色）；纹理一律**硬边平涂**（斑纹用扁平 fill，非柔光渐变）；二者均静态、与内容增长无关 → 不触发重排，不违反 §11①/§11③。

### 10.1 Homepage Hero 双栏撞色 + 酸性肖像

**意图**：hero 满铺撞色块——左栏 **2/3 电蓝紫**承载姓名/about-me，右栏 **1/3 酸性黄绿**承载肖像。落地 VIS §2「海报态度」、§10「孟菲斯活力」。

**版式（`index.astro` scoped）**：
- 全宽出血 `width:100vw; margin-left:calc(50% - 50vw)`，`grid-template-columns: var(--hero-split) 1fr`（`--hero-split:66.66%`），`gap:0`，`border-block: --bd-thick`。
- 背景 `linear-gradient(90deg, anchor 0 split, acid split 100%)`——**硬停色，无柔光**。接缝为 `.hero__media` 的 `border-left: --bd-thick`。
- 左栏文字全改 `--c-paper`（过 AA）；`--gutter` 把内容拉回正常页边距。
- 窄屏（≤880px）：纵向堆叠（蓝紫块上、黄绿块下），接缝转为 `border-top`。

**acid 配额代偿**：右栏满高 acid 是大量 acid，故**把 acid 从首页别处撤掉**——CV 入口卡 `accent="rose"`、about 段落不再用行内 acid 高亮，让 hero 成为全站**唯一** acid 高潮（强化「越少越响」）。

**酸性肖像 = 离线三层错位流水线**（采**做法 a 离线预处理成 PNG**，最可控、合 §9 构建时渲染；`scripts/process_portraits.py`）：
- **抠像（去背）**：`rembg` isnet-general-use 原始 mask + 逐图 **alpha levels boost**（`alpha_lo/alpha_hi`）——把模型低置信区域（如 ~0.3 alpha 的深色裙装）提到不透明，同时硬化发丝边缘消除暖色光晕。
- **三层叠合**（最初「白-黑灰度 + 白-粉灰度 + 点阵」配方的落地形态，改为**错位拼贴**以保留面部可读性）：
  - 顶层 = 白-黑灰度（居中，主图，**保面部可读**）；
  - 中层 = 点阵（`.mark-dots` 母题）**向右**微偏；
  - 底层 = 白-粉灰度**向左**微偏 → 左缘透出粉色幽灵、右缘透出点阵 = 错版印刷感。
- 产物 `public/images/portraitN-acid.png`（透明）。hero 用哪张是 `index.astro` 里一行 `heroPortrait`。
- **页面侧放大**：人像在 acid 栏内 `transform: scale(1.25)`（**视觉放大、不撑高栏**），`transform-origin: bottom left`，溢出由 `.hero__media` 的 `overflow:hidden` 裁掉——锚点固定在左下角接缝处。

### 10.2 卡片页撞色斑纹边栏

**意图**：`/projects`、`/more` 宽屏下中央阅读栏之外是大片空纸（"素"的主因）。中央纸色栏不动，**两侧边栏填撞色纹理**补能量。

**纹理形态（已定）**：**撞色不规则曲线斑纹**——`scripts/gen_blotches.py` 用 Catmull-Rom→bezier 生成有机色斑，调色板撞色平涂、硬边、种子可复现，输出 `public/textures/blotches.svg`。（早期试过「硬边竖条 + 黑线分隔」的彩虹条方案，弃用，因条状过规整、黑线磅重与中央栏冲突。）

**VIS 契合 / 风险**（**两项里唯一与 VIS 正面打架的**，VIS §3 警告大面积撞色「只剩噪声」）——按 §3「结构性压制」救活：
1. 纹理一律**硬边平涂**（扁平 fill，绝不软渐变）。
2. 中央 `.wrap-col` 给**不透明 `--c-paper` 底 + `--bd` 黑边**，明确**压在纹理之上**，阅读路径全留纸色中央（满足 §11③）。**不加硬位移阴影**——它与斑纹边栏不和谐，已去除。
3. 边栏静态、与内容无关 → 满足 §11①。
- 残留风险：边栏与卡片自身 accent 抢色 → 卡片更靠黑/锚色，或与当页默认 accent 错开。

**版式（`base.css` 的 `.texture-margins`）**：
```css
/* 满高 flex 外壳：让中央纸栏永远顶到 fold，纹理只留在两侧边栏（短页不溢色） */
.texture-margins { position: relative; display: flex; min-height: 100vh; }
.texture-margins::before {            /* 全宽固定纹理层，置于内容之下 */
  content: ""; position: fixed; inset: 0; z-index: -1;
  background: var(--c-paper) url("/textures/blotches.svg") center / cover no-repeat;
}
.texture-margins .wrap-col {          /* 中央栏压在纹理之上：纸底 + 黑边，加宽 */
  flex: 1 1 auto; max-width: 1080px; margin-inline: auto;
  background: var(--c-paper); border-inline: var(--bd); padding-block: var(--sp-8);
}
/* 加宽面板内再居中一条更窄的内容轨（标题 + 卡片），左右纸边对称；
   同时压掉 §4.2 章节标题的外偏（否则会探入纹理边栏） */
.texture-margins .section-header,
.texture-margins .card-list { max-width: var(--maxw-col); margin-inline: auto; }
```
模板侧：`projects.astro`/`more.astro` 页根包一层 `<div class="texture-margins">`。

### 10.3 资产再生与维护
- **换 hero 人像**：丢新的 `public/images/portraitN.jpg` → 在 `process_portraits.py` 的 `PORTRAITS` 加一项（按图调 `alpha_lo/alpha_hi`）→ `python scripts/process_portraits.py` → 改 `index.astro` 的 `heroPortrait`。
- **重洗斑纹**：调 `gen_blotches.py` 顶部的 `random.seed` / 层数 / 调色板 → `python scripts/gen_blotches.py` 覆盖 `blotches.svg`。
- 流水线依赖见 `scripts/requirements.txt`（Pillow + numpy + rembg + onnxruntime；模型缓存于 `~/.u2net/`，被墙时从 HuggingFace 镜像手取 `.onnx`）。
- 验收仍以 VIS §11 三条为准：若任一条不成立（尤其 §11③ 阅读受扰、或整页"只剩噪声"），回退该项。
