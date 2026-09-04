# 事实清单（R 阶段产物）

> 来源：三套简书连载博文集（2020 年前后旧教程）。
> - Notebook 1：matplotlib & pillow & networkx（nb/46194813）→ F-101~F-200
> - Notebook 2：开源的世界（nb/40234132）→ F-201~F-265
> - Notebook 3：无人驾驶（nb/47487870）→ F-301~F-363
> 零推测原则：所有条目仅陈述文章内容，不含推断性表述。

# 事实清单：notebook1-matplotlib-pillow-networkx（14 篇）

> 来源目录：`.trae/specs/classics-knowledge/jianshu-blogs-to-okf-wiki/raw/notebook1-matplotlib-pillow-networkx/`
> 时点统一标注：2020（各篇发布于 2020 年前后，隶属于连载《matplotlib & pillow & networkx 手册(停止维护)》）
> 编号范围：F-101 ~ F-200（共 100 条）

## 0099313fce96（画分形图的一个例子）

- **F-101**（来源：0099313fce96.md，https://www.jianshu.com/p/0099313fce96，时点：2020）：文章展示的代码导入 `random`、`numpy` 与 `matplotlib.pyplot` 三个模块。
- **F-102**（来源：0099313fce96.md，https://www.jianshu.com/p/0099313fce96，时点：2020）：代码设置三角形顶点坐标 `x = [1, 1.5, 2]`、`y = [1, 1+np.sqrt(.75), 1]`。
- **F-103**（来源：0099313fce96.md，https://www.jianshu.com/p/0099313fce96，时点：2020）：代码定义函数 `next_point(array, array2)`，函数体返回 `(array + array2) * .5`。
- **F-104**（来源：0099313fce96.md，https://www.jianshu.com/p/0099313fce96，时点：2020）：代码调用 `plt.figure(figsize=(10, 10))` 创建画布，用 `plt.scatter(x, y)` 与 `plt.scatter(rx, ry)` 绘制三角形顶点与初始随机点。
- **F-105**（来源：0099313fce96.md，https://www.jianshu.com/p/0099313fce96，时点：2020）：代码设置循环次数 `n = 100000`，循环内每次用 `random.choice(dirc)` 从顶点列表随机取一个顶点并计算新点，用 `plt.scatter(start[0], start[1], s=5)` 绘制，最后调用 `plt.savefig('ChaosGameTriangle'+str(n)+'.png')` 与 `plt.show()`。

## 3f4f28183885（2 使用 NetworkX 画神经网络）

- **F-106**（来源：3f4f28183885.md，https://www.jianshu.com/p/3f4f28183885，时点：2020）：文章指出神经网络是有向无环图（DAG），并使用 NetworkX 的有向图包处理。
- **F-107**（来源：3f4f28183885.md，https://www.jianshu.com/p/3f4f28183885，时点：2020）：文章定义 `DAGMeta` 基类，其 `__init__(self, layer_sizes, bbox=(.1, .1, .9, .9))` 接收 `layer_sizes` 与 `bbox` 两个参数。
- **F-108**（来源：3f4f28183885.md，https://www.jianshu.com/p/3f4f28183885，时点：2020）：`DAGMeta` 的属性 `x_spacing` 返回 `self.w/(len(self) - 1)`，`y_spacing` 返回 `self.h/max(self.layer_sizes)`。
- **F-109**（来源：3f4f28183885.md，https://www.jianshu.com/p/3f4f28183885，时点：2020）：`SlowlyDAG.plot()` 调用 `nx.DiGraph()` 创建有向图，并通过 `G.add_node(node_count, pos=(...))` 为节点添加位置属性。
- **F-110**（来源：3f4f28183885.md，https://www.jianshu.com/p/3f4f28183885，时点：2020）：`SlowlyDAG.plot()` 调用 `nx.draw(G, pos, node_color=range(node_count), with_labels=True, node_size=500, edge_color=[random.random() for i in range(len(G.edges))], width=2, font_color='black', cmap=plt.cm.Paired, edge_cmap=plt.cm.Blues)`。
- **F-111**（来源：3f4f28183885.md，https://www.jianshu.com/p/3f4f28183885，时点：2020）：`DAG` 类构造函数执行 `self._dag = nx.DiGraph(name=name)`，注释说明可通过 `self.name` 获取名称。
- **F-112**（来源：3f4f28183885.md，https://www.jianshu.com/p/3f4f28183885，时点：2020）：`DAG.plot()` 调用 `nx.get_node_attributes(self._dag, 'pos')` 获取节点位置，并依次调用 `nx.draw_networkx_nodes`、`nx.draw_networkx_edges`、`nx.draw_networkx_labels` 绘制。
- **F-113**（来源：3f4f28183885.md，https://www.jianshu.com/p/3f4f28183885，时点：2020）：文章展示调用实例 `self = DAG([5, 7, 5, 3, 2], bbox)`，其后调用 `plt.axis('off')` 与 `plt.show()`。

## 5b8489e1e4a8（NetworkX 画出简单路径）

- **F-114**（来源：5b8489e1e4a8.md，https://www.jianshu.com/p/5b8489e1e4a8，时点：2020）：文章使用 `G = nx.path_graph(4)` 创建路径图，并用 `nx.draw(G)` 绘制无向图路径。
- **F-115**（来源：5b8489e1e4a8.md，https://www.jianshu.com/p/5b8489e1e4a8，时点：2020）：文章使用 `G = nx.path_graph(4, create_using=nx.DiGraph())` 创建有向图路径。
- **F-116**（来源：5b8489e1e4a8.md，https://www.jianshu.com/p/5b8489e1e4a8，时点：2020）：水平布局代码使用 `pos = {node:(node, 0) for node in G}` 设置节点位置。
- **F-117**（来源：5b8489e1e4a8.md，https://www.jianshu.com/p/5b8489e1e4a8，时点：2020）：竖直布局代码使用 `pos = {node:(0, node) for node in G}` 设置节点位置。
- **F-118**（来源：5b8489e1e4a8.md，https://www.jianshu.com/p/5b8489e1e4a8，时点：2020）：修改节点样式代码调用 `nx.draw(G, pos=pos, node_color=ncolor, node_shape=nshape, node_size=nsize)`，其中 `ncolor = ['r', 'b', 'k', 'g']`、`nsize = [600, 400, 200, 100]`、`nshape = '>'`。
- **F-119**（来源：5b8489e1e4a8.md，https://www.jianshu.com/p/5b8489e1e4a8，时点：2020）：文章展示 `nx.draw(..., with_labels=True, font_color='w')` 修改标签字体颜色，并展示 `alpha=0.4` 设置节点透明度。

## 5c094689481e（Pillow 绘制图形）

- **F-120**（来源：5c094689481e.md，https://www.jianshu.com/p/5c094689481e，时点：2020）：文章指出使用 ImageDraw 模块绘制前需获取 `ImageDraw.Draw` 对象，代码为 `drawer = ImageDraw.Draw(im)`，并创建空白图片 `im = Image.new("RGB", (300, 300), "white")`。
- **F-121**（来源：5c094689481e.md，https://www.jianshu.com/p/5c094689481e，时点：2020）：文章介绍 `line(xy, fill=None, width=0, joint=None)` 方法，`xy` 为起点与终点坐标 (x1, y1, x2, y2)，示例 `drawer.line((50, 50, 150, 150), fill='green', width=2)`。
- **F-122**（来源：5c094689481e.md，https://www.jianshu.com/p/5c094689481e，时点：2020）：文章介绍 `rectangle(xy, fill=None, outline=None, width=0)`、`arc(xy, start, end, fill=None, width=0)`、`ellipse(xy, fill=None, outline=None, width=0)`、`chord(xy, start, end, fill=None, outline=None, width=0)`、`pieslice(xy, start, end, fill=None, outline=None, width=0)`、`polygon(xy, fill=None, outline=None)`、`point(xy, fill=None)` 等绘制方法。
- **F-123**（来源：5c094689481e.md，https://www.jianshu.com/p/5c094689481e，时点：2020）：文章展示 `text(...)` 方法签名，参数包括 `xy`、`text`、`fill`、`font`、`anchor`、`spacing=4`、`align='left'`、`direction`、`features`、`language`、`stroke_width=0`、`stroke_fill=None`。
- **F-124**（来源：5c094689481e.md，https://www.jianshu.com/p/5c094689481e，时点：2020）：文章指出绘制中文时默认编码不支持中文会报错，代码使用 `ImageFont.truetype('simkai.ttf', 30)` 获取字体对象。
- **F-125**（来源：5c094689481e.md，https://www.jianshu.com/p/5c094689481e，时点：2020）：文章使用 `ImageFont.truetype('simsun.ttc', 700)` 加载 .ttc 格式宋体字体绘制中文。
- **F-126**（来源：5c094689481e.md，https://www.jianshu.com/p/5c094689481e，时点：2020）：文章使用 `ttf.getsize(chars)` 得到整个字串的宽度和高度，并用 `img_draw.rectangle(coords, outline='blue')` 框选文字区域。
- **F-127**（来源：5c094689481e.md，https://www.jianshu.com/p/5c094689481e，时点：2020）：文章展示 `drawer.text((50, 100), text="t", font=imFont, fill="red", stroke_width=5, stroke_fill='yellow')` 设置文本笔画宽度与颜色。

## 610cd4f0b77e（使用 Pillow 处理图像）

