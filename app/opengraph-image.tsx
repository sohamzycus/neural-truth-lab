import { ImageResponse } from "next/og";
import { SITE } from "@/lib/constants";

export const runtime = "edge";
export const alt = SITE.name;
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

export default function OpenGraphImage(): ImageResponse {
  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          background: "linear-gradient(135deg, #f6f4ef 0%, #e8f0fe 50%, #ecfdf5 100%)",
          color: "#1c1917",
          fontFamily: "system-ui, sans-serif",
        }}
      >
        <div
          style={{
            fontSize: 64,
            fontWeight: 700,
            letterSpacing: "-0.02em",
            background: "linear-gradient(90deg, #1d4ed8, #0f766e)",
            backgroundClip: "text",
            color: "transparent",
          }}
        >
          {SITE.name}
        </div>
        <div
          style={{
            marginTop: 24,
            fontSize: 28,
            color: "#94a3b8",
            maxWidth: 800,
            textAlign: "center",
          }}
        >
          {SITE.tagline}
        </div>
      </div>
    ),
    { ...size }
  );
}
