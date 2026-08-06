---
id: "animejs-threejs-adapter-wiki-best-practices"
title: "最佳实践与常见陷阱"
category: "learning"
tags: ["animejs", "threejs", "best-practices", "performance", "tips"]
date: "2026-08-03"
status: "active"
author: "SpecWeave"
source: "spec:animejs-threejs-adapter-wiki"
---

# 最佳实践与常见陷阱

> 🎯 **本章目标**：总结 Anime.js + Three.js 适配器在实际项目中的性能优化策略、调试技巧、常见踩坑点，帮助开发者避开陷阱、写出高性能且稳定的 3D 动画代码。

---

## 目录

- [性能优化建议](#性能优化建议)
- [调试技巧](#调试技巧)
- [常见陷阱与踩坑点](#常见陷阱与踩坑点)
- [与框架集成提示](#与框架集成提示)
- [什么时候不该用适配器](#什么时候不该用适配器)

---

## 性能优化建议

> ⚡ 性能是 3D 动画的生命线。以下建议帮助你在保证视觉效果的同时，维持流畅的 60 FPS 帧率。

### 优化策略总览

| 优化策略 | 适用场景 | 性能提升 | 实现难度 |
|---------|---------|---------|---------|
| GPU Shader 动画 | 大规模粒子系统 (1万+实例) | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| InstancedMesh | 相同几何体 > 100个 | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| 避免回调中重计算 | 所有动画场景 | ⭐⭐⭐ | ⭐ |
| 不可见时暂停动画 | 页面滚动、Tab切换 | ⭐⭐⭐⭐ | ⭐⭐ |
| 资源 dispose | 场景切换、对象销毁 | ⭐⭐⭐⭐ | ⭐⭐ |

---

### 1. 大规模粒子系统：优先 GPU Shader 动画

当粒子数量超过 **10,000** 时，JavaScript（CPU）驱动的逐实例插值会成为性能瓶颈。此时应该：

- ✅ **正确做法**：使用 ShaderMaterial（着色器材质）在 GPU 上计算动画，Anime.js 仅驱动 Shader uniforms（全局参数）
- ❌ **错误做法**：用 Anime.js 逐实例驱动每个粒子的 position/rotation/scale

```javascript
// ✅ 推荐：Anime.js 驱动 uniforms，GPU 计算动画
const particleMaterial = new THREE.ShaderMaterial({
  uniforms: {
    uTime: { value: 0 },
    uSpeed: { value: 1.0 },
    uScale: { value: 1.0 }
  },
  // vertexShader 在 GPU 上计算每个粒子位置
  vertexShader: `
    uniform float uTime;
    uniform float uSpeed;
    attribute float aRandom;
    void main() {
      vec3 pos = position;
      pos.y += sin(uTime * uSpeed + aRandom * 6.28) * 2.0;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(pos, 1.0);
      gl_PointSize = 4.0;
    }
  `
});

// Anime.js 仅驱动全局 uniforms 参数
animate(particleMaterial, {
  uTime: 100,
  uSpeed: [0.5, 2.0],
  uScale: [0.5, 1.5],
  duration: 10000,
  ease: 'sineInOut',
  loop: true
}, three);
```

> 💡 **经验法则**：粒子数 < 1,000 → CPU 驱动（Anime.js 直接动画）；1,000 ~ 10,000 → 根据复杂度选择；> 10,000 → 必须 GPU Shader。

---

### 2. 超过 100 个相同几何体时，必须使用 InstancedMesh

Three.js 的 **InstancedMesh（实例化网格）** 可以用 1 个 draw call（绘制调用）渲染成百上千个相同几何体，性能提升可达数十倍。配合适配器的 `getInstances()` 方法，代码和普通 Mesh 数组一样简单：

| 方案 | 1000个Box的draw call数 | 内存占用 | 代码复杂度 |
|------|----------------------|---------|---------|
| 普通Mesh数组 | 1000 | 高 | 低 |
| InstancedMesh + getInstances() | 1 | 低 | 低 |

```javascript
// ✅ 正确：使用 InstancedMesh + getInstances()
const count = 1000;
const geometry = new THREE.BoxGeometry(0.2, 0.2, 0.2);
const material = new THREE.MeshStandardMaterial();
const instancedMesh = new THREE.InstancedMesh(geometry, material, count);

// 初始化位置
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

// 获取可动画的实例代理对象
const instances = three.getInstances(instancedMesh);

// 和普通数组一样使用 Anime.js 动画
animate(instances, {
  y: '+=5',
  rotateX: 360,
  duration: 2000,
  stagger: { each: 2, from: 'center', grid: [10, 10, 10] },
  ease: 'outElastic',
  loop: true,
  alternate: true
}, three);
```

> 💡 **判断标准**：当你发现自己在写 `for (let i = 0; i < N; i++) { new THREE.Mesh(...) }` 且 N > 100 时，立刻换成 InstancedMesh。

---

### 3. 避免在动画回调中做 Heavy Computation

Anime.js 的 `onUpdate`、`onChange` 等回调会在**每一帧**执行（60次/秒），在这些回调中执行重计算会导致帧率暴跌：

| 操作类型 | 是否适合放在动画回调中 |
|---------|----------------------|
| 简单属性赋值（`element.style.opacity = x`） | ✅ 可以 |
| 读取 DOM 布局（`offsetWidth`、`getBoundingClientRect()`） | ❌ 禁止（触发重排） |
| 复杂数学计算（矩阵运算、物理模拟） | ❌ 禁止（提前算好或用 Web Worker） |
| 创建新对象（`new THREE.Vector3()`、`new Date()`） | ❌ 禁止（GC 压力） |
| 遍历大数组（> 1000 元素） | ❌ 禁止 |
| 日志输出（`console.log`） | ❌ 禁止（生产环境） |

```javascript
// ❌ 错误：在 onUpdate 中创建对象和复杂计算
animate(mesh, {
  x: 10,
  duration: 1000,
  onUpdate: () => {
    // 每一帧都创建新的 Vector3 对象 → GC 压力！
    const tempVec = new THREE.Vector3();
    // 每一帧都遍历大数组 → 阻塞主线程！
    for (let i = 0; i < 10000; i++) {
      tempVec.add(vertices[i]);
    }
  }
}, three);

// ✅ 正确：对象复用，计算提前
const tempVec = new THREE.Vector3(); // 外部创建，复用
const precomputedData = preprocessVertices(vertices); // 提前计算

animate(mesh, {
  x: 10,
  duration: 1000,
  onUpdate: (anim) => {
    tempVec.copy(mesh.position); // 复用对象
    // 使用预计算结果
    updateWithPrecomputed(precomputedData, anim.progress);
  }
}, three);
```

---

### 4. 页面不可见时暂停动画

使用 **Intersection Observer（交叉观察器）** 和 **Page Visibility API**，在动画不可见时暂停，避免不必要的性能消耗：

```javascript
import { animate } from 'animejs';
import { three } from '@animejs/three';

const animation = animate(mesh, {
  rotateY: 360,
  duration: 2000,
  loop: true,
  ease: 'linear'
}, three);

// 方案1：Intersection Observer - 元素滚动到视口外时暂停
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      animation.play();
    } else {
      animation.pause();
    }
  });
}, { threshold: 0.1 });

observer.observe(renderer.domElement);

// 方案2：Page Visibility API - 切换到其他 Tab 时暂停
document.addEventListener('visibilitychange', () => {
  if (document.hidden) {
    animation.pause();
  } else {
    animation.play();
  }
});
```

> 📊 **性能收益**：页面在后台时暂停动画，可以将 CPU/GPU 使用率从 30-50% 降到接近 0%，同时减少笔记本电量消耗。

---

### 5. 及时 Dispose 不需要的资源，防止内存泄漏

Three.js 的几何体（Geometry）、材质（Material）、纹理（Texture）不会被自动垃圾回收，必须手动调用 `dispose()` 释放 GPU 内存：

| 资源类型 | Dispose 方法 | 遗漏后果 |
|---------|-------------|---------|
| BufferGeometry | `geometry.dispose()` | GPU 显存泄漏，页面越用越卡 |
| Material | `material.dispose()` | 材质内存泄漏，WebGL 上下文丢失 |
| Texture | `texture.dispose()` | 纹理显存泄漏 |
| RenderTarget | `renderTarget.dispose()` | 帧缓冲区泄漏 |

```javascript
// ✅ 场景切换/对象销毁时的清理模板
function disposeObject(obj) {
  if (obj.geometry) {
    obj.geometry.dispose();
  }
  if (obj.material) {
    if (Array.isArray(obj.material)) {
      obj.material.forEach(m => m.dispose());
    } else {
      obj.material.dispose();
    }
    // 清理材质上的纹理
    Object.values(obj.material).forEach(value => {
      if (value && value.isTexture) {
        value.dispose();
      }
    });
  }
  // 递归清理子对象
  if (obj.children) {
    obj.children.forEach(child => disposeObject(child));
  }
}

// 使用示例：移除并清理一个 Group
scene.remove(group);
disposeObject(group);

// 别忘了暂停和移除 Anime.js 动画！
animation.pause();
animation.remove(mesh); // 如果需要彻底移除目标
```

> ⚠️ **常见误区**：只从 scene 中 remove 对象但不 dispose，GPU 内存不会释放，长时间运行后浏览器会崩溃或标签页崩溃。

---

## 调试技巧

> 🔍 3D 动画调试比 2D 更复杂——你看不见时间线、摸不着 3D 空间坐标。掌握这些技巧能大幅提升调试效率。

### 调试工作流清单

| 步骤 | 操作 | 目的 |
|------|------|------|
| 1 | 简化场景：先隐藏其他物体，只保留调试目标 | 排除干扰因素 |
| 2 | 使用线性缓动：`ease: 'linear'`，关闭 loop/alternate | 排除缓动函数干扰 |
| 3 | 减慢速度：`duration: 10000`（10秒），逐帧观察 | 看清动画细节 |
| 4 | 添加辅助器：`AxesHelper`、`GridHelper`、`BoxHelper` | 可视化 3D 空间 |
| 5 | 打印进度：在 onUpdate 中打印 `anim.progress` | 确认动画是否在运行 |
| 6 | 检查控制台警告：Three.js 会输出有用的性能/错误提示 | 发现常见配置问题 |

---

### 1. 使用 Anime.js DevTools 检查时间线

如果浏览器安装了 Anime.js DevTools 扩展（如有），可以：

- 可视化查看所有活跃动画的时间线（Timeline）
- 暂停/播放/逐帧调试动画
- 查看动画的目标对象、当前属性值、进度
- 实时修改缓动函数、持续时间并预览效果

> 💡 **替代方案**：如果没有 DevTools，可以在代码中暴露全局变量，在控制台手动控制：
> ```javascript
> // 开发环境暴露动画实例到 window
> if (import.meta.env.DEV) {
>   window.__debugAnimation = animation;
> }
> // 在浏览器控制台：
> // __debugAnimation.pause()  // 暂停
> // __debugAnimation.play()   // 播放
> // __debugAnimation.seek(500) // 跳转到500ms位置
> ```

---

### 2. 先简化场景，再逐步添加动画

遇到动画不工作或表现异常时，**不要在复杂场景中调试**——先做减法：

```javascript
// 🔧 调试步骤示例：rotateZ 动画不工作

// 第一步：最小化场景，只保留一个 mesh
// 暂时注释掉其他所有物体、灯光、阴影

// 第二步：最简单的动画配置
animate(testMesh, {
  rotateZ: 90,
  duration: 1000,
  ease: 'linear', // 用线性，排除缓动干扰
  loop: false     // 不循环，看单次效果
}, three);

// 如果这个简单动画工作了，说明核心配置没问题
// 第三步：逐步加回复杂度——先加其他属性，再加其他物体，再加stagger...
```

> 🎯 **调试黄金法则**：**当你遇到 bug 时，先删除一半代码。如果 bug 还在，再删除一半。**

---

### 3. 利用 seed 参数复现随机动画问题

使用 3D stagger 时，`jitter` 参数会引入随机因素，导致每次运行效果不同，bug 难以复现。此时使用 `seed` 参数固定随机种子：

```javascript
// ❌ 没有 seed：每次结果不同，bug 难复现
animate(meshes, {
  scale: [0.1, 1],
  duration: 1500,
  delay: stagger({
    grid: [8, 8, 8],
    jitter: 0.3,
    // 没有 seed → 每次随机都不一样
  }),
}, three);

// ✅ 有 seed：固定随机结果，可稳定复现问题
animate(meshes, {
  scale: [0.1, 1],
  duration: 1500,
  delay: stagger({
    grid: [8, 8, 8],
    jitter: 0.3,
    seed: 42  // 任何整数都行，相同 seed 得到相同的随机序列
  }),
}, three);
```

> 💡 **技巧**：当你发现一个偶现 bug 时，尝试几个不同的 seed 值，找到能稳定复现 bug 的那个 seed，然后固定它进行调试。

---

### 4. 检查浏览器控制台警告

Three.js 会在控制台输出非常有价值的警告信息，**不要忽略它们**：

| 常见警告 | 原因 | 解决方案 |
|---------|------|---------|
| `THREE.Material: transparent` 相关 | 动画 opacity 但没设置 `transparent: true` | 适配器通常自动处理，但手动创建材质时记得加 `transparent: true` |
| `GL ERROR :GL_INVALID_OPERATION` | 纹理尺寸不是2的幂次或格式错误 | 检查纹理尺寸、使用 `THREE.NearestFilter` 或调整纹理大小 |
| `Too many active WebGL contexts` | 创建太多 renderer 没 dispose | 单页面应用复用同一个 renderer，不要重复创建 |
| `Morph Targets exceeds limit` | morph target 数量超出硬件限制 | 减少 morph target 数量或使用其他方案 |

```javascript
// ✅ 动画 opacity 时确保材质设置了 transparent: true
const material = new THREE.MeshStandardMaterial({
  color: 0xff0000,
  transparent: true, // ← 必须设置！否则 opacity 动画无效或视觉异常
  opacity: 1
});

// 适配器会自动为你处理，但直接操作材质时不要忘记
```

---

## 常见陷阱与踩坑点

> ⚠️ **这里是开发者最容易掉进去的坑**——每一个都是真实项目中总结的血泪教训。

### 陷阱速查表

| 陷阱 | 发生频率 | 严重程度 | 易排查度 |
|------|---------|---------|---------|
| API 推测陷阱 | 🔴 极高 | 🔴 高 | 🟡 中 |
| 版本兼容问题 | 🟠 高 | 🔴 高 | 🟢 易 |
| 角度 vs 弧度混淆 | 🟠 高 | 🟡 中 | 🟡 中 |
| transformOrigin 设置错误 | 🟡 中 | 🟡 中 | 🔴 难 |
| 过度抽象反模式 | 🟡 中 | 🔴 高（长期） | 🔴 难 |
| Camera aspect 忘记更新 | 🟠 高 | 🟡 中 | 🟢 易 |

---

### ⚠️ 陷阱 1：API 推测陷阱——不要凭"常识"猜 API

这是**最常见也最浪费时间**的坑。适配器是 v4.5 新出的功能，社区资源少，很多 API 不能凭"看起来应该是这样"来推测：

| 错误推测（凭直觉） | 正确写法（查文档） | 为什么坑 |
|------------------|------------------|---------|
| `import { threeAdapter } from '@animejs/three'` | `import { three } from '@animejs/three'` | 导出名是 `three` 不是 `threeAdapter` 或 `ThreeAdapter` |
| `animate(targets, props, 'three')` | `animate(targets, props, three)` | 第三个参数是适配器对象，不是字符串 |
| `rotateX: Math.PI`（弧度） | `rotateX: 180`（角度） | 适配器用角度，原生 Three.js 用弧度，容易搞混 |
| `mesh.material.opacity = 0.5` 直接赋值后动画 | 直接在 Anime 中写 `opacity: 0.5` | 直接赋值可能绕过适配器的属性追踪 |

> 🚨 **铁律**：**任何 API 不确定时，立刻查[官方文档](https://animejs.com/documentation/three)**，不要猜！猜中了是运气，猜错了可能浪费几小时。

```javascript
// ❌ 典型错误：凭感觉写导入和参数
import { AnimeThree } from 'animejs-three'; // 错！包名和导出名都不对
animate(mesh, { x: 10 }, 'three'); // 错！第三个参数不是字符串

// ✅ 正确：查文档后再写
import { animate } from 'animejs';
import { three } from '@animejs/three'; // 对！包名是 @animejs/three，导出名是 three
animate(mesh, { x: 10 }, three); // 对！第三个参数是导入的 three 对象
```

---

### ⚠️ 陷阱 2：版本兼容——确保 Anime.js ≥ 4.5

Three.js 适配器是 Anime.js **v4.5.0 才新增**的功能，旧版本完全没有：

| 版本 | 有无 Three.js 适配器 | 症状 |
|------|-------------------|------|
| < 4.5.0 | ❌ 无 | `import { three } from '@animejs/three'` 报错，找不到模块 |
| 4.5.x | ✅ 有 | 正常使用 |
| 未来版本 | ✅ 可能有 | 注意 API 是否有 breaking change |

```bash
# 检查已安装版本
npm list animejs
# 或
pnpm list animejs

# 安装/升级到最新版
npm install animejs@latest
npm install @animejs/three@latest

# 或者明确指定版本
npm install animejs@^4.5.0 @animejs/three@^4.5.0
```

> 💡 **在 package.json 中锁定版本**，避免意外升级到不兼容版本：
> ```json
> {
>   "dependencies": {
>     "animejs": "^4.5.0",
>     "@animejs/three": "^4.5.0",
>     "three": "^0.160.0"
>   }
> }
> ```

---

### ⚠️ 陷阱 3：角度 vs 弧度——自动转换但别搞混场景

这是一个**很容易造成脑内冲突**的设计：

| API 场景 | 使用单位 | 示例 |
|---------|---------|------|
| **Anime.js 适配器动画属性** | **角度（degrees）** | `rotateX: 360` → 旋转一圈 |
| **原生 Three.js API** | **弧度（radians）** | `mesh.rotation.x = Math.PI` → 旋转半圈 |
| **Shader 中计算** | **弧度**（通常） | GLSL 中 `sin()` `cos()` 用弧度 |

```javascript
// ✅ Anime.js 适配器：用角度！
animate(mesh, {
  rotateX: 360,  // 360度 = 一圈，直觉正确
  rotateY: 90,   // 90度
  duration: 1000
}, three);

// ✅ 原生 Three.js 直接操作：用弧度！
mesh.rotation.x = Math.PI;       // 180度
mesh.rotation.y = Math.PI / 2;   // 90度
mesh.rotation.z = Math.PI * 2;   // 360度

// ❌ 错误：在 Anime 中用弧度
animate(mesh, {
  rotateX: Math.PI, // 这不是180度！这是约3.14度，几乎看不见旋转！
  duration: 1000
}, three);

// ❌ 错误：在原生 API 中用角度
mesh.rotation.x = 180; // 这不是半圈！这是180弧度 ≈ 10313度，转了28圈多！
```

> 🧠 **记忆口诀**：**动画配置用角度（Anime），直接操作用弧度（Three）**。

---

### ⚠️ 陷阱 4：transformOrigin 设置错误导致旋转中心不对

`transformOrigin` 是一个非常强大的功能，但也很容易设置错误导致旋转/缩放中心点不对：

**常见错误**：

| 错误写法 | 问题 | 正确写法 |
|---------|------|---------|
| `transformOrigin: '50% 50%'` | 用百分比字符串（CSS 写法），适配器不支持 | `transformOrigin: { x: 0.5, y: 0.5, z: 0 }` |
| `transformOrigin: { x: 1, y: 1 }` | 忘记 z 轴，3D 空间中 z 不是 0 | `transformOrigin: { x: 1, y: 1, z: 0 }` |
| 不理解坐标系方向 | Three.js 是 Y-up（Y轴朝上），和 CSS 不同 | 加 `AxesHelper` 可视化确认 |
| 多次动画时 transformOrigin 叠加 | 每次动画都会重新计算原点，不是持续状态 | 理解 transformOrigin 是动画属性而非永久状态 |

```javascript
// ❌ 错误：用 CSS 风格的百分比字符串
animate(mesh, {
  rotateZ: 360,
  transformOrigin: '100% 50%', // 不工作！适配器不识别字符串
  duration: 1000
}, three);

// ✅ 正确：用对象形式，值是**相对几何体尺寸**的倍数
// 几何体默认中心在 (0,0,0)，尺寸从 -0.5 到 0.5
// { x: 1, y: 0.5, z: 0 } → 右边中点（类似 CSS 的 right center）
animate(mesh, {
  rotateZ: 360,
  transformOrigin: { x: 1, y: 0.5, z: 0 }, // 绕右边中心旋转
  duration: 1000,
  ease: 'linear',
  loop: true
}, three);
```

> 🔧 **调试技巧**：如果旋转中心不对，临时添加一个小的 Mesh 标记 transformOrigin 的位置：
> ```javascript
> // 可视化 transformOrigin 位置
> const originHelper = new THREE.Mesh(
>   new THREE.SphereGeometry(0.05),
>   new THREE.MeshBasicMaterial({ color: 0xff0000 })
> );
> originHelper.position.set(1, 0.5, 0); // 和 transformOrigin 设成一样的值
> mesh.add(originHelper);
> ```

---

### ⚠️ 陷阱 5：过度抽象——不要试图用 Anime.js 做所有动画

适配器很强大，但它**不是万能的**。有些场景硬要用 Anime.js 反而更复杂：

| 动画类型 | 推荐方案 | 为什么不推荐用 Anime.js |
|---------|---------|----------------------|
| **骨骼动画**（SkinnedMesh/Bone） | 原生 AnimationMixer + GLTF 动画 | 骨骼权重、动画混合器是非常专业的领域，适配器未覆盖 |
| **物理动画**（碰撞、重力、刚体） | Cannon.js / Ammo.js / Rapier 等物理引擎 | 物理需要连续碰撞检测、积分器，不是简单插值能搞定的 |
| **变形目标动画**（Morph Targets / Blend Shapes） | 原生 morphTargetInfluences 或 Shader | 适配器支持有限，复杂面部表情动画用专业方案 |
| **IK（反向运动学）** | 专门 IK 库（如 THREE.IK） | 逆运动学是复杂数学问题，不属于插值动画范畴 |
| **路径跟随动画**（CatmullRomCurve3） | 可以用，但有更直接的方案 | 沿曲线移动可以直接在 requestAnimationFrame 中用 `getPointAt()` |

```javascript
// ❌ 反模式：硬要用 Anime.js 做物理
// 试图用 Anime.js 模拟小球弹跳重力 → 不真实、代码复杂、容易出问题

// ✅ 正确：专业的事交给专业的库
import * as CANNON from 'cannon-es';

// 用物理引擎处理物理模拟
const world = new CANNON.World();
world.gravity.set(0, -9.82, 0);
// ... 设置物理世界、刚体、碰撞

// Anime.js 只做它擅长的：非物理的装饰性动画、UI 动画、入场动画
animate(uiPanel, {
  opacity: [0, 1],
  y: [20, 0],
  duration: 500,
  ease: 'outQuad'
}, three);
```

> 🎯 **定位认知**：Anime.js 适配器是**补间动画（Tween）和时间线编排工具**，不是物理引擎、不是骨骼动画系统、不是粒子系统。它解决的是"属性从 A 平滑变到 B"的问题，不是所有动画问题。

---

### ⚠️ 陷阱 6：忘记设置 camera.aspect 和 updateProjectionMatrix

这是 **Three.js 新手最常见的问题**，和适配器无关但几乎每个人都会踩——窗口大小变化时画面拉伸变形：

```javascript
// ❌ 错误：窗口 resize 时只更新 renderer 尺寸
window.addEventListener('resize', () => {
  renderer.setSize(window.innerWidth, window.innerHeight);
  // 忘记更新相机！画面会被拉伸变形
});

// ✅ 正确：同时更新相机的 aspect 和投影矩阵
window.addEventListener('resize', () => {
  const width = window.innerWidth;
  const height = window.innerHeight;
  
  renderer.setSize(width, height);
  camera.aspect = width / height;      // 更新宽高比
  camera.updateProjectionMatrix();     // 必须调用！否则不生效
});
```

> 💡 **检查清单**：每次调用 `renderer.setSize()` 时，都要检查是否同步更新了 `camera.aspect` 和 `camera.updateProjectionMatrix()`。

---

## 与框架集成提示

> ⚛️ Anme.js + Three.js 适配器是 vanilla JS 库，在 React/Vue 等响应式框架中使用需要额外注意一些问题。

### 集成核心原则

| 原则 | 说明 |
|------|------|
| **动画状态 ≠ 响应式状态** | 动画每帧改变的值（position、rotation 等）不要放在 React state/Vue ref 中，会触发不必要的重渲染 |
| **useFrame 外创建动画** | 在 R3F 中，不要在 `useFrame` 钩子内创建 Anime.js 动画，会重复创建 |
| **手动清理副作用** | 组件卸载时记得暂停动画、dispose 资源 |
| **避免重复初始化** | 使用 useEffect/onMounted 确保动画只创建一次 |

---

### React Three Fiber (R3F) 集成

React Three Fiber 是 React 生态中最流行的 Three.js 封装。集成时注意：

```jsx
// ✅ 推荐：R3F 中使用 Anime.js 的正确方式
import { useRef, useEffect } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { animate } from 'animejs';
import { three } from '@animejs/three';

function AnimatedBox() {
  const meshRef = useRef();
  const animationRef = useRef(); // 用 ref 存储动画实例，不要放 state

  useEffect(() => {
    // 在 useEffect 中创建动画，确保只执行一次
    animationRef.current = animate(meshRef.current, {
      rotateY: 360,
      rotateX: 360,
      duration: 2000,
      ease: 'linear',
      loop: true
    }, three);

    // 组件卸载时清理
    return () => {
      if (animationRef.current) {
        animationRef.current.pause();
      }
    };
  }, []); // 空依赖数组：只在挂载时执行一次

  // ❌ 不要在 useFrame 中做 Anime.js 动画！
  // useFrame 每帧执行，会重复创建动画
  // useFrame(() => {
  //   animate(meshRef.current, { rotateY: 360 }, three); // 错误！
  // });

  return (
    <mesh ref={meshRef}>
      <boxGeometry args={[1, 1, 1]} />
      <meshStandardMaterial color={0x00ff88} />
    </mesh>
  );
}

function App() {
  return (
    <Canvas>
      <ambientLight intensity={0.5} />
      <pointLight position={[10, 10, 10]} />
      <AnimatedBox />
    </Canvas>
  );
}
```

> 📚 **社区方案**：R3F 社区已有封装好的 hooks（如 `useAnime`），可以搜索 GitHub 和 npm 查找成熟的集成方案，而不是自己从零实现。

---

### Vue Three / TroisJS 集成

Vue 生态的集成原则和 React 类似，核心也是**响应式状态与动画状态分离**：

```vue
<!-- ✅ 推荐：Vue 3 中使用 Anime.js -->
<template>
  <Canvas ref="canvasRef">
    <Mesh ref="meshRef">
      <BoxGeometry />
      <MeshStandardMaterial color="#00ff88" />
    </Mesh>
  </Canvas>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { Canvas, Mesh, BoxGeometry, MeshStandardMaterial } from 'troisjs';
import { animate } from 'animejs';
import { three } from '@animejs/three';

const meshRef = ref(null);
let animation = null;

onMounted(() => {
  // onMounted 中创建动画
  animation = animate(meshRef.value, {
    rotateY: 360,
    duration: 2000,
    ease: 'linear',
    loop: true
  }, three);
});

onUnmounted(() => {
  // 组件卸载时清理
  if (animation) {
    animation.pause();
  }
});
</script>
```

---

## 什么时候不该用适配器

> 🛑 **知道什么时候不用，和知道什么时候用一样重要**。适配器是工具，不是银弹。

### 适用边界决策表

| 场景/需求 | 推荐使用适配器？ | 理由 | 替代方案 |
|---------|----------------|------|---------|
| 简单补间动画（位置/旋转/缩放/透明度） | ✅ 强烈推荐 | 这是适配器最擅长的场景，代码量减少50%+ | 原生 requestAnimationFrame |
| 时间线编排（序列动画、交互动画） | ✅ 推荐 | Anime.js timeline 功能强大，编排复杂序列简单 | 手写 Promise 链、回调地狱 |
| 材质属性动画（颜色、粗糙度、金属度） | ✅ 推荐 | 自动颜色解析、属性扁平化，比原生简单太多 | 手动在渲染循环中更新 |
| Shader uniforms 动画 | ✅ 推荐 | 直接按名访问，无需手动在循环中赋值 | 手动在 requestAnimationFrame 更新 |
| InstancedMesh 批量动画 | ✅ 推荐 | getInstances() 大幅简化代码，性能不损失 | 手动维护 Matrix4 数组 |
| 3D 空间 stagger 交错 | ✅ 推荐 | 内置三维网格、jitter、seed，不用自己实现 | 自己计算 delay 数组 |
| 骨骼动画 / 蒙皮动画 | ❌ 不推荐 | 适配器不覆盖 AnimationMixer 领域 | 原生 AnimationMixer + glTF 动画 |
| 物理模拟（碰撞、重力、刚体） | ❌ 不推荐 | 物理需要连续检测、积分器，不是补间能解决的 | Cannon.js / Ammo.js / Rapier |
| 复杂 morph target 面部动画 | ❌ 不推荐 | 支持有限，面部动画是专业领域 | 原生 morphTargetInfluences + 专用库 |
| IK 反向运动学 | ❌ 不推荐 | 复杂数学问题，不属于插值动画范畴 | THREE.IK 等专用 IK 库 |
| 超大规模粒子系统（10万+） | ⚠️ 仅驱动 uniforms | CPU 逐实例插值性能不够，但可以驱动全局参数 | 纯 GPU Shader 动画（GPGPU） |
| 需要逐帧精确控制渲染逻辑 | ⚠️ 视情况 | Anime.js 封装了 rAF，需要精细控制时可能受限 | 回到原生 requestAnimationFrame |

---

### 决策流程图

```
开始
  ↓
需要做动画吗？
  ├─ 不需要 → 不用
  └─ 需要 → 什么类型的动画？
       ├─ 属性补间（位置/旋转/颜色/scale/opacity）→ ✅ 用适配器
       ├─ 时间线编排/序列动画/stagger → ✅ 用适配器
       ├─ InstancedMesh 批量动画 → ✅ 用适配器
       ├─ Shader uniforms 参数动画 → ✅ 用适配器
       ├─ 骨骼/蒙皮动画 → ❌ 用 AnimationMixer
       ├─ 物理（碰撞/重力/刚体）→ ❌ 用物理引擎
       ├─ 10万+粒子 → ⚠️ GPU Shader + Anime 驱动 uniforms
       └─ 不确定 → 🔍 先做原型测试，性能满足就用
```

---

> 💡 **最终建议**：**先用适配器做原型**——它能让你快速实现想法、验证视觉效果。如果遇到性能瓶颈或功能限制，再针对性地把那部分换成原生或专业方案。不要一开始就过度优化，也不要强行用不适合的工具解决问题。

---

## 本章要点回顾

| 类别 | 核心要点 |
|------|---------|
| **性能优化** | GPU 优先处理大规模粒子；>100个相同几何体用 InstancedMesh；回调中不做重计算；不可见时暂停动画；及时 dispose 资源 |
| **调试技巧** | 简化场景逐步排查；用 seed 固定随机；加 Helper 可视化；检查控制台警告；暴露全局变量手动控制 |
| **常见陷阱** | 不要猜 API，查文档；确保版本 ≥4.5；记住动画用角度、原生用弧度；transformOrigin 用对象而非字符串；专业动画交给专业库；窗口 resize 记得更新相机 |
| **框架集成** | 动画状态和响应式状态分离；useEffect/onMounted 中创建动画；组件卸载时清理；避免在 useFrame 中重复创建 |
| **适用边界** | 适配器是补间/时间线工具，不是物理/骨骼/IK 引擎；适合 80% 高频场景，剩下 20% 专业场景用专业方案 |

---

> **上一章**：[第 04 章 — 实战案例 ←](04-practical-examples.md)  
> **下一章**：[第 06 章 — 常见问题解答 →](06-faq.md)