- **F-128**（来源：610cd4f0b77e.md，https://www.jianshu.com/p/610cd4f0b77e，时点：2020）：文章使用 `Image.open('images/cat3.jpg')` 打开图片，指出打开成功返回 `Image` 对象，失败触发 `OSError` 异常。
- **F-129**（来源：610cd4f0b77e.md，https://www.jianshu.com/p/610cd4f0b77e，时点：2020）：文章展示通过 `im.format`、`im.size`、`im.mode`、`im.width`、`im.height`、`im.getpixel((100, 100))` 获取图像信息，输出示例为 format=JPEG、size=(474, 315)、mode=RGB、getpixel((100,100))=(193, 175, 113)。
- **F-130**（来源：610cd4f0b77e.md，https://www.jianshu.com/p/610cd4f0b77e，时点：2020）：文章指出 `save()` 保存文件时使用文件扩展名决定存储格式，`im.save(outfile, "JPEG")` 为显式指定格式的示例。
- **F-131**（来源：610cd4f0b77e.md，https://www.jianshu.com/p/610cd4f0b77e，时点：2020）：文章使用 `im.thumbnail(size)` 创建缩略图，`size = (128, 128)`。
- **F-132**（来源：610cd4f0b77e.md，https://www.jianshu.com/p/610cd4f0b77e，时点：2020）：文章使用 `region = im.crop(box)` 提取子矩形，区域由 (左, 上, 右, 下) 四元组定义，坐标左上角为 (0, 0)。
- **F-133**（来源：610cd4f0b77e.md，https://www.jianshu.com/p/610cd4f0b77e，时点：2020）：文章使用 `region.transpose(Image.ROTATE_180)` 与 `im.paste(region, box)` 处理并粘贴区域。
- **F-134**（来源：610cd4f0b77e.md，https://www.jianshu.com/p/610cd4f0b77e，时点：2020）：文章使用 `r, g, b = im.split()` 拆分频段、`Image.merge("RGB", (b, g, r))` 合并频段。
- **F-135**（来源：610cd4f0b77e.md，https://www.jianshu.com/p/610cd4f0b77e，时点：2020）：文章使用 `im.resize((128, 128))` 调整大小、`im.rotate(45)` 旋转图像，指出 rotate 参数为逆时针角度；并展示 `im.transpose(Image.FLIP_LEFT_RIGHT)`、`Image.FLIP_TOP_BOTTOM`、`Image.ROTATE_90`、`Image.ROTATE_180`、`Image.ROTATE_270` 等转置操作。
- **F-136**（来源：610cd4f0b77e.md，https://www.jianshu.com/p/610cd4f0b77e，时点：2020）：文章使用 `im.convert("L")` 转换模式，指出库支持每种受支持模式与 "L" 和 "RGB" 模式之间的转换。
- **F-137**（来源：610cd4f0b77e.md，https://www.jianshu.com/p/610cd4f0b77e，时点：2020）：文章使用 `im.filter(ImageFilter.DETAIL)` 应用滤波器，列出 BLUR、CONTOUR、DETAIL、EDGE_ENHANCE、EDGE_ENHANCE_MORE、EMBOSS、FIND_EDGES、SMOOTH、GaussianBlur 等滤镜。
- **F-138**（来源：610cd4f0b77e.md，https://www.jianshu.com/p/610cd4f0b77e，时点：2020）：文章使用 `im.point(lambda i: i * 1.2)` 对每个像素应用函数变换，并使用 `ImageEnhance.Contrast(im)` 创建调整器后调用 `enh.enhance(1.3)`。
- **F-139**（来源：610cd4f0b77e.md，https://www.jianshu.com/p/610cd4f0b77e，时点：2020）：文章使用 `im.seek(1)`、`im.seek(im.tell()+1)` 读取动画序列帧，指出序列结束时触发 `EOFError` 异常，并使用 `ImageSequence.Iterator(im)` 遍历序列。
- **F-140**（来源：610cd4f0b77e.md，https://www.jianshu.com/p/610cd4f0b77e，时点：2020）：文章使用 `im.draft("L", (100, 100))` 控制解码器，指出该方法仅适用于 JPEG 和 MPO 文件。

## 669212a8b6e6（matplotlib 初识）

- **F-141**（来源：669212a8b6e6.md，https://www.jianshu.com/p/669212a8b6e6，时点：2020）：文章指出 `plt.gcf()` 与 `plt.gca()` 分别表示 "Get Current Figure" 与 "Get Current Axes"，`plt.plot()` 通过 `plt.gca()` 获得当前 Axes 后调用 `ax.plot()`。
- **F-142**（来源：669212a8b6e6.md，https://www.jianshu.com/p/669212a8b6e6，时点：2020）：横向柱状图代码调用 `plt.barh(y_pos, performance, xerr=error, align='center', alpha=0.4)`，并调用 `plt.yticks(y_pos, people)`、`plt.xlabel('Performance')`、`plt.title('How efficient do you want to go today?')`、`plt.savefig("barh.png", format="png")`。
- **F-143**（来源：669212a8b6e6.md，https://www.jianshu.com/p/669212a8b6e6，时点：2020）：文章指出 `plt.rcdefaults()` 表示恢复 rc 的默认设置，纵向柱状图使用 `plt.bar(y_pos, performance, xerr=error, align='center', alpha=0.4)`。
- **F-144**（来源：669212a8b6e6.md，https://www.jianshu.com/p/669212a8b6e6，时点：2020）：叠加条形图代码设置 `bar_width = 0.3`，调用 `plt.bar(x, Bj, bar_width)` 与 `plt.bar(x, Sh, bar_width, bottom=Bj)`。
- **F-145**（来源：669212a8b6e6.md，https://www.jianshu.com/p/669212a8b6e6，时点：2020）：图像填充代码调用 `plt.fill(x, y, 'c')` 与 `plt.grid(True)`；多函数填充调用 `plt.fill(x, y1, 'b', x, y2, 'c', alpha=0.7)`，文章指出 `alpha` 为 0 表示全透明、1 表示完全不透明。
- **F-146**（来源：669212a8b6e6.md，https://www.jianshu.com/p/669212a8b6e6，时点：2020）：文章列出绘图函数表，包含 `bar()`、`barh()`、`hist()`、`hist2d()`、`pie()`、`plot()`、`scatter()`、`fill()`、`hexbin()`、`quiver()`、`streamplot()`、`boxplot()` 等；并列出操作类函数表，包含 `axhline()`、`axvline()`、`grid()`、`legend()`、`subplot()`、`subplots()`、`title()`、`xlabel()`、`ylabel()`、`xlim()`、`ylim()`、`xticks()`、`yticks()` 等。

## 70af8dde0705（1 画出神经网络结构）

- **F-147**（来源：70af8dde0705.md，https://www.jianshu.com/p/70af8dde0705，时点：2020）：文章包含绘制卷积神经网络结构的代码，导入 `matplotlib.pyplot`、`matplotlib.lines.Line2D`、`matplotlib.patches.Rectangle`、`matplotlib.collections.PatchCollection` 等模块。
- **F-148**（来源：70af8dde0705.md，https://www.jianshu.com/p/70af8dde0705，时点：2020）：代码定义常量 `NumConvMax = 8`、`NumFcMax = 20` 以及 `White = 1.`、`Light = 0.7`、`Medium = 0.5`、`Dark = 0.3`、`Black = 0.` 灰度值。
- **F-149**（来源：70af8dde0705.md，https://www.jianshu.com/p/70af8dde0705，时点：2020）：代码定义 `add_layer(patches, colors, size=24, num=5, top_left=[0, 0], loc_diff=[3, -3])` 函数，内部调用 `Rectangle(loc_start + ind * loc_diff, size, size)` 添加矩形。
- **F-150**（来源：70af8dde0705.md，https://www.jianshu.com/p/70af8dde0705，时点：2020）：代码定义 `add_mapping(patches, colors, start_ratio, patch_size, ind_bgn, top_left_list, loc_diff_list, num_show_list, size_list)` 函数，内部使用 `Rectangle` 与 `Line2D` 添加映射块与连线。
- **F-151**（来源：70af8dde0705.md，https://www.jianshu.com/p/70af8dde0705，时点：2020）：代码中卷积层使用 `size_list = [32, 18, 10, 6, 4]`、`num_list = [3, 32, 32, 48, 48]`，全连接层使用 `size_list = [fc_unit_size, fc_unit_size, fc_unit_size]`、`num_list = [768, 500, 2]`。
- **F-152**（来源：70af8dde0705.md，https://www.jianshu.com/p/70af8dde0705，时点：2020）：代码使用 `PatchCollection(patches, cmap=plt.cm.gray)`、`collection.set_array(np.array(colors))`、`ax.add_collection(collection)` 添加图形集合，并以 `fig.savefig(os.path.join(fig_dir, 'convnet_fig' + fig_ext), bbox_inches='tight', pad_inches=0)` 保存图像。
- **F-153**（来源：70af8dde0705.md，https://www.jianshu.com/p/70af8dde0705，时点：2020）：文章注明该代码"暂时还未研究，先放这，以后有时间再研究"。

## 8d5ff4ce2052（Pillow 之图像的缩放与合成）

- **F-154**（来源：8d5ff4ce2052.md，https://www.jianshu.com/p/8d5ff4ce2052，时点：2020）：文章指出通过 `Image.new(mode, size, color)` 创建图像，三个参数分别为 mode、size（width, height）、color。
- **F-155**（来源：8d5ff4ce2052.md，https://www.jianshu.com/p/8d5ff4ce2052，时点：2020）：示例 `im = Image.new('RGB', (100, 100), 'red')`、`im.save('red.png')`。
- **F-156**（来源：8d5ff4ce2052.md，https://www.jianshu.com/p/8d5ff4ce2052，时点：2020）：文章介绍 `Image.blend(im1, im2, alpha)` 透明度混合，`alpha` 为 0 时显示 im1、为 1 时显示 im2，并要求 im1 与 im2 大小相同且 mode 均为 RGB。
- **F-157**（来源：8d5ff4ce2052.md，https://www.jianshu.com/p/8d5ff4ce2052，时点：2020）：文章介绍 `Image.composite(im1, im2, mask)` 遮罩混合，三个参数均为 Image 对象，示例 `im3 = Image.composite(im1, im2, b)`。
- **F-158**（来源：8d5ff4ce2052.md，https://www.jianshu.com/p/8d5ff4ce2052，时点：2020）：文章使用 `Image.eval(im, lambda x:x*2)` 对每个像素点进行函数操作。
- **F-159**（来源：8d5ff4ce2052.md，https://www.jianshu.com/p/8d5ff4ce2052，时点：2020）：文章使用 `im2.thumbnail((100, 100))` 按尺寸缩放，示例输出 `im1的大小 (474, 315)`、`im2的大小 (100, 66)`。
- **F-160**（来源：8d5ff4ce2052.md，https://www.jianshu.com/p/8d5ff4ce2052，时点：2020）：文章介绍 `ImageChops.add(image1, image2, scale=1.0, offset=0)` 与 `ImageChops.subtract(image1, image2, scale=1.0, offset=0)` 运算。
- **F-161**（来源：8d5ff4ce2052.md，https://www.jianshu.com/p/8d5ff4ce2052，时点：2020）：文章列出 ImageChops 的 darker、lighter、invert、multiply、screen、difference 函数及各自计算公式：darker 为 `min(im1, im2)`、lighter 为 `max(im1, im2)`、invert 为 `max-image`、multiply 为 `im1*im2/max`、screen 为 `max-((max-im1)*(max-im2)/max)`、difference 为 `abs(im1-im2)`。

## 9048dc53e33a（Matplotlib 事件处理）

