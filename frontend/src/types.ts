export interface CctvMeta {
  id: string;
  name: string;
  pos: [number, number];
  direction: number;
  angle: number;
  length: number;
  color?: string; // 색상(선택)
  sensor_size?: [number, number]; // 센서 크기 [가로, 세로] (mm)
  resolution?: [number, number];  // 해상도 [가로, 세로]
  focal_length?: number;          // 초점거리 (mm)
  sensor_diagonal?: number;       // 센서 대각선 길이 (mm)
  crop_factor?: number;           // 크롭팩터
  model_name?: string;            // 모델명
  is_photo_slides?: boolean;      // 사진 슬라이드 활성화 여부
}

// AirBirds 탐지 결과 형식
export interface AirBirdsDetection {
  image_path: string;
  image_name: string;
  image_shape: [number, number];  // [height, width]
  detections: Array<{
    class_id: number;
    class_name: string;
    confidence: number;
    bbox: {
      x1: number;
      y1: number;
      x2: number;
      y2: number;
    };
  }>;
}

// 처리된 탐지 결과
export interface ProcessedDetection {
  cctv_id: string;
  pos: [number, number];  // [u, v] 상대좌표
  class: string;
  confidence: number;
  timestamp: string;
  geo_pos?: [number, number];  // [lat, lon] 지리적 좌표
  original_bbox: {
    x1: number;
    y1: number;
    x2: number;
    y2: number;
  };
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

// 포토 슬라이드 관련 타입들
export interface PhotoSlideImage {
  image_name: string;
  image_url: string;
  labels: DetectionLabel[];
  max_confidence: number;
  detection_count: number;
}

export interface DetectionLabel {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
  confidence: number;
  class_name: string;
}

export interface PhotoSlidesData {
  cctv_id: string;
  total_images: number;
  confidence_threshold: number;
  images: PhotoSlideImage[];
}