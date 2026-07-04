---
id: "animejs-threejs-adapter-analysis"
title: "Anime.js 4.5 + Three.js 适配器学习分析"
category: "learning"
tags: ["animejs", "threejs", "3d-animation", "webgl", "adapter-pattern", "前端动画", "javascript", "动画库"]
date: "2026-07-04"
status: "stable"
author: "SpecWeave"
summary: "学习分析《Anime.js 4.5 + Three.js，前端3D动画王炸组合来了！》一文：Anime.js 4.5 推出官方 Three.js 适配器，通过适配器模式、API扁平化和前端语法糖，解决Three.js动画六大痛点，让3D动画写起来像CSS transform一样简单。"
source:
  title: "Anime.js 4.5 + Three.js，前端3D动画王炸组合来了！"
  author: "认真努力的小四子"
  url: "https://mp.weixin.qq.com/s/G-vKOJOgauyaESAOJStDEQ"
  platform: "微信公众号"
---

# Anime.js 4.5 + Three.js 适配器学习分析

> **一句话引言**：Anime.js 4.5 带来了官方 Three.js 适配器，核心设计理念是——**Three.js 负责渲染世界，Anime.js 负责驱动世界**，让 3D 动画写起来像 CSS transform 一样直观，官方称可减少约 50% 的动画代码量。

---

## 文章基本信息

| 字段 | 内容 |
|------|------|
| **原文标题** | Anime.js 4.5 + Three.js，前端3D动画王炸组合来了！ |
| **作者** | 认真努力的小四子 |
| **来源** | 微信公众号 |
| **原文链接** | https://mp.weixin.qq.com/s/G-vKOJOgauyaESAOJStDEQ |
| **主题** | Anime.js 4.5 Three.js adapter |
| **核心内容** | 详解 Anime.js 4.5 新增的 Three.js 适配器的五大功能特性、解决的痛点、代码对比与适用场景 |

**文章脉络**：文章首先指出原生 Three.js 动画开发的六大痛点，然后介绍 Anime.js 4.5 适配器如何通过设计模式解决这些问题，接着逐一拆解五大核心功能（属性扁平化、扩展变换、材质动画、实例化网格、三维交错），最后进行价值分析与适用场景总结。

---

## 目录导航系统(TOC)