- **F-162**（来源：9048dc53e33a.md，https://www.jianshu.com/p/9048dc53e33a，时点：2020）：文章指出 matplotlib 使用 wxpython、tkinter、qt4、gtk 和 macosx 等用户界面工具包，事件处理 API 基于 GTK 模型。
- **F-163**（来源：9048dc53e33a.md，https://www.jianshu.com/p/9048dc53e33a，时点：2020）：示例代码调用 `fig.canvas.mpl_connect('button_press_event', onclick)` 连接回调，文章指出 `mpl_connect()` 返回连接 id（整数），并通过 `fig.canvas.mpl_disconnect(cid)` 断开。
- **F-164**（来源：9048dc53e33a.md，https://www.jianshu.com/p/9048dc53e33a，时点：2020）：文章列出可连接事件名，包括 'button_press_event'、'button_release_event'、'close_event'、'draw_event'、'key_press_event'、'key_release_event'、'motion_notify_event'、'pick_event'、'resize_event'、'scroll_event'、'figure_enter_event'、'figure_leave_event'、'axes_enter_event'、'axes_leave_event'。
- **F-165**（来源：9048dc53e33a.md，https://www.jianshu.com/p/9048dc53e33a，时点：2020）：文章指出所有 matplotlib 事件继承自 `matplotlib.backend_bases.Event`，储存 `name`、`canvas`、`guiEvent` 属性。
- **F-166**（来源：9048dc53e33a.md，https://www.jianshu.com/p/9048dc53e33a，时点：2020）：文章指出 `KeyEvent` 和 `MouseEvent` 派生自 `LocationEvent`，具有 `x`、`y`、`inaxes`、`xdata`、`ydata` 属性；`MouseEvent` 的 `button` 属性取值 `None`、`1`、`2`、`3`、`'up'`、`'down'`（文章注明后两者对应滚动事件）。
- **F-167**（来源：9048dc53e33a.md，https://www.jianshu.com/p/9048dc53e33a，时点：2020）：文章展示 DraggableRectangle 可拖拽矩形类，`connect()` 中分别连接 'button_press_event'、'button_release_event'、'motion_notify_event' 三个事件，`on_press` 中调用 `self.rect.contains(event)` 检测命中，`on_motion` 中调用 `self.rect.set_x(x0+dx)`、`self.rect.set_y(y0+dy)`。
- **F-168**（来源：9048dc53e33a.md，https://www.jianshu.com/p/9048dc53e33a，时点：2020）：文章展示鼠标进入/离开示例，连接 'figure_enter_event'、'figure_leave_event'、'axes_enter_event'、'axes_leave_event'，回调中调用 `event.inaxes.patch.set_facecolor('yellow')` 等改变背景色。
- **F-169**（来源：9048dc53e33a.md，https://www.jianshu.com/p/9048dc53e33a，时点：2020）：文章指出通过设置 Artist 的 `picker` 属性启用对象拾取，`picker` 可为 `None`、boolean、float（点的 epsilon 容差）、function（签名 `hit, props = picker(artist, mouseevent)`）；拾取示例中 `line, = ax.plot(np.random.rand(100), 'o', picker=5)`，`onpick` 回调读取 `event.artist` 与 `event.ind`，通过 `fig.canvas.mpl_connect('pick_event', onpick)` 连接。

## a30a6e07102b（Pillow 模拟图像的手绘和石雕、油画效果）

- **F-170**（来源：a30a6e07102b.md，https://www.jianshu.com/p/a30a6e07102b，时点：2020）：文章描述手绘效果特征为黑白灰色、边界线条较重、相同或相近色彩趋于白色、略有光源效果。
- **F-171**（来源：a30a6e07102b.md，https://www.jianshu.com/p/a30a6e07102b，时点：2020）：手绘代码使用 `im.convert('L')` 转为灰度图，`grad_x, grad_y = np.gradient(gray)` 取灰度梯度值，`depth = 10.` 预设深度，梯度值乘以 `depth/100.`。
- **F-172**（来源：a30a6e07102b.md，https://www.jianshu.com/p/a30a6e07102b，时点：2020）：手绘代码设置光源参数 `vec_el = np.pi/2.2`、`vec_ez = np.pi/4`，`dx = np.cos(vec_el)*np.cos(vec_ez)`、`dy = np.cos(vec_el)*np.sin(vec_ez)`、`dz = np.sin(vec_el)`。
- **F-173**（来源：a30a6e07102b.md，https://www.jianshu.com/p/a30a6e07102b，时点：2020）：手绘代码做梯度归一化 `A = np.sqrt(grad_x**2+grad_y**2+1.)`、`uni_x = grad_x/A`、`uni_y = grad_y/A`、`uni_z = 1./A`。
- **F-174**（来源：a30a6e07102b.md，https://www.jianshu.com/p/a30a6e07102b，时点：2020）：手绘代码计算 `e = 255*(dx*uni_x + dy*uni_y + dz*uni_z)`，执行 `e = e.clip(0, 255)`，用 `Image.fromarray(e.astype('uint8'))` 重构图像并 `im.save("e.png")`。
- **F-175**（来源：a30a6e07102b.md，https://www.jianshu.com/p/a30a6e07102b，时点：2020）：石雕/油画代码使用 `grad_x, grad_y, grad_z = np.gradient(im)` 对 RGB 三通道取梯度，归一化使用 `A = np.sqrt(grad_x**2+grad_y**2+grad_z**2) + 1e-7`，光源参数 `vec_el = np.pi/7.2`、`vec_ez = np.pi/7`。
- **F-176**（来源：a30a6e07102b.md，https://www.jianshu.com/p/a30a6e07102b，时点：2020）：文章展示修改光源影响因素的代码：`dx = 2**(np.cos(vec_el)*np.cos(vec_ez))`、`dy = np.exp(np.cos(vec_el))*np.sin(vec_ez)`、`dz = np.log(np.sin(vec_el))`。

## ade5973613ce（matplotlib 入门）

- **F-177**（来源：ade5973613ce.md，https://www.jianshu.com/p/ade5973613ce，时点：2020）：基础代码使用 `fig, ax = plt.subplots()` 创建 figure 与 axes，`ax.plot([1, 2, 3, 4], [1, 4, 2, 3])` 绘图，文章指出也可简化为 `plt.plot([1, 2, 3, 4], [1, 4, 2, 3])`。
- **F-178**（来源：ade5973613ce.md，https://www.jianshu.com/p/ade5973613ce，时点：2020）：文章指出 matplotlib 基本组件包括 `Figure`、`Axes`、`Axis`、`Artist`。
- **F-179**（来源：ade5973613ce.md，https://www.jianshu.com/p/ade5973613ce，时点：2020）：文章展示创建 figure 的三种方式：`plt.figure()`（空 Figure）、`fig, ax = plt.subplots()`（单 Axes）、`fig, axes = plt.subplots(2, 2)`（2x2 Axes 网格）。
- **F-180**（来源：ade5973613ce.md，https://www.jianshu.com/p/ade5973613ce，时点：2020）：文章指出 `Axes` 包含两个（3D 情况下为三个）`Axis` 对象，可使用 `axes.Axes.set_xlim()`、`axes.Axes.set_ylim()`、`set_xlabel()`、`set_ylabel()`、`set_title()`。
- **F-181**（来源：ade5973613ce.md，https://www.jianshu.com/p/ade5973613ce，时点：2020）：文章指出 `Axis` 有 `Locator` 与 `Formatter` 两个子对象，分别控制刻度位置与显示数值。
- **F-182**（来源：ade5973613ce.md，https://www.jianshu.com/p/ade5973613ce，时点：2020）：面向对象绘图示例调用 `ax.plot(x, x, label='linear')`、`ax.set_xlabel('x label')`、`ax.set_ylabel('y label')`、`ax.set_title("Simple Plot")`、`ax.legend()`；pyplot 绘图示例调用 `plt.plot(...)`、`plt.xlabel('x label')`、`plt.ylabel('y label')`、`plt.title("Simple Plot")`、`plt.legend()`。
- **F-183**（来源：ade5973613ce.md，https://www.jianshu.com/p/ade5973613ce，时点：2020）：文章指出后端分为用户界面后端（pygtk、wxpython、tkinter、qt4、macosx）与硬拷贝后端（PNG、SVG、PDF、PS），识别后端有 3 种方式：`rcParams["backend"]`（默认 'agg'）、`MPLBACKEND` 环境变量、`matplotlib.use()` 函数。

## d52132ab9ccc（matplotlib 之形状与路径：patches和path）

- **F-184**（来源：d52132ab9ccc.md，https://www.jianshu.com/p/d52132ab9ccc，时点：2020）：文章指出形状指 `matplotlib.patches` 包中的对象（如箭头、正方形、椭圆），路径指 `matplotlib.path` 中实现的功能。
- **F-185**（来源：d52132ab9ccc.md，https://www.jianshu.com/p/d52132ab9ccc，时点：2020）：文章使用 `patches.Ellipse((xcenter, ycenter), width, height, angle=angle, linewidth=2, fill=False, zorder=2)` 创建椭圆，并指出 `patches.Arc` 等价，因为 `Arc` 继承自 `Ellipse` 类。
- **F-186**（来源：d52132ab9ccc.md，https://www.jianshu.com/p/d52132ab9ccc，时点：2020）：文章指出 `plt` 只实现了 `Rectangle`、`Circle`、`Polygon` 三个常用图形，更复杂的图形使用 `patches` 模块。
- **F-187**（来源：d52132ab9ccc.md，https://www.jianshu.com/p/d52132ab9ccc，时点：2020）：文章展示用 `ax.add_patch(e1)` 添加单个 patch，或用 `PatchCollection(patches)` 构造集合后 `ax.add_collection(collection)` 添加集合。
- **F-188**（来源：d52132ab9ccc.md，https://www.jianshu.com/p/d52132ab9ccc，时点：2020）：形状示例代码创建 `mpatches.Circle`、`mpatches.Rectangle`、`mpatches.Wedge`、`mpatches.RegularPolygon`、`mpatches.Ellipse`、`mpatches.Arrow`、`mpatches.PathPatch`、`mpatches.FancyBboxPatch`、`mlines.Line2D` 等对象，其中 `mpatches.Wedge(grid[2], 0.1, 30, 270, ec="none")`。
- **F-189**（来源：d52132ab9ccc.md，https://www.jianshu.com/p/d52132ab9ccc，时点：2020）：路径代码使用 `Path(verts, codes)` 创建路径对象，示例 codes 为 `[Path.MOVETO, Path.LINETO, Path.LINETO, Path.LINETO, Path.CLOSEPOLY]`，并通过 `patches.PathPatch(path, facecolor='orange', lw=2)` 与 `ax.add_patch(patch)` 绘制。
- **F-190**（来源：d52132ab9ccc.md，https://www.jianshu.com/p/d52132ab9ccc，时点：2020）：文章给出 `Path` 类定义 `Path(vertices, codes=None, _interpolation_steps=1, closed=False, readonly=False)`，并说明 codes 取值含义：`MOVETO` 移动钢笔到给定顶点（起始点）、`LINETO` 绘制直线到给定顶点、`CURVE3` 绘制二次贝塞尔曲线、`CURVE4` 绘制三次贝塞尔曲线、`CLOSEPOLY` 绘制线段到当前折线起始点、`STOP` 为整个路径末尾标记。
- **F-191**（来源：d52132ab9ccc.md，https://www.jianshu.com/p/d52132ab9ccc，时点：2020）：条形图路径代码使用 `np.random.seed(19680801)` 固定随机数种子、`np.histogram(data, 100)` 计算直方图，构造条形图顶点与 codes 后通过 `patches.PathPatch(barpath, facecolor='green', edgecolor='yellow', alpha=0.5)` 绘制。

