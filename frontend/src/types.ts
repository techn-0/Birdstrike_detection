export interface CctvMeta {
  id: string;
  name: string;
  pos: [number, number];
  direction: number;
  angle: number;
  length: number;
  color?: string; // 색상(선택)
}