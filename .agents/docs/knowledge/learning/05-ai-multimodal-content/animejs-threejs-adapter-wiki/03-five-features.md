---
id: "animejs-threejs-adapter-wiki-five-features"
title: "五大核心特性详解"
category: "learning"
tags: ["animejs", "threejs", "features", "property-mapping", "transforms", "instancing"]
date: "2026-08-03"
status: "active"
author: "SpecWeave"
source: "spec:animejs-threejs-adapter-wiki"
---

# 五大核心特性详解

Anime.js Three.js 适配器通过五大核心特性，系统性解决了原生 Three.js 动画开发的六大痛点。本章将逐一详解每个特性的功能、解决的问题、API 使用方法和注意事项。

---

&gt; ⚠️ **API参考提示**：以下代码示例为基于官方文档和最佳实践的参考写法，实际导入方式、函数签名等具体API细节请以 [Anime.js v4.5官方文档](https://animejs.com/documentation/three) 为准。

---

## 特性1：Object Properties（属性扁平化映射）

### 功能说明

属性扁平化映射是适配器最基础也是最核心的特性。它将 Three.js `Object3D` 及其子类（`Mesh`、`Group`、`Light` 等）上分散在多层嵌套对象中的动画属性，统一映射为 Anime.js 可直接访问的扁平化属性。

通过这一特性，开发者无需再写 `mesh.position.x`、`mesh.rotation.y` 这种深层链式访问，直接在动画配置中写 `x`、`rotateY` 即可，大幅减少代码噪音。

### 解决的痛点

| 原生痛点 | 具体表现 |
|---------|---------|
| **属性嵌套分散** | 位置在 `mesh.position`、旋转在 `mesh.rotation`、缩放在 `mesh.scale`、材质在 `mesh.material`，属性分散在不同嵌套对象，动画代码割裂 |
| **手动角度弧度转换** | Three.js 旋转使用弧度（radian），需要手动写 `Math.PI / 180 * angle` 进行转换，容易出错 |
| **透明度设置繁琐** | 设置透明度需要同时写 `mesh.material.opacity = value` 和 `mesh.material.transparent = true`，容易遗漏后者导致无效 |
| **批量对象动画麻烦** | 对一组对象做动画需要手动遍历数组，逐个设置属性 |

### 完整属性映射表

| 扁平化属性 | 原生 Three.js 路径 | 自动处理逻辑 |
|-----------|-------------------|-------------|
| `x` | `mesh.position.x` | 直接映射 |
| `y` | `mesh.position.y` | 直接映射 |
| `z` | `mesh.position.z` | 直接映射 |
| `translateX` | `mesh.position.x` | 同 `x`，CSS 风格别名 |
| `translateY` | `mesh.position.y` | 同 `y`，CSS 风格别名 |
| `translateZ` | `mesh.position.z` | 同 `z`，CSS 风格别名 |
| `rotateX` | `mesh.rotation.x` | **自动角度→弧度转换**，输入角度值即可 |
| `rotateY` | `mesh.rotation.y` | **自动角度→弧度转换**，输入角度值即可 |
| `rotateZ` | `mesh.rotation.z` | **自动角度→弧度转换**，输入角度值即可 |
| `scaleX` | `mesh.scale.x` | 单轴缩放 |
| `scaleY` | `mesh.scale.y` | 单轴缩放 |
| `scaleZ` | `mesh.scale.z` | 单轴缩放 |
| `scale` | `mesh.scale.setScalar()` | 单值等比缩放，自动应用到XYZ |
| `opacity` | `mesh.material.opacity` | **自动设置 `transparent: true`** |
| `visible` | `mesh.visible` | 布尔属性直接映射 |

### 原生写法 vs 适配器写法

**原生 Three.js 写法**（手动管理动画循环）：

```javascript
const mesh = new THREE.Mesh(geometry, material);
const clock = new THREE.Clock();

function animate() {
  requestAnimationFrame(animate);
  const time = clock.getElapsedTime();

  mesh.position.x = Math.sin(time) * 2;
  mesh.position.y = Math.cos(time * 0.5) * 1;
  mesh.rotation.x = time * 0.5;
  mesh.rotation.z = Math.sin(time) * (Math.PI / 6);
  mesh.scale.setScalar(1 + Math.sin(time * 2) * 0.2);

  mesh.material.opacity = 0.5 + Math.sin(time) * 0.5;
  mesh.material.transparent = true;

  renderer.render(scene, camera);
}
animate();
```

**Anime.js 适配器写法**：

```javascript
import { animate } from 'animejs';
import { three } from '@animejs/three';

const mesh = new THREE.Mesh(geometry, material);

animate(mesh, {
  x: Math.sin('*') * 2,
  y: Math.cos('*' * 0.5) * 1,
  rotateX: '*' * 28.65,
  rotateZ: Math.sin('*') * 30,
  scale: 1 + Math.sin('*' * 2) * 0.2,
  opacity: [0, 1],
  duration: Infinity,
  loop: true,
  ease: 'linear'
}, three);
```

### 关键 API 参数说明

| 参数 | 类型 | 说明 |
|------|------|------|
| `x/y/z` | `number` | 位置坐标，直接对应 position 的 XYZ 分量 |
| `rotateX/Y/Z` | `number` | 旋转角度（**单位：度**），适配器自动转换为弧度 |
| `scale` | `number` | 等比缩放值，`1` 为原始大小 |
| `scaleX/Y/Z` | `number` | 单轴缩放值 |
| `opacity` | `number` | 透明度，范围 `0-1`，自动开启 `transparent: true` |
| `'*'` | `string` | Anime.js 内置时间变量，代表动画进度（0-1）或当前时间 |

### 注意事项

1. **角度单位**：`rotateX/Y/Z` 使用**角度（degree）**而非弧度，这是有意的 CSS 对齐设计——`rotateX: 180` 就是旋转半圈，无需写 `Math.PI`
2. **透明度自动处理**：当动画 `opacity` 属性时，适配器会自动将材质的 `transparent` 设为 `true`，无需手动设置
3. **批量动画**：支持直接传入对象数组（如 `group.children`），自动遍历并应用到每个元素，类似 DOM 中的 `querySelectorAll` 批量动画
4. **相对值语法**：支持 `x: '+=2'`、`rotateY: '-=45'` 这种相对值写法，在当前值基础上增减
5. **初始值保留**：动画未指定的属性保持原有值，不会被重置

---

## 特性2：Extended Transforms（CSS transform 风格 3D 变换）

### 功能说明

扩展变换特性在基础属性映射之上，引入了前端开发者熟悉的 CSS transform 语法糖到 3D 空间，新增了 `skewX`/`skewY`/`skewZ` 斜切变换和 `transformOrigin` 变换原点控制。

这是 CSS 开发者最熟悉的特性——你在 CSS 中使用 `transform: skew()` 和 `transform-origin` 的经验，可以 100% 迁移到 3D 场景，知识迁移成本几乎为零。

### 解决的痛点

| 原生痛点 | 具体表现 |
|---------|---------|
| **无原生斜切支持** | Three.js 原生没有 skew 变换，需要手动构造矩阵来实现，代码复杂易出错 |
| **变换原点控制困难** | 要改变旋转/缩放中心点，需要嵌套额外的 `Group` 或手动调整 pivot 矩阵，代码繁琐不直观 |
| **知识无法复用** | CSS 开发者已有的 transform 心智模型无法直接应用到 3D 开发，需要重新学习 |

### 斜切变换（skew）

Three.js 原生不支持斜切变换，适配器通过在底层构造自定义变换矩阵来实现这一功能，让开发者可以像在 CSS 中一样使用 `skewX`/`skewY`/`skewZ`。

**代码示例 - skew 斜切变换**：

```javascript
import { animate } from 'animejs';
import { three } from '@animejs/three';

const mesh = new THREE.Mesh(
  new THREE.BoxGeometry(1, 1, 1),
  new THREE.MeshStandardMaterial({ color: 0x00ff88 })
);

animate(mesh, {
  skewX: 45,
  skewY: -20,
  skewZ: 15,
  duration: 1500,
  ease: 'inOutQuad',
  loop: true,
  alternate: true
}, three);
```

### 变换原点（transformOrigin）

`transformOrigin` 类似 CSS 的 `transform-origin` 属性，用于设置旋转、缩放、斜切等变换的中心点。在 Three.js 原生中实现这一点需要嵌套 Group 或手动处理矩阵，适配器将其简化为一个属性。

支持两种设置方式：
- **百分比字符串**：类似 CSS，如 `'50% 50%'`、`'100% 0%'`、`'left bottom'`
- **具体坐标对象**：`{ x: 1, y: 0.5, z: 0 }`（以几何体局部坐标为单位）

**代码示例 - transformOrigin 变换原点**：

```javascript
import { animate } from 'animejs';
import { three } from '@animejs/three';

const mesh = new THREE.Mesh(
  new THREE.BoxGeometry(2, 1, 1),
  new THREE.MeshStandardMaterial({ color: 0xff6600 })
);

animate(mesh, {
  rotateZ: 360,
  transformOrigin: { x: 1, y: 0, z: 0 },
  duration: 2000,
  ease: 'linear',
  loop: true
}, three);
```

**CSS 风格百分比写法**（以官方文档为准）：

```javascript
animate(mesh, {
  scale: [1, 1.5],
  rotateX: 180,
  transformOrigin: '100% 50%',
  duration: 1200,
  ease: 'outBack',
  loop: true,
  alternate: true
}, three);
```

### 关键 API 参数说明

| 参数 | 类型 | 说明 |
|------|------|------|
| `skewX` | `number` | X 轴斜切角度（单位：度），沿 Y 轴方向倾斜 |
| `skewY` | `number` | Y 轴斜切角度（单位：度），沿 X 轴方向倾斜 |
| `skewZ` | `number` | Z 轴斜切角度（单位：度），3D 空间新增斜切轴 |
| `transformOrigin` | `string \| object` | 变换原点，支持百分比字符串（CSS 风格）或 `{x, y, z}` 坐标对象 |

### 注意事项

1. **skew 是适配器扩展功能**：这不是 Three.js 原生能力，适配器在底层通过矩阵运算实现，复杂 skew 动画可能有微小性能开销
2. **transformOrigin 局部坐标**：使用 `{x, y, z}` 对象时，坐标是相对于几何体自身的局部空间，`{x:0, y:0, z:0}` 是几何体中心（默认值）
3. **CSS 命名完全对齐**：属性命名和行为与 CSS transform 保持一致，前端开发者无需重新记忆
4. **可与其他 transform 叠加**：skew 可以和 rotate、scale、translate 同时使用，适配器会正确处理矩阵组合顺序
5. **skewZ 的 3D 特性**：`skewZ` 是 3D 空间特有的斜切轴，CSS 中没有对应概念，用于创建更丰富的空间扭曲效果

---

## 特性3：Materials &amp; Uniforms（材质与 Shader 参数动画）

### 功能说明

材质与着色器动画特性让开发者可以直接动画材质属性和 Shader uniforms 参数，无需深入嵌套对象或在渲染循环中手动更新。适配器支持自动颜色格式解析、常用材质属性直接动画、Shader uniforms 按名访问。

### 解决的痛点

| 原生痛点 | 具体表现 |
|---------|---------|
| **颜色动画繁琐** | 需要调用 `color.setHex()`/`color.setHSL()`/`color.setRGB()` 等方法，不能直接赋值，颜色格式转换麻烦 |
| **材质属性层级深** | 访问金属度、粗糙度需要写 `mesh.material.metalness`，不够直观 |
| **Shader uniforms 手动更新** | 必须在 `requestAnimationFrame` 循环中逐帧更新 `uniform.value`，代码散落在渲染循环中 |
| **透明度设置遗漏** | 动画 opacity 经常忘记设置 `transparent: true`，导致效果不生效 |

### 颜色自动解析

适配器支持多种颜色格式自动解析，可以直接在动画中使用：
- **HEX 格式**：`'#ff0000'`、`'#f00'`
- **RGB 格式**：`'rgb(255, 0, 0)'`
- **HSL 格式**：`'hsl(0, 100%, 50%)'`
- **命名颜色**：`'red'`、`'blue'` 等（以官方文档为准）
- **Three.js Color 对象**：`new THREE.Color(0xff0000)`

### 材质属性动画

支持所有常用材质属性的直接动画，包括颜色、自发光、金属度、粗糙度、透明度等。

**代码示例 - 颜色渐变与材质属性动画**：

```javascript
import { animate } from 'animejs';
import { three } from '@animejs/three';

const mesh = new THREE.Mesh(
  new THREE.TorusKnotGeometry(1, 0.3, 100, 16),
  new THREE.MeshStandardMaterial({
    color: 0xff0000,
    metalness: 0.5,
    roughness: 0.5,
    transparent: true
  })
);

animate(mesh, {
  color: ['#ff0000', 'hsl(120, 100%, 50%)', 'rgb(0, 0, 255)', '#ff0000'],
  opacity: [0.3, 1],
  metalness: [0, 1],
  roughness: [1, 0],
  emissive: '#00ffff',
  emissiveIntensity: [0, 2],
  duration: 3000,
  ease: 'linear',
  loop: true
}, three);
```

### Shader Uniforms 动画

这是非常强大的特性——直接对 `ShaderMaterial` 做动画，uniform 变量名就是动画属性名，适配器自动识别并更新 `uniform.value`，无需在渲染循环中手动赋值。

**代码示例 - Shader uniform 动画**：

```javascript
import { animate } from 'animejs';
import { three } from '@animejs/three';

const shaderMaterial = new THREE.ShaderMaterial({
  uniforms: {
    uTime: { value: 0 },
    uAmplitude: { value: 0.5 },
    uFrequency: { value: 2.0 }
  },
  vertexShader: `
    uniform float uTime;
    uniform float uAmplitude;
    uniform float uFrequency;
    varying vec2 vUv;
    void main() {
      vUv = uv;
      vec3 pos = position;
      pos.z += sin(pos.x * uFrequency + uTime) * uAmplitude;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(pos, 1.0);
    }
  `,
  fragmentShader: `
    varying vec2 vUv;
    void main() {
      gl_FragColor = vec4(vUv, 0.5 + 0.5 * sin(vUv.x * 6.28), 1.0);
    }
  `,
  transparent: true
});

const mesh = new THREE.Mesh(
  new THREE.PlaneGeometry(5, 5, 32, 32),
  shaderMaterial
);

animate(shaderMaterial, {
  uTime: 100,
  uAmplitude: [0.1, 1.5],
  uFrequency: [1, 5],
  duration: 5000,
  ease: 'sineInOut',
  loop: true
}, three);
```

### 关键 API 参数说明

| 参数 | 类型 | 说明 |
|------|------|------|
| `color` | `string \| Color \| Array` | 材质主色，支持 HEX/RGB/HSL/命名色多格式自动解析，支持数组做关键帧动画 |
| `emissive` | `string \| Color` | 自发光颜色，格式同 `color` |
| `emissiveIntensity` | `number` | 自发光强度，`0` 为不发光 |
| `opacity` | `number` | 透明度，`0-1`，**自动设置 `transparent: true`** |
| `metalness` | `number` | 金属度，`0-1`，`0` 为非金属，`1` 为完全金属 |
| `roughness` | `number` | 粗糙度，`0-1`，`0` 为完全光滑镜面，`1` 为完全漫反射 |
| `uniform名称` | `number \| Array` | ShaderMaterial 的 uniforms 可直接按名称动画，自动更新 `.value` |

### 注意事项

1. **动画目标是材质还是 Mesh**：上面示例中 Shader 动画直接传入 `shaderMaterial`，颜色/金属度等传入 `mesh`——两种方式都支持（以官方文档为准）
2. **颜色插值在正确色彩空间**：适配器自动处理颜色空间转换，确保颜色渐变视觉上平滑自然
3. **uniform 类型限制**：当前主要支持 `float`/`int`/`vec2`/`vec3`/`vec4`/`Color` 等数值类型的 uniforms，纹理（sampler2D）动画需要手动处理
4. **transparent 自动设置**：动画 `opacity` 时自动开启透明，但如果初始材质就需要透明，建议手动设置 `transparent: true`
5. **数组关键帧**：使用 `[start, mid, end]` 数组可以定义多段颜色/数值动画，比使用 timeline 更简洁

---

## 特性4：InstancedMesh（实例化网格批量动画）

### 功能说明

实例化网格动画特性为 Three.js 的 `InstancedMesh` 提供了 `three.getInstances()` 辅助方法，自动生成可独立动画的虚拟实例对象数组。每个实例可以像普通 `Mesh` 一样独立控制位置、旋转、缩放、颜色，同时保留 InstancedMesh 的性能优势（一次 draw call 渲染上千个实例）。

### 解决的痛点

| 原生痛点 | 具体表现 |
|---------|---------|
| **手动管理矩阵** | 原生需要创建 `Matrix4` 对象数组，手动调用 `setMatrixAt()` 设置每个实例的矩阵，代码量大且极易出错 |
| **矩阵数学复杂** | 需要手动组合平移、旋转、缩放矩阵，不能像普通 Mesh 一样直接修改 position/rotation/scale |
| **批量动画困难** | 要做 stagger 交错动画或时间线动画，需要自己计算每个实例的延迟和矩阵更新 |
| **颜色设置繁琐** | 实例颜色需要单独调用 `setColorAt()`，和矩阵管理分开 |

### 核心 API：getInstances()

`three.getInstances(instancedMesh, count?)` 是适配器提供的关键方法，它返回一个实例代理对象数组。数组中的每个对象都可以像普通 Mesh 一样动画 `x`/`y`/`rotateX`/`color` 等属性，适配器在底层自动更新矩阵，无需开发者手动操作 Matrix4。

**代码示例 - 1000个立方体网格交错动画**：

```javascript
import { animate, stagger } from 'animejs';
import { three } from '@animejs/three';

const count = 1000;
const geometry = new THREE.BoxGeometry(0.2, 0.2, 0.2);
const material = new THREE.MeshStandardMaterial();
const instancedMesh = new THREE.InstancedMesh(geometry, material, count);

for (let i = 0; i &lt; count; i++) {
  const matrix = new THREE.Matrix4();
  matrix.setPosition(
    (Math.random() - 0.5) * 20,
    (Math.random() - 0.5) * 20,
    (Math.random() - 0.5) * 20
  );
  instancedMesh.setMatrixAt(i, matrix);
}
scene.add(instancedMesh);

const instances = three.getInstances(instancedMesh);

animate(instances, {
  y: '+=5',
  rotateX: 360,
  rotateY: 360,
  scale: [0.5, 1.5],
  duration: 2000,
  stagger: {
    each: 2,
    from: 'center',
    grid: [10, 10, 10]
  },
  ease: 'outElastic',
  loop: true,
  alternate: true
}, three);
```

### 性能优势说明

| 指标 | 普通 Mesh 数组 | InstancedMesh + 适配器 |
|------|---------------|------------------------|
| Draw Call 数量 | 1000 次 | **1 次** |
| 内存占用 | 高（每个 Mesh 独立对象） | **低**（共享几何体/材质） |
| 动画代码复杂度 | 简单（直接操作属性） | **同样简单**（代理对象操作） |
| 适合实例数量 | &lt; 100 个 | **100 - 100,000 个** |

### 关键 API 参数说明

| API | 参数 | 返回值 | 说明 |
|-----|------|--------|------|
| `three.getInstances(mesh)` | `instancedMesh: InstancedMesh` | `InstancedMeshProxy[]` | 获取所有实例的代理对象数组，数量与 InstancedMesh 构造参数一致 |
| `three.getInstances(mesh, count)` | `instancedMesh, count: number` | `InstancedMeshProxy[]` | 获取前 `count` 个实例的代理（以官方文档为准） |
| 代理对象属性 | `x/y/z/rotateX/Y/Z/scale/color/opacity` | - | 与普通 Mesh 一样支持所有扁平化属性 |

### 注意事项

1. **初始化矩阵**：创建 InstancedMesh 后，需要先初始化每个实例的矩阵（如示例中 `setMatrixAt` 设置初始位置），再调用 `getInstances()`
2. **性能边界**：虽然 InstancedMesh 性能优异，但 JavaScript 驱动的属性插值仍有开销——10,000+ 实例的复杂动画可能需要考虑 GPU 驱动方案（如 Shader 动画）
3. **实例颜色**：代理对象支持 `color` 属性动画，适配器自动调用 `setColorAt()` 并设置 `instanceColor.needsUpdate`
4. **stagger 配合使用**：`getInstances()` 返回的数组完美支持 Anime.js 的 stagger 功能，可以轻松做出波浪、辐射等批量动画效果
5. **不支持几何体差异**：所有实例共享同一个 Geometry 和 Material，这是 InstancedMesh 本身的限制——如果需要不同形状/材质，仍需使用多个 Mesh

---

## 特性5：3D Stagger（三维空间交错动画）

### 功能说明

3D Stagger 在原有 2D stagger 基础上扩展到三维空间，支持 `grid: [x, y, z]` 三维网格布局、`from` 起始位置控制、`jitter` 随机抖动、`seed` 随机种子可复现，实现真正的 3D 空间感知交错动画。

传统 stagger 只按数组索引线性计算延迟，无法感知物体在 3D 空间中的位置关系——3D stagger 可以根据物体在三维网格中的坐标计算延迟，做出从中心向外扩散、波浪传播、球面辐射等具有空间感的交错效果。

### 解决的痛点

| 原生痛点 | 具体表现 |
|---------|---------|
| **Stagger 局限于 2D** | 原生或其他动画库的交错动画主要面向 DOM 2D 布局，缺乏 3D 空间网格交错能力 |
| **按索引而非空间位置** | 只能按数组顺序延迟，无法实现"离中心越近越先开始"这种基于空间位置的延迟 |
| **随机效果不可复现** | 加随机扰动后每次运行结果都不一样，调试困难、视觉一致性无法保证 |
| **3D 波浪效果难实现** | 要做沿 XYZ 轴传播的波浪动画，需要手动计算每个物体的延迟，代码复杂 |

### 核心参数详解

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `grid` | `[number, number, number]` | - | **必填**，三维网格尺寸 `[xCount, yCount, zCount]`，声明物体在 3D 空间中的网格排列方式 |
| `from` | `string \| number` | `'start'` | 起始位置：`'center'`（中心）、`'start'`（第一个）、`'end'`（最后一个）、`'random'`（随机）或具体索引数字 |
| `each` | `number` | - | 每个实例之间的基础延迟时间（毫秒） |
| `jitter` | `number` | `0` | 随机扰动量，范围 `0-1`：`0` 为完全规则网格延迟，`1` 为完全随机，中间值让交错既有规律又有有机感 |
| `seed` | `number` | - | 随机种子，相同的 seed 保证每次运行 jitter 结果一致，便于调试和视觉一致性 |
| `axis` | `string` | - | （以官方文档为准）限制只在特定轴上产生延迟，如 `'x'`、`'y'`、`'z'` |

### 代码示例 - 3D 网格粒子交错入场动画

```javascript
import { animate, stagger } from 'animejs';
import { three } from '@animejs/three';

const gridSize = 8;
const spacing = 0.8;
const meshes = [];

for (let x = 0; x &lt; gridSize; x++) {
  for (let y = 0; y &lt; gridSize; y++) {
    for (let z = 0; z &lt; gridSize; z++) {
      const mesh = new THREE.Mesh(
        new THREE.BoxGeometry(0.5, 0.5, 0.5),
        new THREE.MeshStandardMaterial({
          color: new THREE.Color().setHSL((x + y + z) / (gridSize * 3), 0.8, 0.5)
        })
      );
      mesh.position.set(
        (x - gridSize / 2) * spacing,
        (y - gridSize / 2) * spacing,
        (z - gridSize / 2) * spacing
      );
      meshes.push(mesh);
      scene.add(mesh);
    }
  }
}

animate(meshes, {
  scale: [0.1, 1],
  rotateX: 180,
  rotateY: 180,
  opacity: [0, 1],
  duration: 1500,
  delay: stagger({
    grid: [gridSize, gridSize, gridSize],
    from: 'center',
    each: 15,
    jitter: 0.3,
    seed: 42
  }),
  ease: 'backOut(1.7)',
  loop: true,
  alternate: true
}, three);
```

### 代码示例 - 球面辐射状交错（自定义 stagger 函数）

除了 grid 模式，stagger 还支持函数形式，完全自定义延迟逻辑：

```javascript
animate(meshes, {
  y: (el, i) =&gt; Math.sin(i * 0.1) * 2,
  duration: 2000,
  delay: stagger((_, i, total) =&gt; {
    return i / total * 500;
  }),
  loop: true,
  ease: 'sineInOut'
}, three);
```

### from 参数效果对比

| `from` 值 | 视觉效果 | 适用场景 |
|----------|---------|---------|
| `'start'` | 从数组第一个元素开始，依次向后延迟 | 线性序列动画、瀑布流效果 |
| `'end'` | 从数组最后一个元素开始，反向延迟 | 退场动画、从后往前的波浪 |
| `'center'` | 从网格中心开始，向外辐射扩散 | 爆炸效果、点击反馈、波纹扩散 |
| `'random'` | 完全随机起始点（需要 jitter 配合） | 有机感、粒子飘散、混乱美学 |
| `number`（如 `42`） | 从指定索引的元素开始 | 精确控制、特定元素触发动画 |

### 注意事项

1. **mesh 排列顺序要与 grid 对应**：使用 grid 模式时，meshes 数组的顺序必须和网格坐标一一对应——即外层循环 x，中层 y，内层 z 的顺序推入数组，否则空间位置计算错误
2. **seed 保证可复现**：调试时务必设置 seed，这样每次刷新页面随机抖动都一致，便于观察和调整；最终发布可以保留 seed 保证视觉一致性，或去掉 seed 每次都有变化
3. **jitter 取值建议**：`0.1-0.4` 的 jitter 值通常效果最好——既有网格交错的整体规律，又有自然的随机变化，不会太死板也不会太乱
4. **each 是基础单位**：`each` 是相邻网格点之间的延迟差，总延迟 = 空间距离 × each + jitter 扰动；网格越大 total 延迟越长，注意调整 each 或使用 `start`/`end` 限制
5. **与 InstancedMesh 完美配合**：3D stagger 最强大的用法是和 `getInstances()` 返回的实例数组配合，轻松做出上千实例的空间波浪动画——这是原生 Three.js 需要写大量代码才能实现的效果

---

## 五大特性协同作用

五大特性不是孤立的，它们可以组合使用产生强大的表达能力：

| 组合场景 | 特性组合 | 效果 |
|---------|---------|------|
| **粒子波浪入场** | 特性4（InstancedMesh）+ 特性5（3D Stagger）+ 特性1（属性映射） | 上千个立方体从中心波浪式缩放旋转入场，1个 draw call |
| **CSS风格卡片悬浮** | 特性2（transforms/skew/transformOrigin）+ 特性1（opacity/position） | 完全复用CSS动画思维写3D卡片交互 |
| **Shader驱动波浪** | 特性3（uniforms动画）+ 特性5（3D stagger） | Anime.js驱动Shader参数做平面波浪，同时其他物体做交错动画 |
| **材质渐变序列** | 特性3（颜色/metalness）+ Anime.js timeline | 材质属性随时间线分段变化，做出电影级转场 |

&gt; 💡 **核心记忆点**：这五大特性围绕一个共同目标——**让前端开发者用写CSS动画的直觉，就能写出高性能的3D动画**。属性映射解决"怎么访问"，扩展transform解决"怎么变换"，材质uniforms解决"怎么渲染"，InstancedMesh解决"怎么批量"，3D stagger解决"怎么编排节奏"。

---

> **上一章**：[第 02 章 — 核心概念 ←](02-core-concepts.md)  
> **下一章**：[第 04 章 — 实战案例 →](04-practical-examples.md)
