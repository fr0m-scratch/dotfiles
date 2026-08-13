---
name: systems-paper-figure
description: Draw a top-tier-systems-paper-grade architecture figure as hand-laid SVG source (zone panels, numbered ①—⑧ data flow, trust boundary, mono protocol labels, honest failure/deny paths, bottom legend), render it to high-DPI PNG through headless Chrome, and run a MANDATORY render-inspect-fix loop before calling it done. Use when the user asks for 论文级 / 顶会 / system paper 风格的架构图, an architecture figure for a deck / 方案 / 教科书 / 白皮书 / PPT, 数据中台 · 数据底座 · 系统架构的 SVG 原图, 去 AI 味的架构图, 画一张像 OSDI/SOSP/SIGMOD/VLDB 论文里的图, 数据流图, 部署边界图, 状态机图, or asks to redraw a slide's diagram so it looks like a top engineering team made it. Output is `.svg` source + `.png`. NOT for self-contained HTML blueprint documents (use system-blueprint) and NOT for building the slide deck itself (use pptx).
---

# systems-paper-figure — 顶会 system paper 图语法的手排 SVG 架构图

Produce a figure a senior engineer would accept as coming from a team that writes and reads
top-tier systems papers. **The figure is hand-laid SVG source. There is no GUI tool, no mermaid,
no draw.io, no AI image generation.** Every coordinate is written by you and verified by
looking at the render.

This skill is the *style contract + the render loop + the traps*. It came out of the
上海电气交通自动化 数据底座 figures (`fig1`–`fig11`) and the Context Lake deck figures.

## Non-negotiables

**Never ship a figure you have not looked at.** Writing valid SVG proves nothing about
overlap, overflow, arrows through text, or an arrow pointing at the wrong box. The loop in
§Steps is not optional and is not satisfiable by reading your own source.

**Never invent content.** Numbers, system names, protocol names, percentages and capacities
come from the user, from a facts file, or from a public engineering fact. Anything else is
marked 示意 in the figure itself, verbatim.

**Never decorate.** No gradients, no shadows, no icons, no emoji, no rounded "card" aesthetics,
no color used as decoration. Every color carries one semantic and only one.

## 风格契约（逐条遵守，可整段粘进子代理提示词）

```
- SVG 根元素: <svg xmlns="http://www.w3.org/2000/svg" width="W" height="H" viewBox="0 0 W H"
  font-family="PingFang SC, Helvetica Neue, Arial, sans-serif">，白底 <rect fill="#FFFFFF"/>。
- 颜色（只许用这些）: ink #1D1D1F 标题 / body #3A3D42 / sub #55585E / faint #6E6E73 /
  hairline #C9CCD1 / 分区底 #F6F7F9 / 深一档 #EFF1F4 /
  强调 #0066CC（浅底 #F3F8FE · 深字 #0A55CC，只用于主路径或核心构件）/
  警示待确认 #9A4A16 / 拒绝红 #B5400C（仅"默认拒绝/失败路径"）/ 通过绿 #127A44（仅"校验通过"，节制）。
  禁止渐变、阴影、图标、emoji、装饰色。
- 字号: 组件标题 15px w600；正文行 11.5px；mono 10.5px（Menlo, monospace —— 协议名/键名/路径/
  指标名/接口名一律 mono）；分区标签 14.5px italic #55585E；小注 11px。
- 线: 组件框 stroke 1.1 #55585E，rx=2；分区框 stroke 1 #C9CCD1 rx=3 fill #F6F7F9；箭头 stroke 1.8–2；
  小三角 marker（viewBox 0 0 10 10, markerWidth 6.5, markerHeight 6.5, refX 8, refY 5,
  path M0,0 L10,5 L0,10 z, orient auto）。
  实线=数据/主路径；虚线 6 4=控制/回流/异步；虚线框=可选/待澄清/条件存在；虚线 9 5=信任边界。
- 圈号步骤: circle r=10 fill #1D1D1F（主路径蓝时 #0066CC），白字 11.5 bold，圆心压在箭头线上，
  编号 = 一条具体流程的时间顺序（不是"模块清单编号"）。
- 图例: 画布底部一行小样线 + 说明（只列实际用到的通道），不加"图例"标题框。
- 内容纪律: 只可使用给定的事实文本，禁止自行编造数字/系统名/百分比；要求标"示意"处必须原样标注。
  中文叙述、术语保留英文，分隔符用 ·。
- 布局纪律: 文字不得压框线、箭头不得穿文字、任何两元素间距 ≥8px；CJK 不留孤字。
  手排坐标，不许 transform 缩放文本。
```