- [文章基本信息](#文章基本信息)
- [目录导航系统TOC](#目录导航系统toc)
- [网页结构布局分析](#网页结构布局分析)
- [核心观点提炼](#核心观点提炼)
- [关键技术要点详解](#关键技术要点详解)
  - [1. Object properties（属性扁平化映射）](#1-object-properties属性扁平化映射)
  - [2. Extended transforms（CSS transform风格3D变换）](#2-extended-transformscss-transform风格3d变换)
  - [3. Materials & uniforms（材质与Shader参数动画）](#3-materials--uniforms材质与shader参数动画)
  - [4. Instanced meshes（实例化网格批量动画）](#4-instanced-meshes实例化网格批量动画)
  - [5. 3D stagger（三维空间交错动画）](#5-3d-stagger三维空间交错动画)
- [信息价值与实用性分析](#信息价值与实用性分析)
- [相关资源](#相关资源)
- [参考资料](#参考资料)
- [Changelog](#changelog)

---

## 网页结构布局分析

文章共 **8 个章节**，按照「问题提出 → 解决方案 → 功能拆解 → 价值总结」的经典技术文章逻辑组织：

| 序号 | 章节标题 | 组织逻辑定位 |
|------|----------|-------------|
| 1 | 开篇引言 | **引入**：点明主题——Anime.js 4.5 + Three.js 是前端3D动画王炸组合 |
| 2 | Three.js动画痛点 | **问题提出**：列举原生Three.js动画开发的6大核心痛点，建立问题认知 |
| 3 | Anime.js解决方案总览 | **方案提出**：介绍适配器模式+API扁平化+前端语法糖的整体解决思路 |
| 4 | Object properties 详解 | **功能拆解1**：属性扁平化映射功能，解决属性嵌套分散问题 |
| 5 | Extended transforms 详解 | **功能拆解2**：CSS transform风格3D变换，含skew/transformOrigin等 |
| 6 | Materials & uniforms 详解 | **功能拆解3**：材质与Shader参数动画，颜色自动解析、uniforms按名访问 |
| 7 | Instanced meshes + 3D stagger 详解 | **功能拆解4-5**：实例化网格批量动画与三维空间交错动画 |
| 8 | 价值总结与适用场景 | **总结**：分析实际价值、适用场景、局限性，给出"减少50%代码"的依据 |

---

## 核心观点提炼

### 核心命题

**让 Three.js 动画写起来更像 CSS transform**——**Three.js 负责渲染世界，Anime.js 负责驱动世界**。

这一设计理念体现了**关注点分离**原则：Three.js 作为 3D 渲染引擎专注于场景、几何体、材质、光照等渲染层职责；Anime.js 作为动画引擎专注于时间线、缓动、插值、交错等动画层职责，二者通过**适配器模式**无缝对接。

### Three.js 动画 6 大痛点

| 痛点编号 | 痛点描述 | 具体表现 |
|---------|---------|---------|
| 1 | **属性嵌套分散** | 位置在`mesh.position`、旋转在`mesh.rotation`、缩放在`mesh.scale`，属性分散在不同嵌套对象，动画代码割裂 |
| 2 | **Timeline代码冗余** | 原生需要手动管理`requestAnimationFrame`、时钟对象、时间差计算，复杂时间线编排代码量大 |
| 3 | **手动单位转换** | 角度需要手动转弧度（`Math.PI / 180`）、颜色需要手动处理色彩空间转换，增加心智负担 |
| 4 | **材质动画繁琐** | 材质属性（颜色、透明度、粗糙度等）动画需要深入`mesh.material`层级，Shader uniforms访问更复杂 |
| 5 | **实例化网格复杂** | `InstancedMesh`需要手动维护矩阵数组，批量动画时代码极易出错且难以维护 |
| 6 | **Stagger局限于2D** | 原生或其他动画库的交错动画（stagger）主要面向DOM 2D布局，缺乏3D空间网格交错能力 |

### Anime.js 解决思路

三大核心策略：

1. **适配器模式（Adapter Pattern）**：官方提供`@animejs/three`适配器包，内部处理Three.js对象与Anime.js动画系统的兼容层，用户无需关心底层适配逻辑
2. **API扁平化**：将分散在多层嵌套的3D属性（position/rotation/scale/material）统一扁平化为动画目标的直接属性，写动画像操作普通JS对象一样简单
3. **前端语法糖**：引入前端开发者熟悉的CSS transform概念（translateX/Y/Z、rotateX/Y/Z、scale、skew、transformOrigin），降低学习门槛，实现知识复用

### 新旧写法代码对比

**原生 Three.js 写法**（手动管理动画循环）：

```javascript
const mesh = new THREE.Mesh(geometry, material);

function animate() {
  requestAnimationFrame(animate);
  
  const time = clock.getElapsedTime();
  
  mesh.position.x = Math.sin(time) * 2;
  mesh.position.y = Math.cos(time * 0.5) * 1;
  mesh.rotation.x = time * 0.5;
  mesh.rotation.z = Math.sin(time) * 0.3;
  mesh.scale.setScalar(1 + Math.sin(time * 2) * 0.2);
  
  mesh.material.color.setHSL(time * 0.1, 0.8, 0.5);
  mesh.material.opacity = 0.5 + Math.sin(time) * 0.5;
  
  renderer.render(scene, camera);
}
animate();
```

**Anime.js 4.5 + Three.js 适配器写法**：

```javascript
import { animate } from 'animejs';
import { three } from '@animejs/three';

const mesh = new THREE.Mesh(geometry, material);

animate(mesh, {
  x: Math.sin('*') * 2,
  y: Math.cos('*' * 0.5) * 1,
  rotateX: '*' * 0.5,
  rotateZ: Math.sin('*') * 0.3,
  scale: 1 + Math.sin('*' * 2) * 0.2,
  color: ['hsl(0, 80%, 50%)', 'hsl(360, 80%, 50%)'],
  opacity: [0, 1],
  duration: Infinity,
  loop: true,
  ease: 'linear'
}, three);
```

**对比要点**：
- 无需手动调用`requestAnimationFrame`和管理时钟
- 属性扁平化，直接写`x`/`y`/`rotateX`而非`mesh.position.x`/`mesh.rotation.x`
- 内置时间线、缓动、循环等动画能力
- 颜色支持多种格式自动解析
- 代码量显著减少，可读性大幅提升

---

## 关键技术要点详解

### 1. Object properties（属性扁平化映射）

| 维度 | 说明 |
|------|------|
| **功能描述** | 将Three.js Object3D及其子类（Mesh、Group、Light等）上分散在多层嵌套对象中的动画属性，统一映射为Anime.js可直接访问的扁平化属性 |
| **解决的问题** | **属性嵌套分散痛点**——无需再写`mesh.position.x`、`mesh.rotation.y`这种深层链式访问，直接在动画配置中写`x`、`rotateY`即可 |
| **自动映射的属性** | `x/y/z`（position）、`rotateX/rotateY/rotateZ`（rotation，自动弧度/角度转换）、`scale`（支持单值或分轴）、`opacity`（material透明度）、`visible`等 |

**代码示例**：

```javascript
import { animate, stagger } from 'animejs';
import { three } from '@animejs/three';

const group = new THREE.Group();
scene.add(group);

for (let i = 0; i < 20; i++) {
  const mesh = new THREE.Mesh(
    new THREE.BoxGeometry(0.5, 0.5, 0.5),
    new THREE.MeshStandardMaterial({ color: 0xffffff })
  );
  mesh.position.set(
    (Math.random() - 0.5) * 10,
    (Math.random() - 0.5) * 10,
    (Math.random() - 0.5) * 10
  );
  group.add(mesh);
}

animate(group.children, {
  x: '+=2',
  y: '-=1',
  rotateX: 360,
  rotateY: 180,
  scale: 1.5,
  duration: 1000,
  stagger: 50,
  ease: 'outExpo'
}, three);
```

> **关键特性**：支持对**对象数组**批量动画（如上面的`group.children`），自动遍历并应用到每个元素，类似DOM中的`querySelectorAll`批量动画。

---

### 2. Extended transforms（CSS transform风格3D变换）

| 维度 | 说明 |
|------|------|
| **功能描述** | 引入前端开发者熟悉的CSS transform语法糖到3D空间，新增`translateX/Y/Z`、`rotateX/Y/Z`、`scaleX/Y/Z`、`skewX/Y`、`transformOrigin`等属性 |
| **解决的问题** | **知识复用问题**——前端开发者可以直接复用CSS transform的思维模型写3D动画，降低学习曲线；同时解决了**变换原点控制**难题 |
| **核心新增属性** | **`skewX`/`skewY`**：3D空间中的斜切变换（原生Three.js无直接支持）；**`transformOrigin`**：变换中心点（类似CSS的transform-origin） |

**代码示例 - skew斜切变换**：

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
  duration: 1500,
  ease: 'inOutQuad',
  loop: true,
  alternate: true
}, three);
```

**代码示例 - transformOrigin变换原点**：

```javascript
animate(mesh, {
  rotateZ: 360,
  transformOrigin: { x: 1, y: 0.5, z: 0 },
  duration: 2000,
  ease: 'linear',
  loop: true
}, three);
```

> **设计巧思**：CSS开发者对`transform-origin`的心智模型可以100%迁移到3D场景——设置元素的旋转/缩放中心点，不用再手动调整pivot或嵌套Group来实现。

---

### 3. Materials & uniforms（材质与Shader参数动画）

| 维度 | 说明 |
|------|------|
| **功能描述** | 自动遍历材质属性，支持颜色自动解析（HEX/RGB/HSL/命名色）、透明度、金属度、粗糙度等材质参数动画；ShaderMaterial的**uniforms变量可直接按名称访问动画** |
| **解决的问题** | **材质动画繁琐痛点**——不用再写`mesh.material.color.setRGB(...)`或手动解析色彩空间；**Shader uniforms动画痛点**——不用在渲染循环中逐帧更新uniform值 |
| **支持的材质属性** | `color`（自动解析多格式）、`opacity`、`metalness`、`roughness`、`emissive`、`emissiveIntensity`等；支持`transparent: true`自动处理 |

**代码示例 - 颜色与材质属性动画**：

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

**代码示例 - Shader uniforms动画**：

```javascript
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
  `
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

> **关键突破**：直接对`shaderMaterial`对象做动画，uniform变量名（`uTime`、`uAmplitude`、`uFrequency`）就是动画属性名，Anime.js适配器自动识别并更新`uniform.value`，无需在`requestAnimationFrame`中手动赋值。

---

### 4. Instanced meshes（实例化网格批量动画）

| 维度 | 说明 |
|------|------|
| **功能描述** | 为`InstancedMesh`提供**`getInstances()`**辅助方法，自动生成可独立动画的虚拟实例对象数组，每个实例像普通Mesh一样独立控制位置、旋转、缩放、颜色 |
| **解决的问题** | **实例化网格复杂痛点**——不用再手动维护`Matrix4`数组、不用手动调用`setMatrixAt`/`instanceMatrix.needsUpdate`，每个实例的动画代码和普通Mesh完全一致 |
| **核心API** | `three.getInstances(instancedMesh, count?)`：返回可动画的实例代理对象数组，支持stagger、时间线等所有Anime.js特性 |

**代码示例 - InstancedMesh批量动画**：

```javascript
import { animate, stagger } from 'animejs';
import { three } from '@animejs/three';

const count = 1000;
const geometry = new THREE.BoxGeometry(0.2, 0.2, 0.2);
const material = new THREE.MeshStandardMaterial();
const instancedMesh = new THREE.InstancedMesh(geometry, material, count);

for (let i = 0; i < count; i++) {
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

> **性能优势**：`InstancedMesh`本身是Three.js的性能优化方案（1个draw call渲染N个物体），Anime.js适配器保留这一性能优势的同时，让批量动画代码和普通Mesh数组一样简单。

---

### 5. 3D stagger（三维空间交错动画）

| 维度 | 说明 |
|------|------|
| **功能描述** | 在原有2D stagger基础上扩展到三维空间，支持`grid: [x, y, z]`三维网格布局、`jitter`随机抖动、`seed`随机种子可复现，实现真正的3D空间感知交错动画 |
| **解决的问题** | **Stagger局限于2D痛点**——原生stagger按数组索引或DOM位置交错，无法感知3D空间中的XYZ位置关系；3D stagger可以按三维网格坐标计算交错延迟 |
| **核心参数** | **`grid: [x, y, z]`**：三维网格尺寸；**`jitter`**：随机抖动量（0-1）；**`seed`**：随机种子（保证相同seed结果一致）；**`from`**：起始点（'center'/'start'/'end'/'random'或索引） |

**代码示例 - 3D网格交错动画**：

```javascript
import { animate, stagger } from 'animejs';
import { three } from '@animejs/three';

const gridSize = 8;
const spacing = 0.8;
const meshes = [];

for (let x = 0; x < gridSize; x++) {
  for (let y = 0; y < gridSize; y++) {
    for (let z = 0; z < gridSize; z++) {
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

**代码示例 - 球面辐射状交错**：

```javascript
animate(meshes, {
  y: (el, i) => Math.sin(i * 0.1) * 2,
  duration: 2000,
  delay: stagger((_, i, total) => {
    return i / total * 500;
  }),
  loop: true,
  ease: 'sineInOut'
}, three);
```

> **设计亮点**：`seed`参数保证随机结果可复现，这对调试和视觉一致性很重要；`jitter`参数让交错既有规律又不死板，适合做有机感的粒子动画。

---

## 信息价值与实用性分析

### 对前端开发者的实际价值

| 价值维度 | 具体说明 |
|---------|---------|
| **降低3D开发门槛** | 前端开发者无需深入理解Three.js动画底层（矩阵、欧拉角、四元数、弧度转换），用熟悉的CSS transform思维模型就能写3D动画 |
| **知识复用率高** | CSS动画/Anime.js 2D动画的知识可以直接迁移到3D场景——stagger、timeline、ease、loop等概念完全一致，学习成本极低 |
| **开发效率显著提升** | 官方称**减少约50%代码量**，尤其在复杂时间线、批量动画、Shader动画场景下，代码缩减比例更高；同时减少手动管理动画循环带来的BUG |
| **调试友好** | 动画逻辑集中在Anime.js配置对象中，而非散落在渲染循环各处；支持Anime.js DevTools时间线调试（如有）；属性名直观，代码可读性强 |

### 适用场景

| 场景类型 | 典型用例 | 适配度 |
|---------|---------|--------|
| **3D Hero Section** | 官网首页3D英雄区域、产品展示3D Banner、品牌宣传页的入场/交互动画 | ⭐⭐⭐⭐⭐ |
| **WebGL展示页面** | 作品集3D展示、营销活动H5 3D页面、艺术装置Web版 | ⭐⭐⭐⭐⭐ |
| **交互式产品模型** | 电商3D商品展示、产品3D配置器、3D看车/看房的交互动画 | ⭐⭐⭐⭐ |
| **3D数据可视化** | 3D图表、三维城市数据展示、科学可视化的粒子/柱状/点云动画 | ⭐⭐⭐⭐ |
| **粒子批量动画** | 星空、烟花、粒子流体、群体行为（鸟群/鱼群）等大量实例动画 | ⭐⭐⭐⭐⭐ |
| **3D微交互** | 按钮hover 3D反馈、UI元素3D转场、卡片悬浮3D效果 | ⭐⭐⭐⭐ |
| **创意编程/Generative Art** | CodePen风格创意作品、生成艺术、互动装置的快速原型开发 | ⭐⭐⭐⭐⭐ |

### 局限性分析

| 局限性 | 详细说明 |
|-------|---------|
| **不是Three.js动画替代品** | 定位是**补充增强**而非替代——对于骨骼动画、物理动画（需结合Cannon.js/Ammo.js）、复杂IK动画、变形目标（Morph Targets）高级面部动画等，仍需原生或其他专业方案 |
| **复杂动画覆盖不全** | 当前版本主要覆盖transform、材质、instancing三类高频场景；对于骨骼动画（`SkinnedMesh`/`Bone`）、变形目标（`morphTargetInfluences`）、灯光动画（除基础属性外）等场景支持有限或需要手动适配 |
| **性能开销考量** | 对于超大规模（10万+实例）粒子系统，JavaScript驱动的属性插值仍有性能瓶颈，此时应优先考虑GPU驱动的Shader动画（但即使如此，Anime.js可用来驱动Shader uniforms参数） |
| **生态成熟度待观察** | 作为v4.5刚推出的新特性，社区资源、教程、最佳实践、第三方插件生态尚在早期；与React Three Fiber（R3F）、Vue Three等上层框架的集成方案还需要时间沉淀 |
| **学习天花板** | 降低入门门槛的同时，若开发者只停留在Anime.js抽象层，可能难以深入掌握Three.js底层动画概念（四元数、矩阵变换、动画混合器等），遇到复杂问题时排查能力受限 |
| **版本耦合风险** | 与Anime.js v4.5+版本强绑定，API稳定性需要时间验证；项目需要同时维护Anime.js和Three.js两个依赖的版本兼容 |

### "减少50%代码"说法的依据

这一说法主要基于以下几个维度的代码量缩减：

1. **消除动画循环样板代码**：`requestAnimationFrame`+`clock.getElapsedTime()`+`renderer.render()`的循环框架代码约10-15行，使用Anime.js后完全消失
2. **属性访问扁平化**：`mesh.position.x`→`x`、`mesh.material.color.setHSL()`→`color: 'hsl(...)'`，每行减少约30%-50%字符数
3. **时间线编排简化**：复杂的序列动画/交错动画如果用原生实现需要手写delay/onComplete回调链，Anime.js timeline/stagger声明式配置减少约60%代码
4. **批量动画统一处理**：InstancedMesh的矩阵管理代码从约20行循环缩减为`getInstances()`一行调用
5. **自动单位/格式转换**：角度↔弧度、颜色格式解析、自动设置`transparent: true`等，消除散落的转换代码

**实际效果**：在简单动画场景代码缩减约30%-40%，复杂时间线+批量动画+Shader动画组合场景可达到50%以上的代码缩减。

---

## 相关资源

### 官方资源

- **GitHub Release**: https://github.com/juliangarnier/anime/releases/tag/v4.5.0
- **Anime.js 官网**: https://animejs.com/
- **Three.js 官网**: https://threejs.org/
- **@animejs/three 适配器文档**: https://animejs.com/documentation/three

### 学习资源

- **原文链接**: https://mp.weixin.qq.com/s/G-vKOJOgauyaESAOJStDEQ
- **Anime.js v4 官方文档**: https://animejs.com/documentation/
- **Three.js 动画指南**: https://threejs.org/manual/#en/animation

---

## 参考资料

1. 认真努力的小四子. *Anime.js 4.5 + Three.js，前端3D动画王炸组合来了！*. 微信公众号. https://mp.weixin.qq.com/s/G-vKOJOgauyaESAOJStDEQ
2. Julian Garnier. *Anime.js v4.5.0 Release Notes*. GitHub. https://github.com/juliangarnier/anime/releases/tag/v4.5.0
3. Anime.js 官方文档. *Three.js Adapter Documentation*. https://animejs.com/documentation/three
4. Three.js 官方文档. *InstancedMesh / Object3D / Material*. https://threejs.org/docs/

---

## Changelog

<!-- changelog -->
- 2026-07-04 | create | 初始创建：学习分析《Anime.js 4.5 + Three.js，前端3D动画王炸组合来了！》一文，梳理适配器模式设计理念、六大痛点、五大功能特性、代码对比、价值与局限性分析（v1.0）
