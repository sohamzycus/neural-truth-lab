"use client";

import { useEffect, useRef } from "react";
import { PARTICLE_CONFIG } from "@/animations/particles";
import { useReducedMotion } from "@/hooks/useReducedMotion";

interface Node {
  x: number;
  y: number;
  bx: number;
  by: number;
  vx: number;
  vy: number;
  phase: number;
}

function createNodes(width: number, height: number): Node[] {
  const count =
    window.innerWidth < 768
      ? PARTICLE_CONFIG.mobileNodeCount
      : PARTICLE_CONFIG.nodeCount;

  return Array.from({ length: count }, () => {
    const x = Math.random() * width;
    const y = Math.random() * height;
    return { x, y, bx: x, by: y, vx: 0, vy: 0, phase: Math.random() * Math.PI * 2 };
  });
}

export function HeroAnimation(): React.ReactElement {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const mouseRef = useRef({ x: -1000, y: -1000 });
  const nodesRef = useRef<Node[]>([]);
  const reducedMotion = useReducedMotion();

  useEffect(() => {
    if (reducedMotion) return;

    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    let animationId = 0;
    let width = 0;
    let height = 0;

    const resize = (): void => {
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      const rect = canvas.getBoundingClientRect();
      width = rect.width;
      height = rect.height;
      canvas.width = width * dpr;
      canvas.height = height * dpr;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      nodesRef.current = createNodes(width, height);
    };

    const tick = (time: number): void => {
      const {
        mouseRepelRadius,
        mouseRepelStrength,
        connectionDistance,
        idleDrift,
        springStrength,
        damping,
      } = PARTICLE_CONFIG;

      ctx.clearRect(0, 0, width, height);
      const nodes = nodesRef.current;
      const mx = mouseRef.current.x;
      const my = mouseRef.current.y;

      for (const node of nodes) {
        node.x += Math.cos(time * 0.001 + node.phase) * idleDrift;
        node.y += Math.sin(time * 0.001 + node.phase * 1.3) * idleDrift;

        const dx = node.x - mx;
        const dy = node.y - my;
        const dist = Math.hypot(dx, dy);
        if (dist < mouseRepelRadius && dist > 0) {
          const force = (1 - dist / mouseRepelRadius) * mouseRepelStrength * 8;
          node.vx += (dx / dist) * force;
          node.vy += (dy / dist) * force;
        }

        node.vx += (node.bx - node.x) * springStrength;
        node.vy += (node.by - node.y) * springStrength;
        node.vx *= damping;
        node.vy *= damping;
        node.x += node.vx;
        node.y += node.vy;

        if (node.x < 0) node.x = width;
        if (node.x > width) node.x = 0;
        if (node.y < 0) node.y = height;
        if (node.y > height) node.y = 0;
      }

      // ponytail: O(n²) edge scan fine for ≤100 nodes; spatial hash if count grows
      for (let i = 0; i < nodes.length; i++) {
        for (let j = i + 1; j < nodes.length; j++) {
          const edx = nodes[i].x - nodes[j].x;
          const edy = nodes[i].y - nodes[j].y;
          const edgeDist = Math.hypot(edx, edy);
          if (edgeDist < connectionDistance) {
            const alpha = (1 - edgeDist / connectionDistance) * 0.35;
            ctx.strokeStyle = `rgba(99, 102, 241, ${alpha})`;
            ctx.lineWidth = 1;
            ctx.beginPath();
            ctx.moveTo(nodes[i].x, nodes[i].y);
            ctx.lineTo(nodes[j].x, nodes[j].y);
            ctx.stroke();
          }
        }
      }

      for (const node of nodes) {
        const pulse = 0.5 + 0.5 * Math.sin(time * 0.002 + node.phase);
        ctx.fillStyle = `rgba(139, 92, 246, ${0.35 + pulse * 0.45})`;
        ctx.beginPath();
        ctx.arc(node.x, node.y, 2 + pulse * 0.5, 0, Math.PI * 2);
        ctx.fill();
      }

      animationId = requestAnimationFrame(tick);
    };

    const onMouseMove = (e: MouseEvent): void => {
      const rect = canvas.getBoundingClientRect();
      mouseRef.current = {
        x: e.clientX - rect.left,
        y: e.clientY - rect.top,
      };
    };

    const onMouseLeave = (): void => {
      mouseRef.current = { x: -1000, y: -1000 };
    };

    resize();
    window.addEventListener("resize", resize);
    canvas.addEventListener("mousemove", onMouseMove);
    canvas.addEventListener("mouseleave", onMouseLeave);
    animationId = requestAnimationFrame(tick);

    return () => {
      cancelAnimationFrame(animationId);
      window.removeEventListener("resize", resize);
      canvas.removeEventListener("mousemove", onMouseMove);
      canvas.removeEventListener("mouseleave", onMouseLeave);
    };
  }, [reducedMotion]);

  if (reducedMotion) {
    return (
      <div
        className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_center,rgba(99,102,241,0.15)_0%,transparent_70%)]"
        aria-hidden
      />
    );
  }

  return (
    <canvas
      ref={canvasRef}
      className="absolute inset-0 h-full w-full"
      aria-hidden
    />
  );
}
