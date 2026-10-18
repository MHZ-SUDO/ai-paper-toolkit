# mh-防御性描述skill

找创新点和做实验时自动使用的 Codex skill。先认真发展研究想法，再用文献与实验识别可以成立的贡献，避免因已有相似工作或初期负结果而过早否定、过度收窄研究方向。

中文显示名：**mh-防御性描述skill**

系统标识：`mh-anti-defensive-description`

## 适用任务

- 找创新点、构思和发展 idea、选题与研究路线。
- 检查 novelty、比较最接近工作、判断贡献重合。
- 设计或调整实验、选择强基线与消融、组织机制验证。
- 分析结果、处理早期负结果、安排独立确认。
- 撰写摘要、引言、贡献和结果讨论中的研究价值论证。

普通翻译、日常文字修饰、排版和不含研究判断的代码操作不自动触发。

## 核心方法

“优先保留和发展”决定工作顺序，结论由证据决定。相似算法仍可能解决新的实质问题；新名称、更多模块或换一个应用标签也不自动形成创新。

创新性审查深入最接近工作的设定、机制和证据。只有摘要时给出有限范围的阶段判断；核心问题、机制与贡献确实高度重合时，明确停止不成立的 novelty 论证。

实验从科学问题与机制假设出发，使用公平强对照与关键消融。早期失败用于定位问题和形成新假设；后续用独立数据或场景确认。保留有意义的反证，避免为了获胜而弱化基线或选择有利结果。

## 安装与自动调用

将本目录完整放入 Codex 用户技能目录，保持文件夹名为 `mh-anti-defensive-description`。默认目录为 `~/.codex/skills/`；设置了 `CODEX_HOME` 时使用其下的 `skills/`。

也可在已安装 skill-installer 的 Codex 中输入：

```text
使用 skill-installer，从 MHZ-SUDO/ai-paper-toolkit 的
skills/mh-anti-defensive-description 安装这个 skill。
```

`agents/openai.yaml` 已设置 `allow_implicit_invocation: true`，描述字段提供上述任务的自动选择条件。客户端重新加载技能目录后生效；必要时新开聊天。可显式调用：

```text
$mh-anti-defensive-description 帮我发展这个 idea 的创新点，
比较最接近的工作，并设计能检验核心机制的实验。
```

希望在自己的全局 AGENTS.md 中强调这一偏好时，可添加：

```text
找创新点、检查 novelty、设计与分析实验、撰写研究贡献时，
默认使用 mh-anti-defensive-description，无需我提醒；
先发展实质贡献，再以文献与公平实验证据判断。
```

自动选择用于匹配相关任务，不代表每次对话都必须加载；也不自动授权训练、修改数据或对外发布。

## 文件

- [SKILL.md](SKILL.md)：自动触发范围、研究判断原则与工作流程。
- [agents/openai.yaml](agents/openai.yaml)：中文显示名与隐式调用配置。
- [references/novelty-review.md](references/novelty-review.md)：最接近工作、实质差异与撞车判断。
- [references/experiments.md](references/experiments.md)：科学问题、强对照、消融、探索与确认。

内容依据用户提供的“想 idea”和“检查 idea novelty”提示语及截图整理，并按用户要求扩展了创新点查找、实验设计与结果分析流程。截图中的其他产品界面、宣传与操作提示不属于本 skill 的指令。
