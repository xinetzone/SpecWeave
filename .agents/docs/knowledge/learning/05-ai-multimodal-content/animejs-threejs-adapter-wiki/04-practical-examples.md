---
id: "animejs-threejs-adapter-wiki-practical-examples"
title: "实战案例"
category: "learning"
tags: ["animejs", "threejs", "examples", "practice", "demo"]
date: "2026-08-03"
status: "active"
author: "SpecWeave"
source: "spec:animejs-threejs-adapter-wiki"
---

# 实战案例

本章通过三个完整的实战案例，展示 Anime.js Three.js 适配器在真实项目场景中的应用。每个案例聚焦不同的特性组合，帮助你从"知道API"过渡到"会用API解决实际问题"。

---

&gt; ⚠️ **API参考提示**：以下代码示例为基于官方文档和最佳实践的参考写法，实际导入方式、函数签名、参数配置等具体API细节请以 [Anime.js v4.5官方文档](https://animejs.com/documentation/three) 为准。

---

## 案例1：3D Hero Section入场动画

### 效果说明

官网首页 3D 英雄区域（Hero Section）入场动画是最常见的落地页动画场景。多个不同形状的几何体（立方体、球体、圆环、圆环结等）从屏幕外不同方向交错飞入，同时配合材质颜色渐变和透明度淡入，最终形成富有层次感的 3D 布局。动画完成后几何体保持缓慢的呼吸效果，整体视觉冲击力强但不喧宾夺主。

### 核心思路

本案例综合运用以下特性组合：

1. **属性扁平化**：直接使用 `x`、`y`、`z`、`rotateX`、`scale` 等扁平化属性控制几何体位置和姿态，无需深层链式访问
2. **3D stagger（三维交错）**：使用 `grid` 参数配合 `from: 'center'` 实现从中心向外的辐射状入场延迟，`jitter` 添加有机随机感
3. **材质动画组合**：同步动画 `color`、`opacity`、`metalness`、`roughness` 等材质属性，实现从半透明无质感实体到金属质感的过渡
4. **时间线编排**：主入场动画完成后，通过 `onComplete` 回调启动循环呼吸动画

### 完整代码

```javascript
import * as THREE from 'three';
import { animate, stagger, timeline } from 'animejs';
import { three } from '@animejs/three';

// 场景初始化
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(
  60,
  window.innerWidth / window.innerHeight,
  0.1,
  1000
);
const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });

renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.appendChild(renderer.domElement);

camera.position.z = 12;

// 光照设置
const ambientLight = new THREE.AmbientLight(0xffffff, 0.4);
scene.add(ambientLight);

const mainLight = new THREE.DirectionalLight(0xffffff, 1.2);
mainLight.position.set(5, 8, 5);
mainLight.castShadow = true;
mainLight.shadow.mapSize.set(2048, 2048);
scene.add(mainLight);

const fillLight = new THREE.PointLight(0x4488ff, 0.8, 30);
fillLight.position.set(-5, 3, 2);
scene.add(fillLight);

const rimLight = new THREE.PointLight(0xff6644, 0.6, 30);
rimLight.position.set(3, -2, -5);
scene.add(rimLight);

// 创建多个几何体
const geoms = [];
const meshes = [];

// 不同类型的几何体配置
const geometryConfigs = [
  { type: 'box', size: [1.2, 1.2, 1.2], color: '#6366f1' },
  { type: 'sphere', radius: 0.8, color: '#8b5cf6' },
  { type: 'torus', args: [0.7, 0.25, 16, 50], color: '#ec4899' },
  { type: 'torusKnot', args: [0.6, 0.2, 100, 16], color: '#f59e0b' },
  { type: 'octahedron', radius: 0.9, color: '#10b981' },
  { type: 'dodecahedron', radius: 0.75, color: '#3b82f6' },
  { type: 'icosahedron', radius: 0.7, color: '#ef4444' },
  { type: 'cone', args: [0.7, 1.4, 32], color: '#14b8a6' },
  { type: 'cylinder', args: [0.5, 0.5, 1.4, 32], color: '#f97316' },
];

// 3x3网格布局位置
const gridPositions = [];
const spacing = 3;
for (let row = -1; row &lt;= 1; row++) {
  for (let col = -1; col &lt;= 1; col++) {
    gridPositions.push({
      x: col * spacing,
      y: -row * spacing,
      z: (Math.random() - 0.5) * 2
    });
  }
}

// 创建Mesh
geometryConfigs.forEach((config, i) =&gt; {
  let geometry;
  
  switch (config.type) {
    case 'box':
      geometry = new THREE.BoxGeometry(...config.size);
      break;
    case 'sphere':
      geometry = new THREE.SphereGeometry(config.radius, 32, 32);
      break;
    case 'torus':
      geometry = new THREE.TorusGeometry(...config.args);
      break;
    case 'torusKnot':
      geometry = new THREE.TorusKnotGeometry(...config.args);
      break;
    case 'octahedron':
      geometry = new THREE.OctahedronGeometry(config.radius);
      break;
    case 'dodecahedron':
      geometry = new THREE.DodecahedronGeometry(config.radius);
      break;
    case 'icosahedron':
      geometry = new THREE.IcosahedronGeometry(config.radius);
      break;
    case 'cone':
      geometry = new THREE.ConeGeometry(...config.args);
      break;
    case 'cylinder':
      geometry = new THREE.CylinderGeometry(...config.args);
      break;
  }

  // 使用MeshStandardMaterial获得金属质感效果
  const material = new THREE.MeshStandardMaterial({
    color: config.color,
    metalness: 0,
    roughness: 1,
    transparent: true,
    opacity: 0
  });

  const mesh = new THREE.Mesh(geometry, material);
  mesh.castShadow = true;
  mesh.receiveShadow = true;

  // 初始位置设置在屏幕外不同方向（用于入场动画）
  const enterDir = Math.floor(Math.random() * 4);
  switch (enterDir) {
    case 0: // 从上方飞入
      mesh.position.set(gridPositions[i].x, 15, gridPositions[i].z - 5);
      break;
    case 1: // 从下方飞入
      mesh.position.set(gridPositions[i].x, -15, gridPositions[i].z - 5);
      break;
    case 2: // 从左侧飞入
      mesh.position.set(-15, gridPositions[i].y, gridPositions[i].z - 5);
      break;
    case 3: // 从右侧飞入
      mesh.position.set(15, gridPositions[i].y, gridPositions[i].z - 5);
      break;
  }

  // 存储目标位置用于动画结束后定位
  mesh.userData.targetPos = gridPositions[i];
  meshes.push(mesh);
  scene.add(mesh);
});

// 创建地面接收阴影（增强空间感）
const floorGeometry = new THREE.PlaneGeometry(30, 30);
const floorMaterial = new THREE.ShadowMaterial({ opacity: 0.15 });
const floor = new THREE.Mesh(floorGeometry, floorMaterial);
floor.rotation.x = -Math.PI / 2;
floor.position.y = -4;
floor.receiveShadow = true;
scene.add(floor);

// 入场动画 - 使用3D stagger实现辐射状交错
const enterAnimation = animate(meshes, {
  // 属性扁平化：直接访问位置、旋转、缩放
  x: (el) =&gt; el.userData.targetPos.x,
  y: (el) =&gt; el.userData.targetPos.y,
  z: (el) =&gt; el.userData.targetPos.z,
  rotateX: 360 * 2,
  rotateY: 360 * 2,
  rotateZ: 180,
  scale: [0, 1],
  // 材质动画组合：颜色、透明度、金属度、粗糙度同步过渡
  opacity: [0, 1],
  metalness: [0, 0.7],
  roughness: [1, 0.3],
  duration: 1800,
  delay: stagger({
    grid: [3, 3, 1], // 3x3x1网格布局
    from: 'center', // 从中心向外辐射
    each: 80,       // 每个元素延迟80ms
    jitter: 0.2,    // 20%随机抖动增加自然感
    seed: 12345     // 固定种子保证可复现
  }),
  ease: 'outExpo',
  // 入场完成后启动循环呼吸动画
  onComplete: () =&gt; {
    startBreathingAnimation();
  }
}, three);

// 呼吸动画 - 入场完成后持续运行
function startBreathingAnimation() {
  animate(meshes, {
    y: (el) =&gt; el.userData.targetPos.y + 0.3,
    rotateY: '+=' + 360,
    scale: 1.08,
    duration: 3000,
    delay: stagger({
      grid: [3, 3, 1],
      from: 'center',
      each: 100,
      jitter: 0.1,
      seed: 54321
    }),
    ease: 'inOutSine',
    loop: true,
    alternate: true
  }, three);
}

// 响应窗口大小变化
window.addEventListener('resize', () =&gt; {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

// 渲染循环 - Anime.js自动驱动动画，这里只需要render
function render() {
  requestAnimationFrame(render);
  renderer.render(scene, camera);
}
render();
```

### 关键代码注释

| 代码位置 | 说明 |
|---------|------|
| `delay: stagger({ grid: [3, 3, 1], from: 'center' ... })` | **3D stagger核心配置**：声明3x3x1网格布局，从中心开始计算延迟，实现辐射状入场效果 |
| `x: (el) =&gt; el.userData.targetPos.x` | 使用函数形式属性值，为每个元素设置独立的目标位置，配合批量动画 |
| `metalness` / `roughness` 直接动画 | **材质属性扁平化**：无需访问 `mesh.material.metalness`，适配器自动处理层级 |
| `scale: [0, 1]` | 数组形式定义起始值和结束值，从0缩放到1，实现"弹出"效果 |
| `onComplete` 回调启动呼吸动画 | 使用 Anime.js 生命周期钩子实现动画序列编排 |
| `seed: 12345` | 固定随机种子，保证每次运行交错顺序一致，便于调试和视觉一致性 |

---

## 案例2：粒子网格波动动画

### 效果说明

创意编程（Creative Coding）风格的 10×10×10 三维粒子网格波动效果。1000 个小球体按三维网格排列，根据正弦波规律产生起伏波动，配合基于高度的颜色映射（蓝色→青色→绿色→黄色→红色），形成类似音乐可视化或流体模拟的视觉效果。使用 InstancedMesh 保证性能，通过 seed 参数实现可复现的随机动画参数。

### 核心思路

本案例重点演示以下特性组合：

1. **InstancedMesh + getInstances()**：使用 `three.getInstances()` 获取可独立动画的实例代理数组，1000个实例仅需1个draw call，性能优异
2. **3D stagger + seed可复现随机**：使用固定 `seed` 保证波动相位可复现，`grid: [10, 10, 10]` 正确映射三维网格索引
3. **基于函数的属性值**：使用 `(el, i)` 函数形式为每个实例计算独立的动画参数（相位、振幅、频率）
4. **颜色动画与HSL色彩空间**：使用HSL颜色值实现基于高度的渐变色彩动画

### 完整代码

```javascript
import * as THREE from 'three';
import { animate, stagger } from 'animejs';
import { three } from '@animejs/three';

// 场景初始化
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x0a0a0f);
scene.fog = new THREE.FogExp2(0x0a0a0f, 0.03);

const camera = new THREE.PerspectiveCamera(
  60,
  window.innerWidth / window.innerHeight,
  0.1,
  1000
);
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
document.body.appendChild(renderer.domElement);

camera.position.set(12, 10, 12);
camera.lookAt(0, 0, 0);

// 光照
const ambientLight = new THREE.AmbientLight(0xffffff, 0.3);
scene.add(ambientLight);

const mainLight = new THREE.DirectionalLight(0xffffff, 1);
mainLight.position.set(5, 10, 7);
scene.add(mainLight);

const pointLight1 = new THREE.PointLight(0x00ffff, 0.8, 30);
pointLight1.position.set(-5, 3, -5);
scene.add(pointLight1);

const pointLight2 = new THREE.PointLight(0xff00ff, 0.6, 30);
pointLight2.position.set(5, -2, 5);
scene.add(pointLight2);

// ===== InstancedMesh 核心配置 =====
const gridSize = 10;
const spacing = 1.1;
const instanceCount = gridSize * gridSize * gridSize;

// 小球几何体 - 使用低多边形球体保证性能
const sphereGeometry = new THREE.SphereGeometry(0.15, 8, 8);
const sphereMaterial = new THREE.MeshStandardMaterial({
  metalness: 0.6,
  roughness: 0.3,
  transparent: true,
  opacity: 0.9
});

// 创建InstancedMesh：1个draw call渲染1000个球体
const instancedMesh = new THREE.InstancedMesh(
  sphereGeometry,
  sphereMaterial,
  instanceCount
);
instancedMesh.castShadow = true;
instancedMesh.instanceMatrix.setUsage(THREE.DynamicDrawUsage);

// 初始化实例矩阵位置
const dummy = new THREE.Object3D();
const instanceData = []; // 存储每个实例的网格坐标

let index = 0;
for (let x = 0; x &lt; gridSize; x++) {
  for (let y = 0; y &lt; gridSize; y++) {
    for (let z = 0; z &lt; gridSize; z++) {
      const posX = (x - gridSize / 2 + 0.5) * spacing;
      const posY = (y - gridSize / 2 + 0.5) * spacing;
      const posZ = (z - gridSize / 2 + 0.5) * spacing;
      
      dummy.position.set(posX, posY, posZ);
      dummy.updateMatrix();
      instancedMesh.setMatrixAt(index, dummy.matrix);
      
      // 存储网格坐标用于后续计算
      instanceData.push({
        gridX: x,
        gridY: y,
        gridZ: z,
        baseX: posX,
        baseY: posY,
        baseZ: posZ
      });
      
      index++;
    }
  }
}
instancedMesh.instanceMatrix.needsUpdate = true;
scene.add(instancedMesh);

// ===== 核心：getInstances() 获取可动画的实例代理数组 =====
const instances = three.getInstances(instancedMesh);

// ===== 波动动画配置 =====
// 使用固定seed的伪随机数生成器，保证每次运行参数一致
function seededRandom(seed) {
  let s = seed;
  return function() {
    s = (s * 9301 + 49297) % 233280;
    return s / 233280;
  };
}
const rng = seededRandom(42); // seed=42，可复现

// 为每个实例预计算波动参数
instances.forEach((inst, i) =&gt; {
  inst.userData = {
    phase: rng() * Math.PI * 2,      // 随机相位
    amplitude: 0.3 + rng() * 0.7,     // 波动振幅
    frequency: 0.8 + rng() * 0.8,     // 波动频率
    speed: 0.5 + rng() * 1.0          // 动画速度
  };
});

// 主波动动画 - 无限循环
animate(instances, {
  // Y轴位置：基础位置 + 正弦波偏移
  y: (el, i) =&gt; {
    const data = instanceData[i];
    const { phase, amplitude } = el.userData;
    // 基于网格位置计算波浪传播效果
    const distFromCenter = Math.sqrt(
      data.gridX * data.gridX + 
      data.gridY * data.gridY + 
      data.gridZ * data.gridZ
    );
    return data.baseY + Math.sin(phase + distFromCenter * 0.3) * amplitude;
  },
  // 缩放随波动变化
  scale: (el, i) =&gt; {
    const data = instanceData[i];
    const { phase, amplitude } = el.userData;
    const distFromCenter = Math.sqrt(
      data.gridX * data.gridX + 
      data.gridY * data.gridY + 
      data.gridZ * data.gridZ
    );
    const wave = Math.sin(phase + distFromCenter * 0.3);
    return 0.6 + wave * amplitude * 0.5;
  },
  // 颜色HSL：基于高度和波动相位变化，色相从蓝→红循环
  color: (el, i) =&gt; {
    const data = instanceData[i];
    const { phase } = el.userData;
    const distFromCenter = Math.sqrt(
      data.gridX * data.gridX + 
      data.gridY * data.gridY + 
      data.gridZ * data.gridZ
    );
    const wave = Math.sin(phase + distFromCenter * 0.3);
    // HSL色相：200(蓝) → 0(红)，按距离和波动偏移
    const hue = 200 - (wave + 1) * 100 - distFromCenter * 5;
    const saturation = 70 + wave * 20;
    const lightness = 50 + wave * 15;
    return `hsl(${hue % 360}, ${saturation}%, ${lightness}%)`;
  },
  duration: (el) =&gt; 2000 / el.userData.speed, // 每个实例速度不同
  delay: stagger({
    grid: [gridSize, gridSize, gridSize], // 10x10x10三维网格
    from: 'center',                       // 从中心向外扩散
    each: 3,                              // 每实例延迟3ms
    jitter: 0.15,                         // 15%随机抖动
    seed: 42                              // 与随机数生成器同seed，保证一致
  }),
  ease: 'sineInOut',
  loop: true,
  alternate: true
}, three);

// 相机缓慢旋转，增强3D空间感
animate(camera.position, {
  x: 12,
  z: -12,
  duration: 20000,
  ease: 'linear',
  loop: true,
  alternate: true,
  onUpdate: () =&gt; {
    camera.lookAt(0, 0, 0);
  }
});

// 添加控制面板信息（可选，实际项目可使用lil-gui等）
console.log('粒子网格动画已启动 - 1000个实例，seed=42可复现');

// 响应窗口大小
window.addEventListener('resize', () =&gt; {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

// 渲染循环
function render() {
  requestAnimationFrame(render);
  renderer.render(scene, camera);
}
render();
```

### 关键代码注释

| 代码位置 | 说明 |
|---------|------|
| `three.getInstances(instancedMesh)` | **核心API**：返回可独立动画的实例代理数组，每个元素像普通Mesh一样操作，适配器自动处理矩阵更新 |
| `new THREE.InstancedMesh(geometry, material, count)` | 使用InstancedMesh渲染1000个球体仅需1个draw call，性能远优于创建1000个独立Mesh |
| `seededRandom(42)` + `seed: 42` | **可复现随机**：随机相位、振幅与stagger延迟使用相同seed，保证每次运行波形完全一致 |
| `grid: [gridSize, gridSize, gridSize]` | 3D stagger必须正确声明三维网格尺寸，否则交错延迟计算错误 |
| `y: (el, i) =&gt; { ... }` | 函数式属性值：根据实例索引和网格坐标计算独立目标值，实现个性化动画 |
| `color: 'hsl(...)' ` | 适配器自动解析HSL颜色字符串，无需手动转换为THREE.Color或RGB值 |
| `duration: (el) =&gt; 2000 / el.userData.speed` | 支持函数形式返回duration，为每个实例设置不同的动画周期 |

---

## 案例3：产品3D展示交互

### 效果说明

电商场景的产品3D展示交互：产品模型默认缓慢自转展示各个角度，鼠标悬停（hover）时模型放大、轻微倾斜突出立体感、材质金属度提升产生高光效果；鼠标移开时平滑恢复原状。点击时有额外的弹跳反馈。本案例重点演示如何正确设置 `transformOrigin` 实现自然的旋转和缩放中心，以及交互事件与动画的无缝结合。

### 核心思路

本案例重点演示以下特性组合：

1. **transformOrigin（变换原点）**：正确设置旋转/缩放中心为产品几何中心底部或中心，避免悬浮时偏移
2. **材质动画**：hover时 `metalness`、`roughness`、`emissive` 动态变化，模拟光照反射增强质感
3. **Extended transforms**：使用 `rotateX`/`rotateY` 直接角度值动画，无需弧度转换
4. **交互事件驱动**：结合 `mouseenter`/`mouseleave` 事件，使用 Anime.js 的控件方法（`play`/`reverse`/`seek`）实现流畅的状态过渡
5. **时间线控制**：使用 Anime.js 动画实例的 `pause()`、`play()`、`reverse()` 方法精确控制动画状态

### 完整代码

```javascript
import * as THREE from 'three';
import { animate, createTimer } from 'animejs';
import { three } from '@animejs/three';

// 场景初始化
const scene = new THREE.Scene();
scene.background = new THREE.Color(0xf5f5f7);

const camera = new THREE.PerspectiveCamera(
  45,
  window.innerWidth / window.innerHeight,
  0.1,
  100
);
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.2;
document.body.appendChild(renderer.domElement);

camera.position.set(0, 1.5, 5);
camera.lookAt(0, 0.5, 0);

// 光照设置 - 产品展示需要精致的光照
const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
scene.add(ambientLight);

// 主光源（关键光）
const keyLight = new THREE.DirectionalLight(0xffffff, 1.2);
keyLight.position.set(3, 5, 3);
keyLight.castShadow = true;
keyLight.shadow.mapSize.set(2048, 2048);
keyLight.shadow.bias = -0.0001;
keyLight.shadow.camera.near = 0.5;
keyLight.shadow.camera.far = 20;
keyLight.shadow.camera.left = -5;
keyLight.shadow.camera.right = 5;
keyLight.shadow.camera.top = 5;
keyLight.shadow.camera.bottom = -5;
scene.add(keyLight);

// 补光
const fillLight = new THREE.DirectionalLight(0x88aaff, 0.4);
fillLight.position.set(-3, 2, 2);
scene.add(fillLight);

// 轮廓光（背光）
const rimLight = new THREE.DirectionalLight(0xffddaa, 0.5);
rimLight.position.set(0, 3, -4);
scene.add(rimLight);

// 地面 - 用于接收阴影
const floorGeometry = new THREE.CircleGeometry(3, 64);
const floorMaterial = new THREE.MeshStandardMaterial({
  color: 0xeeeeee,
  roughness: 0.8,
  metalness: 0.1
});
const floor = new THREE.Mesh(floorGeometry, floorMaterial);
floor.rotation.x = -Math.PI / 2;
floor.position.y = -0.01;
floor.receiveShadow = true;
scene.add(floor);

// ===== 创建产品模型（以智能手表/表盘为例）=====
const productGroup = new THREE.Group();
scene.add(productGroup);

// 表盘主体
const bodyGeometry = new THREE.CylinderGeometry(0.8, 0.8, 0.2, 64);
const bodyMaterial = new THREE.MeshStandardMaterial({
  color: 0x2c2c2e,
  metalness: 0.8,
  roughness: 0.2
});
const body = new THREE.Mesh(bodyGeometry, bodyMaterial);
body.rotation.x = Math.PI / 2;
body.castShadow = true;
body.receiveShadow = true;
productGroup.add(body);

// 表圈（金属环）
const bezelGeometry = new THREE.TorusGeometry(0.82, 0.04, 16, 64);
const bezelMaterial = new THREE.MeshStandardMaterial({
  color: 0xc0c0c8,
  metalness: 0.95,
  roughness: 0.08
});
const bezel = new THREE.Mesh(bezelGeometry, bezelMaterial);
bezel.rotation.x = Math.PI / 2;
bezel.castShadow = true;
productGroup.add(bezel);

// 表盘屏幕
const screenGeometry = new THREE.CylinderGeometry(0.75, 0.75, 0.01, 64);
const screenMaterial = new THREE.MeshStandardMaterial({
  color: 0x1a1a2e,
  metalness: 0.1,
  roughness: 0.1,
  emissive: 0x1a1a2e,
  emissiveIntensity: 0.3
});
const screen = new THREE.Mesh(screenGeometry, screenMaterial);
screen.rotation.x = Math.PI / 2;
screen.position.z = 0.11;
productGroup.add(screen);

// 指针（简化）
const hourHandGeometry = new THREE.BoxGeometry(0.06, 0.4, 0.02);
const hourHandMaterial = new THREE.MeshStandardMaterial({ color: 0xffffff });
const hourHand = new THREE.Mesh(hourHandGeometry, hourHandMaterial);
hourHand.position.set(0, 0.15, 0.12);
hourHand.rotation.z = Math.PI / 4;
productGroup.add(hourHand);

const minuteHandGeometry = new THREE.BoxGeometry(0.04, 0.55, 0.02);
const minuteHand = new THREE.Mesh(minuteHandGeometry, hourHandMaterial);
minuteHand.position.set(0, 0.22, 0.12);
productGroup.rotation.x = Math.PI / 6;
productGroup.add(minuteHand);

// ===== transformOrigin 关键设置 =====
// 设置变换原点在产品几何中心，确保缩放/旋转时不会偏移
animate(productGroup, {
  transformOrigin: { x: 0, y: 0, z: 0 }, // 产品组中心为变换原点
  duration: 0 // 立即设置，无动画
}, three);

// ===== 默认自转动画 =====
const idleRotation = animate(productGroup, {
  rotateY: 360,
  duration: 12000,
  ease: 'linear',
  loop: true
}, three);

// ===== Hover交互动画 =====
// hover状态动画：放大、倾斜、金属度提升、发光
const hoverAnimation = animate(productGroup.children, [
  {
    // 主体和表圈：金属度提升、粗糙度降低
    targets: [body, bezel],
    scale: 1.12,
    metalness: 0.98,
    roughness: 0.05,
    duration: 600,
    ease: 'outCubic'
  },
  {
    // 屏幕：发光增强
    targets: screen,
    scale: 1.05,
    emissiveIntensity: 0.8,
    emissive: '#4488ff',
    duration: 600,
    ease: 'outCubic'
  },
  {
    // 整体组：倾斜和上移
    targets: productGroup,
    y: 0.3,
    rotateX: -20,   // 向上倾斜展示
    rotateZ: 8,     // 轻微侧倾增加动感
    duration: 600,
    ease: 'outBack(1.2)'
  }
], three);

// 初始暂停hover动画
hoverAnimation.pause();

// ===== 点击反馈动画 =====
function playClickAnimation() {
  animate(productGroup, {
    scale: [1, 0.92, 1.05, 1],
    duration: 400,
    ease: 'outElastic(1, 0.5)'
  }, three);
}

// ===== 射线检测实现鼠标交互 =====
const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();
let isHovered = false;

function onMouseMove(event) {
  // 计算鼠标NDC坐标
  mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
  mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;
  
  raycaster.setFromCamera(mouse, camera);
  const intersects = raycaster.intersectObjects(productGroup.children);
  
  if (intersects.length &gt; 0 &amp;&amp; !isHovered) {
    // 鼠标进入
    isHovered = true;
    document.body.style.cursor = 'pointer';
    idleRotation.pause();          // 暂停自转
    hoverAnimation.play();         // 播放hover动画
  } else if (intersects.length === 0 &amp;&amp; isHovered) {
    // 鼠标离开
    isHovered = false;
    document.body.style.cursor = 'default';
    hoverAnimation.reverse();      // 反向播放恢复
    idleRotation.play();           // 恢复自转
  }
}

function onClick(event) {
  mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
  mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;
  
  raycaster.setFromCamera(mouse, camera);
  const intersects = raycaster.intersectObjects(productGroup.children);
  
  if (intersects.length &gt; 0) {
    playClickAnimation();
  }
}

window.addEventListener('mousemove', onMouseMove);
window.addEventListener('click', onClick);

// 响应窗口大小
window.addEventListener('resize', () =&gt; {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

// 渲染循环
function render() {
  requestAnimationFrame(render);
  renderer.render(scene, camera);
}
render();
```

### 关键代码注释

| 代码位置 | 说明 |
|---------|------|
| `transformOrigin: { x: 0, y: 0, z: 0 }` | **transformOrigin核心设置**：设置变换原点在产品组中心，确保缩放/倾斜时围绕产品中心进行，不会出现偏移（以官方文档为准） |
| `hoverAnimation.pause()` + `.play()` + `.reverse()` | 使用 Anime.js 动画实例方法控制动画状态，`reverse()`实现平滑恢复而非硬重置 |
| `targets: [body, bezel]` / `targets: screen` / `targets: productGroup` | 时间线支持多目标分阶段动画，不同对象同时执行不同动画 |
| `rotateX: -20` / `rotateZ: 8` | 使用角度值直接动画，适配器自动转换为弧度，无需手动 `* Math.PI / 180` |
| `emissive` / `emissiveIntensity` 直接动画 | 材质发光属性扁平化，直接动画 `emissive` 颜色和强度，模拟屏幕点亮效果 |
| `idleRotation.pause()` / `.play()` | hover时暂停自转，离开时恢复，避免动画冲突 |
| Raycaster 检测hover | Three.js标准射线检测实现鼠标拾取，与Anime.js动画控制解耦 |
| `scale: [1, 0.92, 1.05, 1]` | 关键帧数组形式实现点击弹跳：按下→弹起→过冲→回正 |

---

## 案例特性矩阵总结

| 特性 | 案例1：Hero Section | 案例2：粒子网格 | 案例3：产品展示 |
|------|:------------------:|:--------------:|:--------------:|
| 属性扁平化（x/y/rotateX/scale） | ✅ | ✅ | ✅ |
| 3D stagger（grid/from/each） | ✅ | ✅ | - |
| seed 可复现随机 | ✅ | ✅ | - |
| InstancedMesh + getInstances() | - | ✅ | - |
| 材质动画（color/opacity/metalness） | ✅ | ✅ | ✅ |
| transformOrigin | - | - | ✅ |
| Extended transforms（rotate/skew） | ✅ | - | ✅ |
| 时间线/多目标动画 | ✅ | - | ✅ |
| 交互事件驱动 | - | - | ✅ |
| 函数式属性值 | ✅ | ✅ | - |
| HSL颜色自动解析 | ✅ | ✅ | ✅ |
| emissive 发光动画 | - | - | ✅ |
| 生命周期回调（onComplete） | ✅ | - | - |

---

## 扩展练习建议

学完以上三个案例后，建议尝试以下扩展练习巩固知识：

1. **扩展案例1**：添加文字标题入场动画，使用 CSS 2D 与 3D 动画时间线同步
2. **扩展案例2**：添加鼠标排斥效果，鼠标靠近时粒子散开（使用 onUpdate + raycaster）
3. **扩展案例3**：添加材质切换按钮，点击时在不同材质间平滑过渡（metalness/roughness/color timeline）
4. **综合挑战**：结合三个案例的技术点，实现一个包含产品展示、粒子背景、入场动画的完整落地页

---

&gt; 💡 **提示**：以上示例代码为独立完整的可运行示例（除导入路径需根据项目配置调整外）。实际项目中建议将场景初始化、对象创建、动画配置分离到不同模块，保持代码可维护性。

---

> **上一章**：[第 03 章 — 五大核心特性详解 ←](03-five-features.md)  
> **下一章**：[第 05 章 — 最佳实践与常见陷阱 →](05-best-practices.md)
