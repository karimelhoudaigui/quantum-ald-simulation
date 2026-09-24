import { Info, Maximize2 } from "lucide-react";
import { useEffect, useRef } from "react";
import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";

import { useChemistryStore } from "../../stores/chemistryStore";
import type { AtomDraft, CoordinateUnit } from "../../types/chemistry";
import { IconButton } from "../ui/IconButton";

const elementStyle: Record<string, { color: number; radius: number }> = {
  H: { color: 0xe8f4f1, radius: 0.31 },
  He: { color: 0xbfe9e2, radius: 0.28 },
  Li: { color: 0xa78bfa, radius: 1.28 },
  Be: { color: 0x86efac, radius: 0.96 },
  B: { color: 0xf2a65a, radius: 0.84 },
  C: { color: 0x6b7280, radius: 0.76 },
  N: { color: 0x60a5fa, radius: 0.71 },
  O: { color: 0xf87171, radius: 0.66 },
  F: { color: 0x4ade80, radius: 0.57 },
  Na: { color: 0xc084fc, radius: 1.66 },
  Mg: { color: 0x86efac, radius: 1.41 },
  Al: { color: 0x94a3b8, radius: 1.21 },
  Si: { color: 0xf0b36a, radius: 1.11 },
  P: { color: 0xf59e0b, radius: 1.07 },
  S: { color: 0xfacc15, radius: 1.05 },
  Cl: { color: 0x22c55e, radius: 1.02 },
};

