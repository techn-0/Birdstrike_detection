export interface CctvMeta {
  id: string;
  name: string;
  pos: [number, number];
  direction: number;
  angle: number;
  length: number;
  color?: string; // 색상(선택)
}

export interface Detection {
  cctv_id: string;
  bbox: number[];
  pos: number[];
  risk: "red" | "orange" | "yellow" | "green";
  captured_at: string;
  frame_url?: string;
  fov?: {
    direction: number;
    angle: number;
    length: number;
  };
  bird_count: number;
}