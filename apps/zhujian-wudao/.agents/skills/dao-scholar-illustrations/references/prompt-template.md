# 生图提示词模板

每张图单独生成。根据正文内容替换变量，不要把多张图拼在一起。

```text
Generate one standalone 16:9 horizontal Chinese philosophical article illustration.

Visual DNA:
Pure white background. Minimalist black hand-drawn line art. Lines have slight irregularity — like knife-etched characters on bamboo slips. Wobbly pen strokes, intentionally imperfect. Lots of empty white space (at least 40%). Sparse cinnabar-red and mineral-blue handwritten Chinese annotations. Clean, serene, contemplative aesthetic. No gradients, no shadows, no paper texture, no complex background, no commercial vector style, no PPT infographic look, no traditional Chinese painting (水墨/工笔), no CGI ancient Chinese fantasy, no Daoist religious symbols.

Recurring IP character required:
A minimalist hand-drawn ancient Chinese scholar in simple flowing robes. The scholar is a quiet, contemplative figure — not a historical person, not a Daoist priest, not a martial artist. Simple outline, often just a silhouette or a few brush strokes. Face is blank or has only a dot suggesting lowered eyes in contemplation. The scholar must participate in the core philosophical metaphor of the image — observing nature, writing on bamboo slips, sitting by water, walking between two states, untying a knot, letting go of a stone. The scholar is often small in the frame, dwarfed by nature, integrated into the scene. Make the scholar silent, still, present — not teaching, not pointing, not looking at the viewer.

Theme:
{正文配图主题}

Structure type:
{结构类型：Contemplation(观道) / Unbinding(解缚) / Dawning Clarity(微明) / Four Paths(四法) / Verification Chain(体道链) / Three Depths(三层递进) / Non-Action(自然无为) / Mysterious Sameness(玄同) / Practice-Without-Practice(行无行)}

Core idea:
{这张图要表达的哲学意味}

Composition:
{具体画面：学者在哪里、正在做什么、主要自然意象是什么、信息如何流动}

Suggested elements:
{自然意象1} / {自然意象2} / {自然意象3} / {自然意象4}

Chinese handwritten labels:
{标注词1} / {标注词2} / {标注词3} / {标注词4} / {可选标注词5}

Color use:
Black for main line art, scholar figure, bamboo slips, and object outlines. Cinnabar-red only for key concept highlights, main path arrows, or emphasis (max 3 spots). Mineral-blue only for secondary notes, feedback, or subtle states (max 3 spots). Red and blue never on the same object simultaneously.

Constraints:
One image explains only one core philosophical structure. Keep the main subject around 30%-50% of the canvas. Preserve at least 40% blank white space. Use at most 3-5 short handwritten Chinese labels (not sentences). Do not write a title in the top-left corner. Do not write the structure type on the image. Do not make it a formal diagram, course slide, or dense explainer. Do not use Daoist religious symbols (八卦/符箓/拂尘/丹炉). Do not draw specific historical figures. Do not copy prior examples or reuse known case compositions unless explicitly requested; invent a fresh visual metaphor rooted in nature imagery (water, mountain, cloud, stone, tree, valley, stream, bamboo, infant, vessel, wheel, door, window). It should be serene but not empty, profound but not pretentious, simple but not simple-minded.
```

## 图像编辑提示

去掉左上角标题：

```text
Edit the provided image. Remove only the handwritten title "{要删除的文字}" and its underline from the top-left corner. Fill that area with the same clean white background, matching the surrounding blank space. Preserve everything else exactly: scholar figure, labels, natural elements, line style, composition, aspect ratio, and image quality. Do not add any new text or objects.
```

增强哲思感：

```text
Regenerate this illustration with the same core philosophical meaning and simple layout, but make the scholar more central to the conceptual metaphor. The scholar should not be standing beside the diagram — they should be inside it, participating in the philosophical action. Add more empty space around the scholar. Keep it clean, sparse, hand-drawn, and contemplative. The scholar should feel small in the vastness of nature.
```