## Canvas & scale

| 用途 | 画布 | 说明 |
|---|---|---|
| 独立论文级配图（方案 / 教科书 / 图解） | 宽 **1700–1860**，高按内容 | 实测用过 1860×852、1760×640、1700×560、1760×480 |
| 嵌进 16:9 幻灯片的图 | **1600×660** 固定 | 落到 8.38×3.46 in 不变形；同一 deck 内所有图同尺寸 |
| 目检渲染 | scale **2.2** | 够看清 10.5px mono，又不慢 |
| 印刷 / LaTeX 入书 | scale **4.8–5**（1860 → ~9000 px） | `\includegraphics{fig.png}` 用这一档 |

根元素必须显式写 `width=` 和 `height=`（渲染器按它们定尺）。

## Steps

1. **确定内容与事实来源。** 先拿到这张图要讲的那条具体流程（谁→谁→谁，中间哪一步会失败），
   以及可用的事实文本。缺事实就问，不要填空。一张图讲一条论证，不是模块罗列。

2. **选一个构图骨架**（见 §Composition patterns），把画布纵向切成 3–5 个 tier，
   横向切成对齐的列。**让相连的盒子对齐** —— 对齐了箭头才是水平或垂直直线，
   才不需要斜线、扇出、交叉、回环。

3. **手写 SVG。** 顶部 `<defs>` 放 marker + 一个 `<style>` 块，把字号字重收进两字母 class
   （`.bt` `.br` `.bs` `.mn` `.zl` `.num` `.lg`），正文只写 `<text class="bs" x= y=>`。
   坐标全部手算写死。参考 `EXAMPLE.svg`（本目录，一张完整可运行的成品）。

4. **渲染并亲眼看。**
   ```bash
   node "$HOME/.claude/skills/systems-paper-figure/svg2png.mjs" fig.svg fig.png 2.2
   ```
   然后 **用 Read 工具打开 fig.png**，逐项检查：文字溢出 / 压框线、箭头穿文字、
   箭头指向的盒子对不对、间距、对齐、图例完整、"示意"标注在位、CJK 孤字。

5. **放大复核密集区。** 全图缩略图会盖掉小缺陷。对每个密集区域：
   ```bash
   node "$HOME/.claude/skills/systems-paper-figure/zoom.mjs" fig.svg r1.png X Y W H 3
   ```
   X/Y/W/H 是 SVG 自身坐标。再 Read 一次。

6. **定点修改，不重写整张图。** 用 inline python 做字符串替换：
   ```bash
   python3 - <<'EOF'
   p='fig.svg'; s=open(p).read()
   s = s.replace('<path d="M200,580 L200,536"', '<path d="M325,580 L325,536"')
   open(p,'w').write(s)
   EOF
   ```
   改完 **必须重渲 + 重看**。

7. **至少两轮渲染-目检才算完成。** 第一轮必出缺陷；一轮就通过说明你没认真看。

8. **多图时并行。** 一图一个子代理，每个子代理拿到三样东西：上面那段风格契约原文、
   这张图逐字给定的事实内容、以及第 4–7 步的自检流程（明确写"必须 Read PNG"）。
   子代理返回最终 png 路径 + 一句话说明它修了什么。

9. **成品交付。** `.svg` 是源，`.png` 是产物，**永不手改 png**。改图 = 改 svg + 重渲。

## Composition patterns（实测有效）

- **信任边界 + 唯一出口** —— 虚线 9 5 框住内网，把网关画在边界上，外部服务用虚线框画在边界之外，
  一条线穿过边界。比写十行"安全说明"有力。
- **kernel bus** —— 所有人都要访问的那个东西（本体 / 元数据 / 目录）画成横贯全宽的一条带，
  上面是来源，下面是消费者。避免所有人都往中间画箭头造成扇出。