## f687c1aecfcc（NetworkX 中的节点与边）

- **F-192**（来源：f687c1aecfcc.md，https://www.jianshu.com/p/f687c1aecfcc，时点：2020）：文章指出节点可以是任何可哈希的 Python 对象（`None` 除外），边可以是使用 `G.add_edge(n1, n2, object=x)` 创建联系的任何对象 x。
- **F-193**（来源：f687c1aecfcc.md，https://www.jianshu.com/p/f687c1aecfcc，时点：2020）：文章提到 `convert_node_labels_to_integers()` 函数可得到整数标签的图。
- **F-194**（来源：f687c1aecfcc.md，https://www.jianshu.com/p/f687c1aecfcc，时点：2020）：示例创建空图 `G = nx.Graph()`，调用 `G.add_edge(1, 2, length = 10)`、`G.add_edge(1, 3, weight = 20)`、`G.add_edge(2, 3, capacity = 15)` 为边添加属性，并用 `nx.draw(G)` 画图。
- **F-195**（来源：f687c1aecfcc.md，https://www.jianshu.com/p/f687c1aecfcc，时点：2020）：文章展示 `G[1][3]['color'] = 'red'`，并注明等价于 `G[1][3].update({'color': 'red'})`；还展示 `G.add_edges_from([(3, 4), (4, 5)], color='red')`、`G.add_edges_from([(1, 2, {'color': 'blue'}), (2, 3, {'weight': 8})])`、`G.edges[3, 4]['weight'] = 4.2` 等边属性操作。
- **F-196**（来源：f687c1aecfcc.md，https://www.jianshu.com/p/f687c1aecfcc，时点：2020）：文章展示 `G = nx.Graph(day='Friday')` 创建带属性的图，`G.graph` 显示为 `{'day': 'Friday'}`；也可用 `G.graph['day'] = 'Friday'` 添加属性。
- **F-197**（来源：f687c1aecfcc.md，https://www.jianshu.com/p/f687c1aecfcc，时点：2020）：文章展示 `G.add_node(1, time='5pm')`、`G.add_nodes_from([3], time='2pm')`、`G.nodes[1]['room'] = 714` 等节点属性操作，`G.nodes.data()` 返回 `NodeDataView`。

## f6b0a43023b3（Pillow 模拟电子显示屏）

- **F-198**（来源：f6b0a43023b3.md，https://www.jianshu.com/p/f6b0a43023b3，时点：2020）：代码定义 `gen_text()` 函数，使用 `Image.open('70.png')` 打开图片，`ImageDraw.Draw(im)` 创建绘图对象。
- **F-199**（来源：f6b0a43023b3.md，https://www.jianshu.com/p/f6b0a43023b3，时点：2020）：代码读取 `W, H = im.size`，设置 `spacing = 20`，计算 `row, colum = int(W / spacing), int(H / spacing)`。
- **F-200**（来源：f6b0a43023b3.md，https://www.jianshu.com/p/f6b0a43023b3，时点：2020）：代码嵌套循环调用 `img_draw.rectangle([i*spacing, j*spacing, (1+i)*spacing, (1+j)*spacing], outline='gray', width=2)` 绘制网格，并以 `im.save('d.png')` 保存图像。


<!--
编号事实清单：notebook2-opensource（开源的世界·Git/GitHub/开源实践）
来源目录：.trae/specs/classics-knowledge/jianshu-blogs-to-okf-wiki/raw/notebook2-opensource/
共 10 篇，编号 F-201 ~ F-265，合计 65 条。
说明：9e81e3ca89a8.md 为部分抓取，其事实仅基于已抓取内容。
-->

# notebook2 编号事实清单（F-201 ~ F-265）

## 161b4241bc09.md《5 GitHub Actions 手册》

- **F-201**（来源：161b4241bc09.md，https://www.jianshu.com/p/161b4241bc09，时点：2020）：文章标题为《5 GitHub Actions 手册》，作者为"水之心"，属于简书连载《开源的世界》（https://www.jianshu.com/nb/40234132）。
- **F-202**（来源：161b4241bc09.md，https://www.jianshu.com/p/161b4241bc09，时点：2020）：文章开篇列出学习资源，包括 GitHub 帮助（help.github.com/cn）、关于自述文件、忽略文件、github.com/actions 组织及其 starter-workflows 仓库、sdras 的 awesome-actions 仓库。
- **F-203**（来源：161b4241bc09.md，https://www.jianshu.com/p/161b4241bc09，时点：2020）：文章介绍了 GitHub Actions 的核心概念 Workflow、Workflow run、Workflow file、Job、Step、Action、CI、CD、Virtual environment、Runner、Event、Artifact，其中 Workflow file 是位于 GitHub 仓库根目录 `.github/workflows` 位置的 YAML 文件。
- **F-204**（来源：161b4241bc09.md，https://www.jianshu.com/p/161b4241bc09，时点：2020）：文章说明工作流程必须存储在仓库根目录的 `.github/workflows` 目录中，至少包含一项作业，作业包含一组用于执行个别任务的步骤。
- **F-205**（来源：161b4241bc09.md，https://www.jianshu.com/p/161b4241bc09，时点：2020）：文章给出通过事件触发工作流程的 YAML 示例：在工作流程名称后添加 `on: push`，并说明 `on` 字段可以是事件数组，如 `on: [push, pull_request]`。
- **F-206**（来源：161b4241bc09.md，https://www.jianshu.com/p/161b4241bc09，时点：2020）：文章展示用 POSIX cron 语法计划工作流程运行的示例，如 `on: schedule: - cron: '0 * * * *'`（每小时触发一次）和 `- cron: "0 2 * * 1-5"`（周一至周五 2:00 UTC）。
- **F-207**（来源：161b4241bc09.md，https://www.jianshu.com/p/161b4241bc09，时点：2020）：文章展示将工作流程限定在特定分支运行的示例 `on: push: branches: - master`，并说明可选的 `paths` 字段（如 `test/*`）可限定事件考虑的文件路径。
- **F-208**（来源：161b4241bc09.md，https://www.jianshu.com/p/161b4241bc09，时点：2020）：文章给出选择虚拟环境的示例 `runs-on: ubuntu-18.04`，说明可以选择 Ubuntu、Linux 和 macOS 等不同类型和版本的虚拟主机。
- **F-209**（来源：161b4241bc09.md，https://www.jianshu.com/p/161b4241bc09，时点：2020）：文章展示配置构建矩阵的示例：`strategy: matrix: node: [6, 8, 10] os: [ubuntu-14.04, ubuntu-18.04]`，说明矩阵配置写在 `strategy:` 下。
- **F-210**（来源：161b4241bc09.md，https://www.jianshu.com/p/161b4241bc09，时点：2020）：文章展示使用检出操作 `- uses: actions/checkout@v1` 及浅层克隆设置 `with: fetch-depth: 1`，并给出引用公共仓库操作的语法 `{owner}/{repo}@{ref}`、同一仓库操作的 `./path/to/dir` 语法与引用 Docker Hub 容器的 `docker://{image}:{tag}` 语法。
- **F-211**（来源：161b4241bc09.md，https://www.jianshu.com/p/161b4241bc09，时点：2020）：文章说明 `jobs` 字段是 workflow 文件的主体，示例中 `job2` 通过 `needs: job1` 依赖 job1，`job3` 通过 `needs: [job1, job2]` 等待前两者完成。
- **F-212**（来源：161b4241bc09.md，https://www.jianshu.com/p/161b4241bc09，时点：2020）：文章给出状态徽章的 URL 格式 `https://github.com/<OWNER>/<REPOSITORY>/workflows/<WORKFLOW_NAME>/badge.svg`，说明常见添加位置是仓库的 README.md，也可用 branch 和 event 查询参数显示特定分支或事件的状态。

## 1a4c45c12dee.md《2.1 Git 学习笔记》

- **F-213**（来源：1a4c45c12dee.md，https://www.jianshu.com/p/1a4c45c12dee，时点：2020）：文章标题为《2.1 Git 学习笔记》，作者为"水之心"，属于连载《开源的世界》。
- **F-214**（来源：1a4c45c12dee.md，https://www.jianshu.com/p/1a4c45c12dee，时点：2020）：文章列出 Git 学习资源，包括《图解 Git》（marklodato.github.io）、Git 图解常用命令和廖雪峰教程笔记总结、《Git Rebase原理以及黄金准则详解》、Git 的原理简介和常用命令、《图解git原理与日常实用指南》、ssh-agent 使用指南、Git 远程操作详解（阮一峰）、《标签管理》（廖雪峰）。
- **F-215**（来源：1a4c45c12dee.md，https://www.jianshu.com/p/1a4c45c12dee，时点：2020）：文章给出的 gitk 中文乱码问题处理命令是 `git config --global gui.encoding utf-8`。
- **F-216**（来源：1a4c45c12dee.md，https://www.jianshu.com/p/1a4c45c12dee，时点：2020）：文章转载《GIT分支管理是一门艺术》（英文原文 http://www.nvie.com/posts/a-successful-git-branching-model/），文中建议一个中心版本库（origin）至少包括"主分支(master)"和"开发分支(develop)"两个分支，并说明从 master 获得的代码处于可发布状态、从 develop 能获得最新开发进展的代码。
- **F-217**（来源：1a4c45c12dee.md，https://www.jianshu.com/p/1a4c45c12dee，时点：2020）：文章介绍"辅助分支"概念，包括 Feature branches（起源于 develop、最终归于 develop）、Release branches（起源于 develop、归于 develop 或 master，命名 `release-*`）、Hotfix branches（源于 master、归于 develop 或 master，命名 `hotfix-*`），并说明辅助分支生命周期有限、完成后即可被清除。
- **F-218**（来源：1a4c45c12dee.md，https://www.jianshu.com/p/1a4c45c12dee，时点：2020）：文章给出的命令示例包括创建 feature 分支 `git checkout -b myfeature develop`、合并 `git merge --no-ff myfeature`，并说明 `--no-ff`（not fast forward）要求 git merge 即使在 fast forward 条件下也产生一个新的 merge commit，以保持 Feature branches 整个提交链的完整性。
- **F-219**（来源：1a4c45c12dee.md，https://www.jianshu.com/p/1a4c45c12dee，时点：2020）：文章说明 Release branches 达到可发布状态后需完成三个动作：合并到 master 分支、为 master 上的新提交打 TAG、合并回 develop 分支，示例命令含 `git merge --no-ff release-1.2` 与 `git tag -a 1.2`；Hotfix branches 修复后同样需合并回 master 并打 TAG，示例命令含 `git tag -a 1.2.1`。