export function MoleculeCanvas() {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const fitViewRef = useRef<(() => void) | null>(null);
  const atoms = useChemistryStore((state) => state.atoms);
  const unit = useChemistryStore((state) => state.unit);
  const selectedAtomId = useChemistryStore((state) => state.selectedAtomId);
  const selectAtom = useChemistryStore((state) => state.selectAtom);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(42, 1, 0.01, 1000);
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    container.appendChild(renderer.domElement);

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.06;
    controls.autoRotate = false;
    controls.enablePan = true;
    controls.enableZoom = false;
    controls.screenSpacePanning = true;
    renderer.domElement.style.touchAction = "none";

    scene.add(new THREE.HemisphereLight(0xd9fff7, 0x101827, 2.2));
    const keyLight = new THREE.DirectionalLight(0xffffff, 2.8);
    keyLight.position.set(5, 7, 8);
    scene.add(keyLight);
    const rimLight = new THREE.DirectionalLight(0x57e6cb, 2.1);
    rimLight.position.set(-5, -2, -6);
    scene.add(rimLight);

    const molecule = buildMolecule(atoms, unit, selectedAtomId);
    scene.add(molecule.group);
    const moleculeCenter = molecule.bounds.getCenter(new THREE.Vector3());
    const moleculeSize = molecule.bounds.getSize(new THREE.Vector3());
    const horizontalSpan = Math.max(moleculeSize.x, moleculeSize.z, 1);
    const gridSize = Math.min(12, Math.max(4, Math.ceil(horizontalSpan * 2.6) / 2));
    const gridDivisions = Math.min(24, Math.max(8, Math.round(gridSize * 2)));
    const gridY = molecule.bounds.min.y - 0.3;
    const grid = new THREE.GridHelper(gridSize, gridDivisions, 0x294c48, 0x182a2d);
    grid.position.set(moleculeCenter.x, gridY, moleculeCenter.z);
    scene.add(grid);

    const framingPoints = boxCorners(molecule.bounds);
    const halfGrid = gridSize / 2;
    for (const xOffset of [-halfGrid, halfGrid]) {
      for (const zOffset of [-halfGrid, halfGrid]) {
        framingPoints.push(new THREE.Vector3(
          moleculeCenter.x + xOffset,
          gridY,
          moleculeCenter.z + zOffset,
        ));
      }
    }
    const viewTarget = moleculeCenter.clone();
    viewTarget.y = THREE.MathUtils.lerp(moleculeCenter.y, gridY, 0.85);
    let fittedDistance = 4.25;

    const fitView = () => {
      const width = Math.max(container.clientWidth, 1);
      const height = Math.max(container.clientHeight, 1);
      camera.aspect = width / height;

      const verticalFov = THREE.MathUtils.degToRad(camera.fov);
      const horizontalFov = 2 * Math.atan(Math.tan(verticalFov / 2) * camera.aspect);
      const viewDirection = new THREE.Vector3(1, 0.55, 0.25).normalize();
      const distance = Math.max(
        distanceToFitPoints(framingPoints, viewTarget, viewDirection, verticalFov, horizontalFov),
        4.25,
      );

      fittedDistance = distance;
      controls.minDistance = fittedDistance * 0.35;
      controls.maxDistance = fittedDistance * 6;
      camera.position.copy(viewTarget).addScaledVector(viewDirection, distance);
      camera.near = Math.max(distance / 1000, 0.01);
      camera.far = distance * 30;
      camera.updateProjectionMatrix();
      controls.target.copy(viewTarget);
      controls.update();
    };
    fitViewRef.current = fitView;

    const onWheel = (event: WheelEvent) => {
      event.preventDefault();
      event.stopPropagation();
      controls.autoRotate = false;

      const height = Math.max(renderer.domElement.clientHeight, 1);
      const normalizeDelta = (value: number) => {
        if (event.deltaMode === WheelEvent.DOM_DELTA_LINE) return value * 16;
        if (event.deltaMode === WheelEvent.DOM_DELTA_PAGE) return value * height;
        return value;
      };

      const distance = camera.position.distanceTo(controls.target);
      if (event.ctrlKey) {
        const zoomFactor = Math.exp(THREE.MathUtils.clamp(normalizeDelta(event.deltaY), -60, 60) * 0.012);
        const nextDistance = THREE.MathUtils.clamp(
          distance * zoomFactor,
          fittedDistance * 0.35,
          fittedDistance * 6,
        );
        const viewOffset = camera.position.clone().sub(controls.target).normalize();
        camera.position.copy(controls.target).addScaledVector(viewOffset, nextDistance);
        controls.update();
        return;
      }

      const worldPerPixel = (
        2 * distance * Math.tan(THREE.MathUtils.degToRad(camera.fov) / 2)
      ) / height;
      const cameraRight = new THREE.Vector3().setFromMatrixColumn(camera.matrixWorld, 0).normalize();
      const cameraUp = new THREE.Vector3().setFromMatrixColumn(camera.matrixWorld, 1).normalize();
      const panOffset = cameraRight
        .multiplyScalar(normalizeDelta(event.deltaX) * worldPerPixel)
        .addScaledVector(cameraUp, -normalizeDelta(event.deltaY) * worldPerPixel);

      camera.position.add(panOffset);
      controls.target.add(panOffset);
      controls.update();
    };
    renderer.domElement.addEventListener("wheel", onWheel, { passive: false });

    const resize = () => {
      const width = Math.max(container.clientWidth, 1);
      const height = Math.max(container.clientHeight, 1);
      renderer.setSize(width, height, false);
      fitView();
    };
    const resizeObserver = new ResizeObserver(resize);
    resizeObserver.observe(container);
    resize();

    const raycaster = new THREE.Raycaster();
    const pointer = new THREE.Vector2();
    const onPointerDown = (event: PointerEvent) => {
      if (event.button !== 0) return;
      const rect = renderer.domElement.getBoundingClientRect();
      pointer.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
      pointer.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
      raycaster.setFromCamera(pointer, camera);
      const hit = raycaster.intersectObjects(molecule.atomMeshes, false)[0];
      selectAtom(hit ? String(hit.object.userData.atomId) : null);
      controls.autoRotate = false;
    };
    renderer.domElement.addEventListener("pointerdown", onPointerDown);

    let frame = 0;
    const render = () => {
      frame = requestAnimationFrame(render);
      controls.update();
      renderer.render(scene, camera);
    };
    render();

    return () => {
      cancelAnimationFrame(frame);
      resizeObserver.disconnect();
      renderer.domElement.removeEventListener("pointerdown", onPointerDown);
      renderer.domElement.removeEventListener("wheel", onWheel);
      controls.dispose();
      molecule.dispose();
      grid.geometry.dispose();
      (grid.material as THREE.Material).dispose();
      renderer.dispose();
      renderer.domElement.remove();
      fitViewRef.current = null;
    };
  }, [atoms, selectAtom, selectedAtomId, unit]);

  return (
    <section className="relative h-[380px] min-h-[380px] overflow-hidden border-y border-border bg-background sm:h-[520px] sm:min-h-[520px] lg:h-[clamp(180px,calc(100svh_-_500px),520px)] lg:min-h-[180px] lg:shrink-0">
      <div ref={containerRef} className="absolute inset-0" data-testid="molecule-canvas" />
      <div className="pointer-events-none absolute left-4 top-4 z-10">
        <p className="text-xs font-medium uppercase text-foreground/45">Molecule</p>
        <p className="mt-1 text-sm font-semibold">{atoms.length} atoms · {unit}</p>
      </div>
      <div className="absolute right-4 top-4 z-10 flex gap-2">
        <IconButton label="Visual bonds are inferred from covalent radii and do not affect the calculation">
          <Info size={15} />
        </IconButton>
        <IconButton label="Fit molecule and platform in view" onClick={() => fitViewRef.current?.()}>
          <Maximize2 size={15} />
        </IconButton>
      </div>
      {atoms.length === 0 ? (
        <div className="absolute inset-0 flex items-center justify-center text-sm text-foreground/45">
          Add an atom to begin.
        </div>
      ) : null}
    </section>
  );
}

