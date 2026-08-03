---
id: "animejs-threejs-adapter-wiki-quickstart"
title: "快速开始"
category: "learning"
tags: ["animejs", "threejs", "quickstart", "installation"]
date: "2026-08-03"
status: "active"
author: "SpecWeave"
source: "spec:animejs-threejs-adapter-wiki"
---

# 快速开始

本章节将引导你从零开始搭建 Anime.js 4.5 + Three.js 适配器开发环境，并完成你的第一个 3D 动画示例。

---

## 环境准备

在开始之前，请确保你的开发环境满足以下要求：

| 依赖 | 版本要求 | 说明 |
|------|---------|------|
| **Node.js** | 16.0+ | 推荐使用 LTS 版本，用于 npm/yarn/pnpm 包管理方式 |
| **Anime.js** | 4.5+ | 必须使用 4.5 或更高版本，Three.js 适配器在此版本首次引入 |
| **Three.js** | 任意稳定版 | 推荐 r150+，适配器兼容 Three.js 主流稳定版本 |

你可以选择以下任意一种开发方式：
- **模块化开发**：使用 Vite、Webpack、Rollup 等构建工具，通过 npm/yarn/pnpm 安装依赖
- **快速原型**：直接在 HTML 文件中通过 CDN 引入，无需构建工具，适合 CodePen、JSFiddle 等在线演示

---

## 安装方式

### 使用 npm

```bash
npm install three animejs@latest
```

> ⚠️ 注意：适配器包 `@animejs/three` 的引入方式请以官方文档为准。部分版本可能已集成在 `animejs` 主包中，或需要单独安装。

### 使用 yarn

```bash
yarn add three animejs
```

### 使用 pnpm

```bash
pnpm add three animejs
```

### CDN 方式（无需构建工具）

如果你想快速验证效果或在在线代码平台中使用，可以直接通过 CDN 引入：

**使用 jsDelivr：**

```html
<!-- Three.js -->
<script src="https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.min.js"></script>
<!-- Anime.js 4.5+ -->
<script src="https://cdn.jsdelivr.net/npm/animejs@4.5.0/lib/anime.min.js"></script>
<!-- 适配器（具体CDN路径以官方发布为准） -->
```

**使用 unpkg：**

```html
<!-- Three.js -->
<script src="https://unpkg.com/three@0.160.0/build/three.min.js"></script>
<!-- Anime.js 4.5+ -->
<script src="https://unpkg.com/animejs@4.5.0/lib/anime.min.js"></script>
```

> 💡 CDN 方式下，全局对象通常为 `THREE` 和 `anime`。适配器的全局挂载方式请以官方文档为准。

---

> ⚠️ **API参考提示**：示例代码基于Anime.js 4.5官方文档整理，实际使用时请以最新官方文档（https://animejs.com/documentation/three）为准。适配器API可能随版本更新而变化。

---

## 第一个 3D 动画：旋转的彩色立方体

下面我们通过一个经典的"旋转彩色立方体"示例，对比原生 Three.js 写法与 Anime.js 适配器写法的差异。

### 方式一：原生 Three.js 写法

这是不使用任何动画库时的标准 Three.js 动画实现方式——你需要手动管理动画循环、时钟对象和属性更新。

```javascript
import * as THREE from 'three';

// 1. 初始化场景
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x1a1a2e);

// 2. 初始化相机（透视相机）
const camera = new THREE.PerspectiveCamera(
  75,
  window.innerWidth / window.innerHeight,
  0.1,
  1000
);
camera.position.z = 5;

// 3. 初始化渲染器
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
document.body.appendChild(renderer.domElement);

// 4. 创建立方体几何体和材质
const geometry = new THREE.BoxGeometry(2, 2, 2);
const material = new THREE.MeshStandardMaterial({
  color: 0x00ff88,
  metalness: 0.3,
  roughness: 0.4
});

// 5. 创建网格对象并添加到场景
const cube = new THREE.Mesh(geometry, material);
scene.add(cube);

// 6. 添加光源（环境光+方向光）
const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
scene.add(ambientLight);

const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
directionalLight.position.set(5, 5, 5);
scene.add(directionalLight);

// 7. 创建时钟对象用于计算时间差
const clock = new THREE.Clock();

// 8. 手动编写动画循环
function animate() {
  requestAnimationFrame(animate);

  // 获取已流逝的时间（秒）
  const elapsedTime = clock.getElapsedTime();

  // 手动更新旋转属性（需要嵌套访问 position/rotation）
  cube.rotation.x = elapsedTime * 0.5;
  cube.rotation.y = elapsedTime * 0.8;

  // 手动更新颜色（需要调用 material.color.setHSL）
  const hue = (elapsedTime * 0.1) % 1;
  cube.material.color.setHSL(hue, 0.8, 0.6);

  // 手动缩放脉动效果
  const scale = 1 + Math.sin(elapsedTime * 2) * 0.1;
  cube.scale.set(scale, scale, scale);

  // 手动调用渲染
  renderer.render(scene, camera);
}

// 启动动画循环
animate();

// 窗口大小自适应
window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});
```

### 方式二：Anime.js 适配器写法

使用 Anime.js 适配器后，你不再需要手动管理 `requestAnimationFrame` 和时钟对象，属性访问也被扁平化，代码更简洁直观。

