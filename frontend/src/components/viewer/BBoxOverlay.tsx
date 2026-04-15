"use client";

import type { OCRMatch } from "@/types";

type Props = {
  matches: OCRMatch[];
  page?: number;
};

/** Renders an absolutely-positioned SVG overlay with one highlight per match.
 *  The parent element must be `position: relative` and sized to the rendered
 *  image so that percentages map correctly. */
export function BBoxOverlay({ matches, page = 1 }: Props) {
  const visible = matches.filter((m) => (m.bbox.page ?? 1) === page);
  return (
    <svg
      className="absolute inset-0 w-full h-full pointer-events-none"
      preserveAspectRatio="none"
      viewBox="0 0 100 100"
    >
      {visible.map((m, i) => (
        <g key={i}>
          <rect
            x={m.bbox.x * 100}
            y={m.bbox.y * 100}
            width={m.bbox.w * 100}
            height={m.bbox.h * 100}
            fill="rgba(99,102,241,0.25)"
            stroke="rgba(99,102,241,1)"
            strokeWidth={0.3}
            vectorEffect="non-scaling-stroke"
          />
        </g>
      ))}
    </svg>
  );
}