function boxCorners(bounds: THREE.Box3) {
  const corners: THREE.Vector3[] = [];
  for (const x of [bounds.min.x, bounds.max.x]) {
    for (const y of [bounds.min.y, bounds.max.y]) {
      for (const z of [bounds.min.z, bounds.max.z]) {
        corners.push(new THREE.Vector3(x, y, z));
      }
    }
  }
  return corners;
}

function distanceToFitPoints(
  points: THREE.Vector3[],
  target: THREE.Vector3,
  viewDirection: THREE.Vector3,
  verticalFov: number,
  horizontalFov: number,
) {
  const forward = viewDirection.clone().negate();
  const right = forward.clone().cross(new THREE.Vector3(0, 1, 0)).normalize();
  const up = right.clone().cross(forward).normalize();
  const tanVertical = Math.tan(Math.max(verticalFov, 0.1) / 2);
  const tanHorizontal = Math.tan(Math.max(horizontalFov, 0.1) / 2);
  let requiredDistance = 0;

  for (const point of points) {
    const relative = point.clone().sub(target);
    const towardCamera = relative.dot(viewDirection);
    requiredDistance = Math.max(
      requiredDistance,
      towardCamera + Math.abs(relative.dot(right)) / tanHorizontal,
      towardCamera + Math.abs(relative.dot(up)) / tanVertical,
    );
  }

  return requiredDistance * 1.08;
}

function buildMolecule(atoms: AtomDraft[], unit: CoordinateUnit, selectedAtomId: string | null) {
  const group = new THREE.Group();
  const atomMeshes: THREE.Mesh[] = [];
  const disposables: Array<THREE.BufferGeometry | THREE.Material> = [];
  const positions = atoms.map((atom) => new THREE.Vector3(atom.x, atom.y, atom.z));

  atoms.forEach((atom, index) => {
    const style = elementStyle[atom.symbol] ?? { color: 0x94a3b8, radius: 0.8 };
    const geometry = new THREE.SphereGeometry(Math.max(0.22, style.radius * 0.43), 36, 24);
    const material = new THREE.MeshStandardMaterial({
      color: style.color,
      roughness: 0.32,
      metalness: atom.symbol === "Al" ? 0.38 : 0.06,
      emissive: atom.id === selectedAtomId ? 0x32d8bd : 0x000000,
      emissiveIntensity: atom.id === selectedAtomId ? 0.6 : 0,
    });
    const mesh = new THREE.Mesh(geometry, material);
    mesh.position.copy(positions[index]);
    mesh.userData.atomId = atom.id;
    group.add(mesh);
    atomMeshes.push(mesh);
    disposables.push(geometry, material);
  });

  const unitScale = unit === "bohr" ? 1.889726 : 1;
  for (let first = 0; first < atoms.length; first += 1) {
    for (let second = first + 1; second < atoms.length; second += 1) {
      const firstRadius = elementStyle[atoms[first].symbol]?.radius ?? 0.8;
      const secondRadius = elementStyle[atoms[second].symbol]?.radius ?? 0.8;
      const maxBondLength = (firstRadius + secondRadius) * 1.25 * unitScale;
      const distance = positions[first].distanceTo(positions[second]);
      if (distance > 0.05 && distance <= maxBondLength) {
        const bond = createBond(positions[first], positions[second]);
        group.add(bond.mesh);
        disposables.push(bond.geometry, bond.material);
      }
    }
  }

  group.updateMatrixWorld(true);
  const bounds = atoms.length > 0
    ? new THREE.Box3().setFromObject(group).expandByScalar(0.18)
    : new THREE.Box3(
      new THREE.Vector3(-1, -1, -1),
      new THREE.Vector3(1, 1, 1),
    );

  atomMeshes.forEach((mesh) => {
    if (String(mesh.userData.atomId) === selectedAtomId) mesh.scale.setScalar(1.16);
  });

  return {
    group,
    bounds,
    atomMeshes,
    dispose: () => disposables.forEach((item) => item.dispose()),
  };
}

function createBond(start: THREE.Vector3, end: THREE.Vector3) {
  const direction = new THREE.Vector3().subVectors(end, start);
  const midpoint = new THREE.Vector3().addVectors(start, end).multiplyScalar(0.5);
  const geometry = new THREE.CylinderGeometry(0.055, 0.055, direction.length(), 14);
  const material = new THREE.MeshStandardMaterial({
    color: 0x688781,
    roughness: 0.5,
    metalness: 0.12,
  });
  const mesh = new THREE.Mesh(geometry, material);
  mesh.position.copy(midpoint);
  mesh.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), direction.normalize());
  return { mesh, geometry, material };
}