## 37d5fd7792ae.md《项目的自述文档（README）模板》

- **F-220**（来源：37d5fd7792ae.md，https://www.jianshu.com/p/37d5fd7792ae，时点：2020）：文章标题为《项目的自述文档（README）模板》，作者为"水之心"，内容翻译自 @PurpleBooth 的 README 模板（https://gist.github.com/PurpleBooth/109311bb0361f32d87a2）。
- **F-221**（来源：37d5fd7792ae.md，https://www.jianshu.com/p/37d5fd7792ae，时点：2020）：文章给出的 README 模板结构包括：项目标题、获得开始（先决条件/安装使用）、运行测试程序（分解为端到端测试/编码样式测试）、部署、内置、投稿、版本、作者、许可证、致谢。
- **F-222**（来源：37d5fd7792ae.md，https://www.jianshu.com/p/37d5fd7792ae，时点：2020）：文章在"内置"部分列举示例框架与工具：Dropwizard、Maven、ROME（生成 RSS 源）；"版本"部分说明使用 https://semver.org/lang/zh-CN/ 进行版本控制；"许可证"部分以 MIT 许可证为例并指向 LICENSE.md 文件；"投稿"部分指向 CONTRIBUTING.md。

## 3cb32565dc41.md《4 无版权图库》

- **F-223**（来源：3cb32565dc41.md，https://www.jianshu.com/p/3cb32565dc41，时点：2020）：文章标题为《4 无版权图库》，正文仅列出 3 篇参考资料：《整理 | 几个值得推荐的"开源"图片网站》（简书 p/8038c3426c98）、《几个值得推荐的"开源"图片网站》（知乎专栏 zhuanlan.zhihu.com/p/62326123）、《干货！6个最新免费、开源、高质量的无版权图库！》（简书 p/3882932aea14）。
- **F-224**（来源：3cb32565dc41.md，https://www.jianshu.com/p/3cb32565dc41，时点：2020）：文章标题序号为"4"，属于连载《开源的世界》的教程编号序列，文章未直接列出任何无版权图库的具体网站名称。

## 5a939f2c6b79.md《3 创建 Gist》

- **F-225**（来源：5a939f2c6b79.md，https://www.jianshu.com/p/5a939f2c6b79，时点：2020）：文章标题为《3 创建 Gist》，作者为"水之心"，介绍可创建两种 Gist：公开和机密（secret）Gist。
- **F-226**（来源：5a939f2c6b79.md，https://www.jianshu.com/p/5a939f2c6b79，时点：2020）：文章说明每个 gist 都是 Git 仓库，可以复刻和克隆；公共 gists 显示在 Discover 中且可供搜索，秘密 gists 不显示在 Discover 中也不可搜索；创建 gist 后无法将其从公共转换为机密。
- **F-227**（来源：5a939f2c6b79.md，https://www.jianshu.com/p/5a939f2c6b79，时点：2020）：文章说明秘密 gists 不是私人的，将秘密 gist 的 URL 发送给朋友即可查看，需要代码不被偷窥时可改而创建私有仓库。
- **F-228**（来源：5a939f2c6b79.md，https://www.jianshu.com/p/5a939f2c6b79，时点：2020）：文章给出的创建 Gist 步骤：登录 GitHub、导航到 gist 主页、键入 Gist 的说明和名称、在文本框中键入文本内容、单击 Create public gist 或 Create secret Gist；也可将桌面文本文件直接拖放到 Gist 编辑器中。
- **F-229**（来源：5a939f2c6b79.md，https://www.jianshu.com/p/5a939f2c6b79，时点：2020）：文章说明可将 gist 嵌入到支持 JavaScript 的任何文本字段中（如博文），嵌入特定 gist 文件用 `?file=FILENAME` 附加嵌入 URL；gist 支持地图 GeoJSON 文件，地图显示在嵌入的 Gist 中。

## 648eb0157103.md《程序员需要了解的网站》

- **F-230**（来源：648eb0157103.md，https://www.jianshu.com/p/648eb0157103，时点：2020）：文章标题为《程序员需要了解的网站》，作者为"水之心"，正文先分节介绍 W3Schools、GeeksforGeeks、TutorialsPoint、StackOverflow、HackerRank、Codebeautify，再分"资讯、在线学习、社区&&工具、竞赛"四类列出网站清单。
- **F-231**（来源：648eb0157103.md，https://www.jianshu.com/p/648eb0157103，时点：2020）：文章介绍 W3Schools（标注"需要梯子"）可学习 HTML5、CSS3、PHP、JavaScript、ASP 等，网站内有嵌入式编辑器可练习代码，并提醒国内网站 w3school.com.cn 提供类似中文内容但二者似无关系。
- **F-232**（来源：648eb0157103.md，https://www.jianshu.com/p/648eb0157103，时点：2020）：文章介绍 GeeksforGeeks 主要专注于计算机科学、有大量算法/解决方案/编程问题及面试常问问题；TutorialsPoint 有几乎所有语言框架的教程；StackOverflow 几乎所有问题都得到答案。
- **F-233**（来源：648eb0157103.md，https://www.jianshu.com/p/648eb0157103，时点：2020）：文章介绍 HackerRank 可参与各种编码竞赛并检测竞争能力，赢得比赛可增加分数；Codebeautify 可使代码易于阅读，也支持让代码不能被某个人读取。
- **F-234**（来源：648eb0157103.md，https://www.jianshu.com/p/648eb0157103，时点：2020）：文章的"资讯"部分列举知乎周刊、码农周刊、PyCoder's Weekly、Hacker News、InfoQ、FreeBuf、WooYun（漏洞报告平台）等资讯网站。
- **F-235**（来源：648eb0157103.md，https://www.jianshu.com/p/648eb0157103，时点：2020）：文章的"在线学习"部分列举实验楼（IT在线实训平台）、Codecademy、Teamtreehouse、优达学城（Udacity）、慕课网、Coursera、leetcode（算法学习网站）等。
- **F-236**（来源：648eb0157103.md，https://www.jianshu.com/p/648eb0157103，时点：2020）：文章的"社区&&工具"部分列举开源中国（中文开源社区）、博客园（老牌技术社区）、CSDN（老牌专业 IT 技术社区）、V2EX、GitHub（文章描述为"最大的同性交友网站，拥有代码托管功能"）。
- **F-237**（来源：648eb0157103.md，https://www.jianshu.com/p/648eb0157103，时点：2020）：文章的"竞赛"部分列举 HackerRank、TopCoder（最早的在线竞技编程平台之一）、Coderbyte（提供 200 多项编码挑战、10 门编程语言）、CodeChef（位于印度的编程竞赛网站）、CodeEval（提供公司发起的挑战）、Kaggle（数据发掘和预测竞赛平台）、Codeforces（俄罗斯的编程比赛网站）、CodeSignal（含"公司机器人"功能）。

## 65dc83219330.md《2.2 使用 Git 管理配置团队项目》

- **F-238**（来源：65dc83219330.md，https://www.jianshu.com/p/65dc83219330，时点：2020）：文章标题为《2.2 使用 Git 管理配置团队项目》，作者为"水之心"，介绍项目配置管理（Project Configuration Management，PCM），采用 Git（git-scm.com）与 vscode（code.visualstudio.com）搭配进行项目管理。
- **F-239**（来源：65dc83219330.md，https://www.jianshu.com/p/65dc83219330，时点：2020）：文章给出的项目初始化步骤包括：`git clone git@github.com:xinetzone/projects.git cvsome`、将 demo.gitignore/python.gitignore 复制为 .gitignore、`git add .` 与 `git commit -m "修改 gitignore"`、`mkdir data draft models outputs app notebook`、`git flow init`。
- **F-240**（来源：65dc83219330.md，https://www.jianshu.com/p/65dc83219330，时点：2020）：文章用表格总结 Git Flow 规则：master（永远处在即将发布状态）、develop（最新的开发状态）、feature（基于 develop，完成后 merge 回 develop）、release（基于 develop，完成后 merge 回 develop 和 master）、hotfix（基于 master，完成后 merge 回 master 和 develop）。
- **F-241**（来源：65dc83219330.md，https://www.jianshu.com/p/65dc83219330，时点：2020）：文章场景1以"开发爬取百度图片的 API（spide）"为例，演示 `git flow feature start spide` 创建基于 develop 的特性分支 feature/spide、在 app/ 目录下创建代码（含 baiduimages.py）、`git flow feature finish spide` 将 feature/spide 合并到 develop 并删除该分支。
- **F-242**（来源：65dc83219330.md，https://www.jianshu.com/p/65dc83219330，时点：2020）：文章展示创建裸库的命令 `git clone --bare cvsome/ cvsome.git`，说明 `cvsome.git` 便是需要的服务器；通过 `git clone cvsome.git/ test/cvsome` 在同一台电脑不同目录克隆副本，用 `git branch -a` 查看分支。
- **F-243**（来源：65dc83219330.md，https://www.jianshu.com/p/65dc83219330，时点：2020）：文章给出的版本号格式为 `x.y.z`：x 在重大重构时升级、y 在新的特性发布时升级、z 在修改某个 bug 后升级，并说明每个微服务都需严格按照该开发模式执行。
- **F-244**（来源：65dc83219330.md，https://www.jianshu.com/p/65dc83219330，时点：2020）：文章场景2以"发布上线版本代号 0.0.1"为例，演示 `git flow release start v0.0.1` 创建 release/v0.0.1 分支、`git flow release publish v0.0.1` 提交到服务器、`git flow release track v0.0.1` 追踪远端 release 分支、`git flow release finish v0.0.1 -m "发布 v0.0.1"` 完成发布。
- **F-245**（来源：65dc83219330.md，https://www.jianshu.com/p/65dc83219330，时点：2020）：文章说明 `git flow release finish` 完成的工作：归并 release 分支到 master 并用 release 分支名打 Tag、归并到 develop 并移除 release 分支与远端分支 remotes/origin/release/v0.0.1、切换到 develop 分支。
- **F-246**（来源：65dc83219330.md，https://www.jianshu.com/p/65dc83219330，时点：2020）：文章场景3介绍命令 `git flow hotfix start VERSION [BASENAME]`，其中 VERSION 参数标记修正版本，可自 `[BASENAME]`（finish release 时填写的版本号）开始；`git flow hotfix finish VERSION` 将代码归并回 develop 和 master，master 分支打上修正版本的 TAG。
- **F-247**（来源：65dc83219330.md，https://www.jianshu.com/p/65dc83219330，时点：2020）：文章给出的局域网克隆命令格式为 `git clone lxw@192.168.20.57:/home/lxw/utils/sdk.git`，其中 @ 前为用户名、中间为 IP 地址、最后为裸库绝对路径；文章还列出参考资料《git-flow 备忘清单》（danielkummer.github.io/git-flow-cheatsheet）。