```javascript
import * as THREE from 'three';
import { animate } from 'animejs';
import { three } from '@animejs/three'; // 具体导入路径以官方文档为准

// 1. 初始化场景（与原生写法相同）
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x1a1a2e);

// 2. 初始化相机（与原生写法相同）
const camera = new THREE.PerspectiveCamera(
  75,
  window.innerWidth / window.innerHeight,
  0.1,
  1000
);
camera.position.z = 5;

// 3. 初始化渲染器（与原生写法相同）
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
document.body.appendChild(renderer.domElement);

// 4. 创建立方体几何体和材质（与原生写法相同）
const geometry = new THREE.BoxGeometry(2, 2, 2);
const material = new THREE.MeshStandardMaterial({
  color: 0x00ff88,
  metalness: 0.3,
  roughness: 0.4,
  transparent: true
});

// 5. 创建网格对象并添加到场景（与原生写法相同）
const cube = new THREE.Mesh(geometry, material);
scene.add(cube);

// 6. 添加光源（与原生写法相同）
const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
scene.add(ambientLight);

const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
directionalLight.position.set(5, 5, 5);
scene.add(directionalLight);

// 7. 使用 Anime.js 驱动动画——这是核心差异部分
animate(cube, {
  // 属性扁平化：直接写 rotateX/rotateY，无需 cube.rotation.x
  rotateX: 360,
  rotateY: 360,
  // 颜色动画：支持 HSL/HEX/RGB 多种格式，自动色彩空间转换
  color: ['hsl(0, 80%, 60%)', 'hsl(360, 80%, 60%)'],
  // 缩放脉动：支持数组形式 [起始值, 结束值]
  scale: [0.9, 1.1],
  // 动画配置
  duration: 4000,
  ease: 'linear',
  loop: true,
  alternate: false,
  // 自动渲染：适配器会在每一帧自动调用 renderer.render
  // 具体自动渲染配置以官方文档为准，部分场景可能需要手动配置renderer
  onUpdate: () => {
    renderer.render(scene, camera);
  }
}, three); // 第三个参数传入 three 适配器

// 窗口大小自适应（与原生写法相同）
window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});
```

> 💡 **关键说明**：
> - `'*'` 是 Anime.js 内置的时间单位标记，代表当前动画的时间进度（0-1）
> - 角度单位默认使用度（degree），适配器自动转换为 Three.js 需要的弧度（radian）
> - 颜色支持 `'hsl(...)'`、`'#ff0000'`、`'rgb(...)'` 等多种格式，无需手动转换
> - 第三个参数 `three` 是适配器，告诉 Anime.js 如何解析 Three.js 对象属性

---

## 代码对比说明

通过上面的示例，我们可以清晰看到 Anime.js 适配器为我们减少了哪些样板代码（Boilerplate Code）：

| 对比维度 | 原生 Three.js 写法 | Anime.js 适配器写法 | 改进效果 |
|---------|-------------------|-------------------|---------|
| **动画循环** | 需要手动编写 `requestAnimationFrame` 递归函数 | 由 Anime.js 内部管理，无需编写 | 减少约 10-15 行循环框架代码 |
| **时钟管理** | 需要创建 `THREE.Clock` 对象并调用 `getElapsedTime()` | 内置时间系统，可直接使用 `'*'` 时间标记 | 消除时钟对象的创建和维护 |
| **属性访问** | 深层嵌套：`cube.rotation.x`、`cube.material.color.setHSL()` | 扁平化属性：`rotateX`、`color` 直接写在配置中 | 属性访问代码减少约 40%-60% |
| **单位转换** | 角度需手动转弧度（`value * Math.PI / 180`） | 自动进行度↔弧度转换，直接使用角度值 | 消除散落的单位转换代码 |
| **颜色处理** | 需要调用 `color.setHSL()`/`setRGB()` 等方法 | 支持多种颜色格式字符串，自动解析 | 颜色动画代码更直观 |
| **动画配置** | 缓动、循环、往复等效果需要手动实现 | 声明式配置：`ease`/`loop`/`alternate`/`duration` | 复杂动画效果一行配置完成 |
| **代码组织** | 动画逻辑散落在 `animate()` 函数各处 | 所有动画配置集中在一个对象中 | 可读性和可维护性大幅提升 |

### 核心差异总结

**适配器消除的样板代码类型：**

1. **循环框架代码**：`requestAnimationFrame` 递归、时钟初始化、时间差计算
2. **属性嵌套访问**：不再需要 `.position.`、`.rotation.`、`.material.` 等链式访问
3. **手动单位转换**：角度↔弧度、色彩空间转换等底层细节被封装
4. **动画基础能力**：缓动函数（easing）、循环（loop）、往复（alternate）、延迟（delay）等无需手写

**保留不变的部分：**

- Three.js 场景、相机、渲染器、几何体、材质、光源的初始化代码完全相同
- Three.js 的渲染逻辑和 WebGL 底层能力不受影响
- 你依然可以在需要时直接访问 Three.js 原生 API，二者可以混合使用

---

## 下一步

恭喜你完成了第一个 Anime.js + Three.js 3D 动画！接下来你可以继续学习：

- **属性映射详解**：了解适配器支持的所有扁平化属性及其对应关系
- **扩展变换**：学习 CSS transform 风格的 `translate`/`skew`/`transformOrigin` 用法
- **材质动画**：探索颜色、透明度、金属度、粗糙度以及 Shader uniforms 的动画
- **批量动画**：使用 `getInstances()` 高效驱动 InstancedMesh 和对象数组
- **3D 交错动画**：掌握三维空间感知的 stagger 动画技巧

---

> **上一章**：[第 00 章 — 教程总览 ←](00-overview.md)  
> **下一章**：[第 02 章 — 核心概念 →](02-core-concepts.md)
