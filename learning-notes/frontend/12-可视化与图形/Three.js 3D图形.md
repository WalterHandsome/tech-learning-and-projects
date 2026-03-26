# Three.js 3D 图形

## 1. 基本概念

```javascript
import * as THREE from 'three';

// 场景
const scene = new THREE.Scene();
scene.background = new THREE.Color(0xf0f0f0);

// 相机（透视相机）
const camera = new THREE.PerspectiveCamera(
  75,                                    // 视角
  window.innerWidth / window.innerHeight, // 宽高比
  0.1,                                   // 近裁剪面
  1000                                   // 远裁剪面
);
camera.position.set(0, 5, 10);
camera.lookAt(0, 0, 0);

// 渲染器
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(window.devicePixelRatio);
document.body.appendChild(renderer.domElement);
```

## 2. 几何体与材质

```javascript
// 立方体
const geometry = new THREE.BoxGeometry(1, 1, 1);
const material = new THREE.MeshStandardMaterial({ color: 0x3498db });
const cube = new THREE.Mesh(geometry, material);
scene.add(cube);

// 球体
const sphere = new THREE.Mesh(
  new THREE.SphereGeometry(0.5, 32, 32),
  new THREE.MeshStandardMaterial({ color: 0xe74c3c, metalness: 0.3, roughness: 0.7 })
);
sphere.position.set(2, 0, 0);
scene.add(sphere);

// 平面
const plane = new THREE.Mesh(
  new THREE.PlaneGeometry(20, 20),
  new THREE.MeshStandardMaterial({ color: 0xcccccc })
);
plane.rotation.x = -Math.PI / 2;
plane.position.y = -1;
scene.add(plane);
```

## 3. 光照

```javascript
// 环境光（均匀照亮所有物体）
const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
scene.add(ambientLight);

// 平行光（模拟太阳光）
const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
directionalLight.position.set(5, 10, 5);
directionalLight.castShadow = true;
scene.add(directionalLight);

// 点光源
const pointLight = new THREE.PointLight(0xff6600, 1, 100);
pointLight.position.set(0, 5, 0);
scene.add(pointLight);
```

## 4. 动画循环

```javascript
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';

const controls = new OrbitControls(camera, renderer.domElement);

function animate() {
  requestAnimationFrame(animate);
  cube.rotation.x += 0.01;
  cube.rotation.y += 0.01;
  controls.update();
  renderer.render(scene, camera);
}
animate();

// 响应式
window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});
```

## 5. 模型加载

```javascript
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader';

const loader = new GLTFLoader();
loader.load('/models/scene.gltf', (gltf) => {
  scene.add(gltf.scene);
  // 播放动画
  const mixer = new THREE.AnimationMixer(gltf.scene);
  gltf.animations.forEach(clip => mixer.clipAction(clip).play());
});
```