## 6f3a66b1a491.md《1.2 开启一个开源项目》

- **F-248**（来源：6f3a66b1a491.md，https://www.jianshu.com/p/6f3a66b1a491，时点：2020）：文章标题为《1.2 开启一个开源项目》，作者为"水之心"，说明当一个项目被开源，意味着任何人都可以出于任何目的查看、使用、修改和分发你的项目，这些权限通过开源许可（opensource.org/licenses）强制实施。
- **F-249**（来源：6f3a66b1a491.md，https://www.jianshu.com/p/6f3a66b1a491，时点：2020）：文章列举个人或组织开源项目的原因：协作（如 Exercism 是拥有 350 多个贡献者的练习平台）、采用和重组（如 WordPress 派生自 b2 项目）、透明度（对保加利亚/美国政府、银行、医疗保健等受监管行业及 Let's Encrypt 等安全软件重要）。
- **F-250**（来源：6f3a66b1a491.md，https://www.jianshu.com/p/6f3a66b1a491，时点：2020）：文章说明开源不是"免费"的同义词，"免费"只是开源的总体价值的一个副产品，"免费"不是开源定义的一部分，可通过双重许可或有限功能间接地为开源项目收费同时仍遵守开源官方定义。
- **F-251**（来源：6f3a66b1a491.md，https://www.jianshu.com/p/6f3a66b1a491，时点：2020）：文章说明每个开源项目都应包括的文档：Open source license、README、Contributing guidelines、Code of conduct；将文件放在仓库根目录并使用推荐文件名有助于 GitHub 识别并自动显示给读者。
- **F-252**（来源：6f3a66b1a491.md，https://www.jianshu.com/p/6f3a66b1a491，时点：2020）：文章介绍 MIT、Apache 2.0、GPLv3 都是非常流行的开源许可证，可通过 choosealicense.com 选择其他选项；在 GitHub 创建新项目时可以选择许可证，包含开源许可证使项目成为开源，并强调"启动开源项目时，请务必包含许可证"。
- **F-253**（来源：6f3a66b1a491.md，https://www.jianshu.com/p/6f3a66b1a491，时点：2020）：文章说明 README（README.md）应尝试回答的问题：What（这个项目做什么）、Why（为什么有用）、How（如何开始）、Help（在哪里获得更多帮助）、Who（谁维护和参与项目），并给出灵感来源 @18F 的"让 README 可读"与 @PurpleBooth 的 README 模板。
- **F-254**（来源：6f3a66b1a491.md，https://www.jianshu.com/p/6f3a66b1a491，时点：2020）：文章说明 CONTRIBUTING 文件可包含如何提交错误报告（issue 和 pull request 模板）、如何建议新功能、如何配置环境和运行测试等信息，并给出 @nayafia 的贡献指南模板与 @mozilla 的"如何构建 CONTRIBUTION.md"；行为规范可参考《贡献者公约》（contributor-covenant.org），已被超过 4000 个开源项目使用。
- **F-255**（来源：6f3a66b1a491.md，https://www.jianshu.com/p/6f3a66b1a491，时点：2020）：文章介绍了项目命名与品牌（如 Sentry、Thin、node-fetch 命名示例），并给出 pre-launch checklist，涵盖文档（开源协议、基础文档、易记不冲突的项目名）、代码（一致的代码风格、注释清晰、无敏感信息）、人（个人需告知法律部门/理解公司开源政策与 IP；公司或组织需告知法律部门、有营销计划、有人管理社区互动、至少两人有管理访问权限）等检查项。

## 8a47a9e7353b.md《Git 下载代码加速，解除容量限制》

- **F-256**（来源：8a47a9e7353b.md，https://www.jianshu.com/p/8a47a9e7353b，时点：2020）：文章标题为《Git 下载代码加速，解除容量限制》，作者为"水之心"；针对 `error: RPC failed; curl 18 transfer closed with outstanding read data remaining` 报错，给出的方法之一是增大缓存：`git config --global http.postBuffer 524288000`，并用 `git config --list` 查看是否生效后重新克隆。
- **F-257**（来源：8a47a9e7353b.md，https://www.jianshu.com/p/8a47a9e7353b，时点：2020）：文章针对网络下载速度缓慢给出的命令：`git config --global http.lowSpeedLimit 0` 与 `git config --global http.lowSpeedTime 999999`。
- **F-258**（来源：8a47a9e7353b.md，https://www.jianshu.com/p/8a47a9e7353b，时点：2020）：文章给出的第三种方法：以浅层克隆后更新远程库到本地，命令为 `git clone --depth=1 http://xxx.git` 与 `git fetch --unshallow`。
- **F-259**（来源：8a47a9e7353b.md，https://www.jianshu.com/p/8a47a9e7353b，时点：2020）：文章列出的参考资料为博客《使用Git pull文件时，出现"error: RPC failed; curl 18 transfer closed with outstanding read data remaining"》（cnblogs.com/p/12503650.html）。

## 9e81e3ca89a8.md《1.1 开源项目指南》（部分抓取）

- **F-260**（来源：9e81e3ca89a8.md，https://www.jianshu.com/p/9e81e3ca89a8，时点：2020）：文章标题为《1.1 开源项目指南》，作者为"水之心"，学习资料为开源软件指南（Open Source Guides，opensource.guide/zh-cn/）；本文为部分抓取，正文在「你提交贡献之后发生了什么 -> 没有人响应你」章节的"每个人都会遇到这样的情况。"处截断，后续章节（含文末"最后编辑于"页脚）未获取。
- **F-261**（来源：9e81e3ca89a8.md，https://www.jianshu.com/p/9e81e3ca89a8，时点：2020）：文章列举为开源做贡献的原因：巩固现有技能、遇见志同道合的人、寻找导师并尝试帮助他人、在公众间建立声誉（职业口碑）、学习领导和管理的艺术、鼓励作出改变（哪怕很微小）。
- **F-262**（来源：9e81e3ca89a8.md，https://www.jianshu.com/p/9e81e3ca89a8，时点：2020）：文章说明为开源做贡献不一定需要编码能力，并列出多种非编码贡献类型：规划事件（研讨会/线下分享/大型会议）、设计（重新布置布局/用户研究/风格指南/t恤或新标志）、写作（文档/教程/新闻稿/翻译）、组织活动（链接重复问题、建议新标签、阐述问题）、享受编码乐趣（解决开放问题/写新功能/自动化设置/改进工具与测试）、帮助他人（回答 Stack Overflow 与 reddit 问题、帮助缓和讨论板）、在编码方面帮助他人（审核代码/撰写教程/做导师）。
- **F-263**（来源：9e81e3ca89a8.md，https://www.jianshu.com/p/9e81e3ca89a8，时点：2020）：文章说明开源项目通常包含的文档：LICENSE（每个开源项目必须包含开源许可协议，源码开放但无许可协议就不能叫做开源）、README、CONTRIBUTING、CODE_OF_CONDUCT，及其他文档（教程、导游、治理规则）；文章还列举开源项目的组织工具：问题追踪（Issue tracker）、Pull requests、论坛或邮件列表、即时在线聊天（Slack 或 IRC）。
- **F-264**（来源：9e81e3ca89a8.md，https://www.jianshu.com/p/9e81e3ca89a8，时点：2020）：文章列出找合适项目做贡献的资源：GitHub 探索（github.com/explore/）、Open Source Friday、First Timers Only、CodeTriage、24 Pull Requests、Up For Grabs、像忍者一样贡献（contributor.ninja）。
- **F-265**（来源：9e81e3ca89a8.md，https://www.jianshu.com/p/9e81e3ca89a8，时点：2020）：文章给出贡献前检查列表（是否有许可协议、提交活跃度、开放 issue/PR 数量与维护者响应速度、项目受欢迎程度），并说明沟通建议（给出上下文、做好准备工作、保持请求短小直接、公开场合沟通、大胆提问但要谨慎、尊重社区决定、保持优雅）及创建 issue 与 pull request 的适用情形。


# 事实登记：Notebook 3（无人驾驶 / Autoware / ROS2 / DDS / WSL2）

> 信源：简书连载《☠️无人驾驶(停止维护)》（nb/47487870，作者：水之心），共 10 篇，原始文本快照位于 `raw/notebook3-autonomous/`。
> 编号从 F-301 起。所有事实为文章陈述内容的客观登记（零推测），标注来源 slug、原文 URL 与内容时点（2020 年前后）。

## 0066c78a2f43.md（无人驾驶数据集）

- **F-301**（来源：0066c78a2f43.md，https://www.jianshu.com/p/0066c78a2f43，时点：2020）：文章列出 KITTI 数据集（网址 http://www.cvlibs.net/datasets/kitti/），称其为"目前最知名的自动驾驶数据集之一"。
- **F-302**（来源：0066c78a2f43.md，https://www.jianshu.com/p/0066c78a2f43，时点：2020）：文章介绍 KITTI Vision Benchmark Suite 数据集使用高分辨率彩色和灰度立体相机、Velodyne 3D 激光扫描仪和高精度 GPS/IMU 惯性导航系统，在 10-100 Hz 下进行 6 小时拍摄的交通场景。
- **F-303**（来源：0066c78a2f43.md，https://www.jianshu.com/p/0066c78a2f43，时点：2020）：文章介绍 Cityscapes 数据集包含从 50 个不同城市的街景中记录的各种立体视频序列，高质量的像素级注释为 5000 帧，另有 20000 个弱注释帧。
- **F-304**（来源：0066c78a2f43.md，https://www.jianshu.com/p/0066c78a2f43，时点：2020）：文章介绍 Mapillary 数据集包含 25,000 个高分辨率图像，注释为 66 个对象类别，另有 37 个类别的特定于实例的标签，注释通过使用多边形描绘单个对象完成。
- **F-305**（来源：0066c78a2f43.md，https://www.jianshu.com/p/0066c78a2f43，时点：2020）：文章介绍 comma.ai's Driving Dataset（archive.org 的 comma-dataset）包含 7.25 小时的高速公路驾驶，10 个可变大小的视频片段以 20 Hz 频率录制，相机安装在 Acura ILX 2016 的挡风玻璃上，测量值转换为均匀的 100 Hz 时基。
- **F-306**（来源：0066c78a2f43.md，https://www.jianshu.com/p/0066c78a2f43，时点：2020）：文章介绍 Udacity's Driving Dataset（优达学城的自动驾驶数据集）包含 ROSBAG 训练数据，约 80 GB。
- **F-307**（来源：0066c78a2f43.md，https://www.jianshu.com/p/0066c78a2f43，时点：2020）：文章介绍 ApolloCar3D 数据集包含 5,277 个驾驶图像和超过 60K 的汽车实例，每辆汽车配备具有绝对模型尺寸和语义标记关键点的行业级 3D CAD 模型。
- **F-308**（来源：0066c78a2f43.md，https://www.jianshu.com/p/0066c78a2f43，时点：2020）：文章介绍 BDDV（Berkeley 的大规模自动驾驶视频数据集）包含超过 100K 的视频，包括图像级别标记、对象边界框、可行驶区域、车道标记和全帧实例分割。
- **F-309**（来源：0066c78a2f43.md，https://www.jianshu.com/p/0066c78a2f43，时点：2020）：文章介绍 nuscenes 数据集由安波福（aptiv）于 2019 年 3 月正式公开，包含从波士顿和新加坡收集的 1000 个"场景"，由 140 万张图像、39 万次激光雷达扫描和 140 万个 3D 人工注释边界框组成。
- **F-310**（来源：0066c78a2f43.md，https://www.jianshu.com/p/0066c78a2f43，时点：2020）：文章介绍 H3D - HRI-US 数据集由本田研究所于 2019 年 3 月发布（介绍见 arXiv:1903.01568），使用 3D LiDAR 扫描仪收集，包含 160 个拥挤且高度互动的交通场景，在 27,721 帧中共有 100 万个标记实例。
- **F-311**（来源：0066c78a2f43.md，https://www.jianshu.com/p/0066c78a2f43，时点：2020）：文章介绍 CamVid（剑桥驾驶标签视频数据库）是第一个具有对象类语义标签的视频集合，数据库提供将每个像素与 32 个语义类之一关联的基础事实标签。