- **zone 列 + 编号 trace** —— 左到右分区，①—⑧ 追一次具体请求的时间顺序，编号写在箭头上，
  底部两行列出每一号在做什么。
- **control plane 底带** —— 血缘 / 权限审计 / 轨迹评测 / 版本回滚 单独一条底带，
  用虚线连上去。这是 data plane vs control plane 的论文语法。
- **诚实的失败支线** —— 至少画一条红色拒绝路径或一条被封死的路径。只画 happy path 的图不可信。
- **Delta Lake Fig 2 式目录布局** —— 左侧真实目录树（用 `├─ └─` 字符排版）+ 花括号分组 +
  细箭头 callout，右侧几个工程用途框。讲存储物理布局时用这个。
- **真 trace** —— 逐字 SQL、真键值、完整审计 JSON、含失败支线。比任何"能力清单"都值钱。

## Traps（每一条都真实付出过一轮代价）

1. **`<style>` 里的 class 会静默压过 `fill="..."` 属性。** 类选择器是 author stylesheet，
   优先级高于 presentation attribute。深色条上 `<text class="t" fill="#FFFFFF">` 会渲成类里的深色。
   要覆盖颜色就用 inline `style="fill:#FFFFFF"`，或者干脆给它一个专用 class。
2. **`sips --cropOffset` 是相对图片中心的，不是左上角。** 裁 PNG 看细节会静默给你错误区域。
   用本目录的 `zoom.mjs` 改 viewBox 重渲。
3. **裁 SVG 上边前，先找有没有比第一个 `<rect>` 更靠上的箭头 / marker。** 只按首个 rect 估裁剪线
   会切掉箭头三角。裁完必须渲染确认四边都不切。
4. **不要把标签居中放在一条边界线会穿过的窄间隙里。** 信任边界虚线是竖穿全高的，
   间隙中点上的任何文字都会被压。把该语义写进图例，别硬塞标签。
5. **编号箭头必须从真正执行那一步的盒子出发。** "人签后写回"的箭头画在"运营应用"上方，
   源码完全合法，但语义是错的 —— 只有目检能抓到。
6. **卡片底部留白。** 内容最后一行基线到框底留 16–20px 就够，留 30px 以上会显得空。
   写完先按"标题基线 = 框顶 + 28，每行 +22–24，框底 = 末行 + 18"配高度。
7. **箭头长度要留给圈号。** r=10 的圈号会吃掉 20px，箭头走廊短于 36px 就只剩两截残线。
   分层之间留 **44px** 走廊。
8. **pptxgenjs 3.12 嵌 SVG 会写一张坏的 Office 回退 PNG**（没装 sharp 时）。
   生成 pptx 后用 JSZip 拆包，把 `ppt/media/image-N-3.svg` 用 `rsvg-convert --width 3200`
   重渲替换掉 `image-N-2.png`。PowerPoint 吃 SVG，Keynote/旧 Office 吃修好的 PNG。
9. **pptxgenjs 的 `contain` 会把高受限的 SVG 缩得过小** —— 按 viewBox 纵横比显式定尺，别用 contain。

## 消费产物

- **LaTeX / 教科书**：渲 scale 4.8–5 出 PNG，`\includegraphics{/abs/path/fig.png}`。
- **pandoc → PDF 图解册**：把每张图配一节 markdown，`build.sh` 里 `pandoc --pdf-engine=xelatex`
  加 `-V CJKmainfont="Songti SC"`。
- **PPTX**：`pptxgenjs` 直接 `addImage` SVG（data URI），再按 Trap 8 修回退 PNG。

## 本目录文件

| 文件 | 作用 |
|---|---|
| `svg2png.mjs` | 零依赖 headless Chrome CDP 渲染器（Node ≥21 原生 WebSocket）。`node svg2png.mjs in.svg out.png [scale=3]` |
| `zoom.mjs` | 按 SVG 坐标高倍重渲一个矩形区域用于目检。`node zoom.mjs in.svg out.png X Y W H [scale=3]` |
| `EXAMPLE.svg` | 一张完整成品（AgentOS · AIP 架构图）：信任边界 + kernel bus + ①—⑧ trace + control plane 底带 + 拒绝路径 + 图例。抄它的结构。 |
