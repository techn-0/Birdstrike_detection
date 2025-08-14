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
  // CSV 형식에서 추가된 필드들
  image_name?: string;
  image_path?: string;
  object_id?: number;
  class_name?: string;
  confidence: number;
  width?: number;
  height?: number;
}

// CSV 형식 전용 인터페이스
export interface DetectionCSV {
  image_index: number;
  image_path: string;
  image_name: string;
  object_id: number;
  class_name: string;
  class_id: number;
  x1: number;
  y1: number;
  x2: number;
  y2: number;
  confidence: number;
  width: number;
  height: number;
  center_x: number;
  center_y: number;
  cctv_id?: string;
  captured_at?: string;
}