## 46945ab25c01.md（数据分发服务：DDS）

- **F-312**（来源：46945ab25c01.md，https://www.jianshu.com/p/46945ab25c01，时点：2020）：文章翻译自 dds-foundation.org 的 "What is DDS" 一文，介绍数据分发服务（DDS™）是来自 Object Management Group®（OMG®）的中间件协议和 API 标准，提供以数据为中心的连接。
- **F-313**（来源：46945ab25c01.md，https://www.jianshu.com/p/46945ab25c01，时点：2020）：文章介绍 DDS 提供 QoS 控制的数据共享，应用程序通过发布和订阅由其主题名称标识的主题进行通信，订阅可以指定时间和内容过滤器，仅获取在主题上发布的数据的子集。
- **F-314**（来源：46945ab25c01.md，https://www.jianshu.com/p/46945ab25c01，时点：2020）：文章介绍不同的 DDS 域（domain）彼此完全独立，DDS 域之间没有数据共享。
- **F-315**（来源：46945ab25c01.md，https://www.jianshu.com/p/46945ab25c01，时点：2020）：文章介绍 DDS 概念上的"全局数据空间"（global data space），对应用程序来说全局数据空间看起来像是通过 API 访问的本地内存，文章陈述 DDS 进行对等通信。
- **F-316**（来源：46945ab25c01.md，https://www.jianshu.com/p/46945ab25c01，时点：2020）：文章介绍 DDS 提供发布者和订阅者的动态发现（Dynamic Discovery），该机制使 DDS 应用程序可扩展，应用程序不必知道或配置通信端点（endpoint）。
- **F-317**（来源：46945ab25c01.md，https://www.jianshu.com/p/46945ab25c01，时点：2020）：文章介绍 DDS 包括为信息分发提供身份验证、访问控制、机密性和完整性的安全机制，DDS Security 使用分散的点对点体系结构。
- **F-318**（来源：46945ab25c01.md，https://www.jianshu.com/p/46945ab25c01，时点：2020）：文章说明 DDS DomainParticipant 代表域中应用程序的本地成员身份，并充当 DDS 发布者、订阅者、主题、MultiTopics 和 ContentFilteredTopics 的工厂。

## 7218542ae424.md（Ubuntu 搭建 AutowareAuto）

- **F-319**（来源：7218542ae424.md，https://www.jianshu.com/p/7218542ae424，时点：2020）：文章描述使用 Agile Development Environment (ADE) 开发 Autoware.Auto 应用，参考来源为 gitlab.com/ApexAI/autowareclass2020 的 lectures/01_DevelopmentEnvironment/devenv.md 与 AutowareAuto 官方 installation 文档。
- **F-320**（来源：7218542ae424.md，https://www.jianshu.com/p/7218542ae424，时点：2020）：文章说明 ADE 需要一个在主机上的目录作为用户在容器内的主目录挂载，该目录填充 dotfiles 且必须与容器外部用户的主目录不同；文章建议多项目场景下每个项目使用专用的 adehome 目录。
- **F-321**（来源：7218542ae424.md，https://www.jianshu.com/p/7218542ae424，时点：2020）：文章说明 ADE 寻找一个包含名为 `.adehome` 文件的目录（从当前工作目录开始并继续到父目录）来标识要挂载的 ADE 主目录；Autoware.Auto 提供 `.aderc` 文件，该文件应存在于当前工作目录或任何父目录中，可通过设置环境变量覆盖默认配置值。
- **F-322**（来源：7218542ae424.md，https://www.jianshu.com/p/7218542ae424，时点：2020）：文章给出克隆 AutowareAuto 的命令：`git clone --recursive https://gitlab.com/autowarefoundation/autoware.auto/AutowareAuto.git`。
- **F-323**（来源：7218542ae424.md，https://www.jianshu.com/p/7218542ae424，时点：2020）：文章给出初始化与测试命令：`ade start --update --enter` 后依次执行 `colcon build`、`colcon test`、`colcon test-result`。

## 86377a66ecef.md（ROS2 概念）

- **F-324**（来源：86377a66ecef.md，https://www.jianshu.com/p/86377a66ecef，时点：2020）：文章介绍 ROS 2 是基于匿名发布/订阅（publish/subscribe）机制的中间件，该机制允许消息（message）在不同的 ROS 进程之间传递；文章说明 ROS graph 是所有 ROS 2 系统的核心。
- **F-325**（来源：86377a66ecef.md，https://www.jianshu.com/p/86377a66ecef，时点：2020）：文章列出基本概念：Nodes（使用 ROS 与其他节点通信的实体）、Messages（订阅或发布主题时使用的 ROS 数据类型）、Topics（节点将消息发布到主题或订阅主题以接收消息）、Discovery（节点决定如何互相通信的自动过程）。
- **F-326**（来源：86377a66ecef.md，https://www.jianshu.com/p/86377a66ecef，时点：2020）：文章介绍节点是 ROS graph 的参与者，ROS 节点使用 ROS 客户端库（client library）与其他节点通信，节点之间的连接通过分布式发现过程建立。
- **F-327**（来源：86377a66ecef.md，https://www.jianshu.com/p/86377a66ecef，时点：2020）：文章介绍 ROS 2 团队维护的客户端库：rclcpp（C++ client library）、rclpy（Python client library），核心 ROS 客户端库缩写为 RCL。
- **F-328**（来源：86377a66ecef.md，https://www.jianshu.com/p/86377a66ecef，时点：2020）：文章描述节点发现过程：节点启动后向具有相同 ROS domain（通过 `ROS_DOMAIN_ID` 环境变量设置）的网络上的其他节点通告其存在状态；节点定期通告其存在；节点下线时向其他节点通告；仅具有兼容 QoS 设置的节点建立连接。
- **F-329**（来源：86377a66ecef.md，https://www.jianshu.com/p/86377a66ecef，时点：2020）：文章介绍 ROS2 基于 DDS/RTPS 作为中间件，该中间件提供发现（discovery）、序列化（serialization）和传输（transportation）；RTPS（DDSI-RTPS）是 DDS 通过网络进行通信的有线协议。
- **F-330**（来源：86377a66ecef.md，https://www.jianshu.com/p/86377a66ecef，时点：2020）：文章列举 DDS 实现：RTI 的 Connext、ADLINK 的 OpenSplice、Eclipse 的 Cyclone DDS、eProsima 的 Fast RTPS；文章说明将 DDS/RTPS 实现与 ROS2 结合需创建 "ROS Middleware interface"（rmw 接口）包。
- **F-331**（来源：86377a66ecef.md，https://www.jianshu.com/p/86377a66ecef，时点：2020）：文章介绍 QoS 策略中 History 包括 Keep last（最多存储 N 个样本，可通过"队列深度"选项配置）与 Keep all（根据基础中间件的配置资源限制存储所有样本）。
- **F-332**（来源：86377a66ecef.md，https://www.jianshu.com/p/86377a66ecef，时点：2020）：文章介绍 Topic Statistics 提供的度量是接收到的消息寿命（age）与消息周期（period），统计量包括平均值、最大值、最小值、标准差和样本数，在移动窗口（moving window）中计算；文章说明 ROS 2 Foxy 的该功能仅限 C++（rclcpp）支持。

## 8f97786e1631.md（AutowareAuto 基础）

- **F-333**（来源：8f97786e1631.md，https://www.jianshu.com/p/8f97786e1631，时点：2020）：文章介绍 Autoware 是由 The Autoware Foundation 维护的软件堆栈，并列出 2020 年已有的三个 Autoware 项目：Autoware.AI、Autoware.IO、Autoware.Auto。
- **F-334**（来源：8f97786e1631.md，https://www.jianshu.com/p/8f97786e1631，时点：2020）：文章介绍 Autoware.AI 基于 ROS1，是第一个 Autoware 项目；Autoware.IO 是 Autoware 的接口，包含传感器驱动程序（sensor drivers）、有线控制器（by-wire controllers）、SoC 板的硬件相关程序；Autoware.Auto 基于 ROS 2，提供实时（RT）功能和更多安全措施。
- **F-335**（来源：8f97786e1631.md，https://www.jianshu.com/p/8f97786e1631，时点：2020）：文章说明 2020 年 5 月 Autoware.Auto 具有使用 LIDAR 和 GPS 的全面定位功能、对 2D 和 3D 中其他交通参与者的完整感知、相对简单的动作运动计划。
- **F-336**（来源：8f97786e1631.md，https://www.jianshu.com/p/8f97786e1631，时点：2020）：文章介绍开发环境 ADE 是 Docker 的包装器，允许与 Docker 交互（如启动/停止 docker）、配置和 docker 卷版本控制。
- **F-337**（来源：8f97786e1631.md，https://www.jianshu.com/p/8f97786e1631，时点：2020）：文章给出 ADE 安装命令：`wget https://gitlab.com/ApexAI/ade-cli/uploads/85a5af81339fe55555ee412f9a3a734b/ade+x86_64`，随后 `mv ade+x86_64 ade`、`chmod +x ade`、`mv ade ~/.local/bin`、`which ade`。
- **F-338**（来源：8f97786e1631.md，https://www.jianshu.com/p/8f97786e1631，时点：2020）：文章给出 NVIDIA Docker（nvidia-container-toolkit）安装命令：添加 nvidia.github.io/nvidia-docker 的 GPG 公钥与软件源，执行 `sudo apt-get install -y nvidia-container-toolkit`、`sudo systemctl restart docker`。
- **F-339**（来源：8f97786e1631.md，https://www.jianshu.com/p/8f97786e1631，时点：2020）：文章给出 ADE setup 命令：`touch .adehome`、`git clone --recurse-submodules https://gitlab.com/autowarefoundation/autoware.auto/AutowareAuto.git`、`ade start`、`ade enter`；文章说明 Autoware.Auto 使用 ROS2 Dashing，安装在 /opt/ros/dashing/，可通过 `ade$ ros2 -h` 确认安装。
- **F-340**（来源：8f97786e1631.md，https://www.jianshu.com/p/8f97786e1631，时点：2020）：文章给出目标检测演示流程与命令：将 Palo Alto 行驶时记录的 pcap 文件（UDP 软件包集合）移到 adehome 目录的 data/ 文件夹、克隆 ApexAI/autowareclass2020 仓库、`source /opt/AutowareAuto/setup.bash`，随后执行 `udpreplay ~/data/route_small_loop_rw-127.0.0.1.pcap`、`rviz2 -d ...`、`ros2 run velodyne_node velodyne_cloud_node_exe ...`、`ros2 run robot_state_publisher robot_state_publisher .../lexus_rx_450h.urdf`、`ros2 run point_cloud_filter_transform_nodes ...`、`ros2 run ray_ground_classifier_nodes ...`、`ros2 run euclidean_cluster_nodes ...`。

