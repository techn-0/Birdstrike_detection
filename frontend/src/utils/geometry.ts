// geometry.ts - 기하학적 계산 유틸리티
import { AirBirdsDetection, ProcessedDetection } from '../types';

/**
 * AirBirds 탐지 결과를 상대좌표로 변환
 */
export function convertAirBirdsToRelative(
  airbirdsData: AirBirdsDetection
): ProcessedDetection[] {
  const [height, width] = airbirdsData.image_shape;
  
  return airbirdsData.detections.map(detection => {
    const centerX = (detection.bbox.x1 + detection.bbox.x2) / 2;
    const centerY = (detection.bbox.y1 + detection.bbox.y2) / 2;
    
    return {
      cctv_id: extractCctvId(airbirdsData.image_name),
      pos: [centerX / width, centerY / height],
      class: detection.class_name,
      confidence: detection.confidence,
      timestamp: extractTimestamp(airbirdsData.image_name),
      original_bbox: detection.bbox
    };
  });
}

/**
 * 이미지명에서 CCTV ID 추출
 */
function extractCctvId(imageName: string): string {
  return imageName.split("_")[0] || "unknown";
}

/**
 * 이미지명에서 타임스탬프 추출
 */
function extractTimestamp(imageName: string): string {
  const parts = imageName.split("_");
  if (parts.length >= 3) {
    const dateStr = parts[1];
    const timeStr = parts[2].split(".")[0];
    
    const year = dateStr.substr(0, 4);
    const month = dateStr.substr(4, 2);
    const day = dateStr.substr(6, 2);
    const hour = timeStr.substr(0, 2);
    const minute = timeStr.substr(2, 2);
    const second = timeStr.substr(4, 2);
    
    return `${year}-${month}-${day}T${hour}:${minute}:${second}Z`;
  }
  return new Date().toISOString();
}

/**
 * 상대좌표를 실제 지리적 위치로 변환
 */
export function computeWorldOffset(
  u: number, 
  v: number, 
  fovAngle: number, 
  fovLength: number, 
  direction: number
): [number, number] {
  const angleOffset = (u - 0.5) * fovAngle;
  const distance = v * fovLength * 1000; // km를 m로 변환
  
  const actualBearing = direction + angleOffset;
  const radians = (actualBearing * Math.PI) / 180;
  
  const dx = distance * Math.sin(radians);
  const dy = distance * Math.cos(radians);
  
  return [dx, dy];
}

/**
 * 거리 오프셋을 위도/경도로 변환
 */
export function computeLatLon(
  centerLat: number, 
  centerLon: number, 
  dx: number, 
  dy: number
): [number, number] {
  const earthRadius = 6371000; // 지구 반지름 (미터)
  
  const dLat = dy / earthRadius;
  const dLon = dx / (earthRadius * Math.cos((centerLat * Math.PI) / 180));
  
  const newLat = centerLat + (dLat * 180) / Math.PI;
  const newLon = centerLon + (dLon * 180) / Math.PI;
  
  return [newLat, newLon];
}