## 98c8af1d2d33.md（wsl2 配置多环境的深度学习 GPU 环境）

- **F-341**（来源：98c8af1d2d33.md，https://www.jianshu.com/p/98c8af1d2d33，时点：2020）：文章参考 Microsoft Docs "在 WSL 2 中启用 NVIDIA CUDA" 配置基础设置，并参考 NVIDIA 的 CUDA 工具包 11.1 下载页（target_os=Linux、target_distro=WSLUbuntu）。
- **F-342**（来源：98c8af1d2d33.md，https://www.jianshu.com/p/98c8af1d2d33，时点：2020）：文章给出 WSL2 安装 CUDA 11.1 的命令序列：`wget .../cuda-wsl-ubuntu.pin`、`sudo mv cuda-wsl-ubuntu.pin /etc/apt/preferences.d/cuda-repository-pin-600`、`wget .../cuda-repo-wsl-ubuntu-11-1-local_11.1.0-1_amd64.deb`、`sudo dpkg -i cuda-repo-wsl-ubuntu-11-1-local_11.1.0-1_amd64.deb`、`sudo apt-key add /var/cuda-repo-wsl-ubuntu-11-1-local/7fa2af80.pub`、`sudo apt-get update`、`sudo apt-get -y install cuda`。
- **F-343**（来源：98c8af1d2d33.md，https://www.jianshu.com/p/98c8af1d2d33，时点：2020）：文章提示安装过程中若报错 "404 Not Found [IP: 180.101.196.129 443]"，可尝试离线安装：`wget .../cuda_11.1.0_455.23.05_linux.run`、`sudo sh cuda_11.1.0_455.23.05_linux.run`。
- **F-344**（来源：98c8af1d2d33.md，https://www.jianshu.com/p/98c8af1d2d33，时点：2020）：文章给出 wsl2 安装 GUI 的两个参考链接：Harshit Yadav 的 "Install GUI Desktop in WSL2 Ubuntu 20.04 LTS in Windows 10" 与 "The complete WSL2 + GUI setup"。
- **F-345**（来源：98c8af1d2d33.md，https://www.jianshu.com/p/98c8af1d2d33，时点：2020）：文章说明下载 Anaconda Individual Edition 后执行 `sh Anaconda-...` 安装。
- **F-346**（来源：98c8af1d2d33.md，https://www.jianshu.com/p/98c8af1d2d33，时点：2020）：文章给出 MXNet 环境配置命令：`conda create -n mxnet python=3.9`、`conda install jupyter notebook`、`conda install cudnn=8 -c conda-forge`、`pip install mxnet-cu110`、`conda install ipykernel`、`python -m ipykernel install --name mxnet --user`、`pip install autopep8`。
- **F-347**（来源：98c8af1d2d33.md，https://www.jianshu.com/p/98c8af1d2d33，时点：2020）：文章给出 TensorFlow 环境配置命令：`conda create -n tensorflow python=3.9`、`conda install jupyter notebook`、`conda install cudnn=8 -c conda-forge`、`pip install tensorflow`、`conda install ipykernel`、`python -m ipykernel install --name tensorflow --user`。
- **F-348**（来源：98c8af1d2d33.md，https://www.jianshu.com/p/98c8af1d2d33，时点：2020）：文章给出 PyTorch 环境配置命令：`conda create -n torch python=3.9`、`conda install pytorch torchvision torchaudio cudatoolkit=11 -c pytorch -c conda-forge`、`conda install ipykernel`、`python -m ipykernel install --name torch --user`。

## a95f95276fec.md（WSL2 之 autoware.auto）

- **F-349**（来源：a95f95276fec.md，https://www.jianshu.com/p/a95f95276fec，时点：2020）：文章说明 WSL2 提供 X 桌面支持，不再需要安装 xrdp（参考文章《WSL2 提供 X 桌面支持》）。
- **F-350**（来源：a95f95276fec.md，https://www.jianshu.com/p/a95f95276fec，时点：2020）：文章给出 WSL2 安装 docker 的步骤：安装依赖 apt-transport-https、ca-certificates、curl、gnupg-agent、software-properties-common；执行 `curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -` 信任 Docker 的 GPG 公钥；添加 `deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable` 软件源；最后 `sudo apt-get install docker-ce docker-ce-cli containerd.io`。
- **F-351**（来源：a95f95276fec.md，https://www.jianshu.com/p/a95f95276fec，时点：2020）：文章给出创建 autoware 环境并安装 ade-cli 的命令：`conda create --name autoware python=3.7`、`conda activate autoware && pip install ade-cli`。
- **F-352**（来源：a95f95276fec.md，https://www.jianshu.com/p/a95f95276fec，时点：2020）：文章给出免 sudo 使用 docker 命令的配置步骤：`docker login` 登录、`sudo groupadd docker`、`sudo gpasswd -a ${USER} docker`、`sudo service docker restart`、`newgrp - docker`。
- **F-353**（来源：a95f95276fec.md，https://www.jianshu.com/p/a95f95276fec，时点：2020）：文章给出在 autoware 环境下配置与测试 Autoware.Auto 的命令：`sudo service docker start`、`cd /mnt/d/adehome/AutowareAuto && conda activate autoware && ade start --update --enter`、`ade$ cd AutowareAuto`、`ade$ colcon build`、`ade$ colcon test`、`ade$ colcon test-result`；测试时执行 `source /opt/AutowareAuto/setup.bash`、`ros2 launch autoware_demos ekf_ndt_smoothing_lgsvl.launch.py`。

## ca403b26e91b.md（Autonomous 资源）

- **F-354**（来源：ca403b26e91b.md，https://www.jianshu.com/p/ca403b26e91b，时点：2020）：文章列出 paperswithcode.com 的 Autonomous Driving 与 Autonomous Vehicles 两个任务页面、codete 的 "Technology in Autonomous Vehicles: Overview of Current Trends and the Future" 文章、unite.ai 的 "2021 is the Year of Autonomous Vehicles" 文章。
- **F-355**（来源：ca403b26e91b.md，https://www.jianshu.com/p/ca403b26e91b，时点：2020）：文章列出 GitHub 资源：github topics autonomous-vehicles、DeepTecher/AutonomousVehiclePaper、microsoft/AutonomousDrivingCookbook、DeepTecher/awesome-autonomous-vehicle。
- **F-356**（来源：ca403b26e91b.md，https://www.jianshu.com/p/ca403b26e91b，时点：2020）：文章列出 Kaggle 竞赛 "Lyft Motion Prediction for Autonomous Vehicles" 的代码页面。

## dfc1df4eb6ee.md（WSL2 安装和配置无人驾驶系统 autoware.auto）

- **F-357**（来源：dfc1df4eb6ee.md，https://www.jianshu.com/p/dfc1df4eb6ee，时点：2020）：文章列出初始步骤：安装 docker、安装 Anaconda3、使用 vscode 创建名为 autoware 的工作区、使用 Git 拉取 AutowareAuto 到 d:/adehome/AutowareAuto（可自定义），命令为 `git clone --recursive https://gitlab.com/autowarefoundation/autoware.auto/AutowareAuto.git`。
- **F-358**（来源：dfc1df4eb6ee.md，https://www.jianshu.com/p/dfc1df4eb6ee，时点：2020）：文章说明需安装 Ubuntu20.04 子系统与远程桌面（参考文章《WSL2 配置深度学习环境》），并使用 conda 创建 autoware 环境安装 ade-cli（命令为 `pip install ade-cli`）。
- **F-359**（来源：dfc1df4eb6ee.md，https://www.jianshu.com/p/dfc1df4eb6ee，时点：2020）：文章给出初始化 AutowareAuto 的命令：`sudo service xrdp restart`、`sudo service docker start`、`cd /mnt/d/adehome/AutowareAuto && conda activate autoware && ade start --update --enter`。
- **F-360**（来源：dfc1df4eb6ee.md，https://www.jianshu.com/p/dfc1df4eb6ee，时点：2020）：文章给出构建与测试命令：`colcon build && colcon test`、`colcon test-result`，激活 autoware.auto 的命令为 `source /opt/AutowareAuto/setup.bash`。
- **F-361**（来源：dfc1df4eb6ee.md，https://www.jianshu.com/p/dfc1df4eb6ee，时点：2020）：文章给出处理 VcXsrv 不显示的方法：在 PowerShell 终端执行 ipconfig 获取 IPv4 地址（示例 172.30.240.1），在 WSL2 的 ~/.bashrc 添加 `export DISPLAY=172.30.240.1:0`，执行 `source ~/.bashrc` 激活，并用 `ros2 launch autoware_demos ekf_ndt_smoothing_lgsvl.launch.py` 测试 X Play 效果。

## e99b8cbb1825.md（汽车系统开发常见名称）

- **F-362**（来源：e99b8cbb1825.md，https://www.jianshu.com/p/e99b8cbb1825，时点：2020）：文章定义电子控制器（又称电子控制单元或电控单元，英文 Electronic Control Unit，缩写 ECU）为汽车电子系统中控制电气系统、电子系统及汽车子系统的嵌入式系统。
- **F-363**（来源：e99b8cbb1825.md，https://www.jianshu.com/p/e99b8cbb1825，时点：2020）：文章定义控制器局域网（Controller Area Network，简称 CAN 或 CAN bus）为一种车用总线标准，文章陈述该标准允许网络上的单片机和仪器在不需要主机（Host）的情况下相互通信、基于消息传递协议，并在车辆上采用复用通信线缆以降低铜线使用量。
