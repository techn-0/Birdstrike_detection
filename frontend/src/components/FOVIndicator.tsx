import React from 'react';
import { Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import { ProcessedDetection } from '../types';
import { computeWorldOffset, computeLatLon } from '../utils/geometry';

interface Props {
  cameraLat: number;
  cameraLon: number;
  direction: number;
  angle: number;
  length: number;
  detections: ProcessedDetection[];
  cctvMeta: any;
}

const FOVIndicator: React.FC<Props> = ({ 
  cameraLat,
  cameraLon,
  direction,
  angle,
  length,
  detections,
  cctvMeta
}) => {
  
  const getBirdIcon = (confidence: number): L.DivIcon => {
    // 새 이모지 선택
    let birdEmoji = '🐦';
    let bgColor = '#ffcc00';


    return L.divIcon({
      className: '',
      html: `<div style="
        font-size: 24px;
        text-align: center;
        line-height: 30px;
        width: 30px;
        height: 30px;
        border-radius: 50%;
        background-color: ${bgColor};
        border: 2px solid white;
        box-shadow: 0 2px 6px rgba(0,0,0,0.3);
        display: flex;
        align-items: center;
        justify-content: center;
      ">${birdEmoji}</div>`,
      iconSize: [30, 30],
      iconAnchor: [15, 15],
      popupAnchor: [0, -15]
    });
  };

  return (
    <>
      {detections.map((detection, idx) => {
        const [u, v] = detection.pos;
        
        // 상대좌표를 실제 지리적 위치로 변환
        const imageWidth = cctvMeta.resolution?.[0] || 1920;
        const imageHeight = cctvMeta.resolution?.[1] || 1080;

        const bbox = [
          detection.original_bbox.x1,
          detection.original_bbox.y1,
          detection.original_bbox.x2 - detection.original_bbox.x1,
          detection.original_bbox.y2 - detection.original_bbox.y1
        ];

        const [dx, dy] = computeWorldOffset(u, v, angle, length, direction, bbox, imageWidth, imageHeight);
        const [lat, lon] = computeLatLon(cameraLat, cameraLon, dx, dy);
        
        
        return (
          <Marker
            key={`bird-${idx}`}
            position={[lat, lon]}
            icon={getBirdIcon(detection.confidence)}
          >
            <Popup>
              <div className="bird-popup">
                <h4>🐦 {detection.class}</h4>
                <div className="detection-info">
                  <p><strong>신뢰도:</strong> {(detection.confidence * 100).toFixed(1)}%</p>
                  <p><strong>CCTV ID:</strong> {detection.cctv_id}</p>
                  <p><strong>탐지 시간:</strong> {new Date(detection.timestamp).toLocaleString()}</p>
                  <p><strong>원본 bbox:</strong> 
                    ({detection.original_bbox.x1.toFixed(0)}, {detection.original_bbox.y1.toFixed(0)}) - 
                    ({detection.original_bbox.x2.toFixed(0)}, {detection.original_bbox.y2.toFixed(0)})
                  </p>
                  <p><strong>상대좌표:</strong> ({u.toFixed(3)}, {v.toFixed(3)})</p>
                  <p><strong>실제 위치:</strong> ({lat.toFixed(6)}, {lon.toFixed(6)})</p>
                </div>
              </div>
            </Popup>
          </Marker>
        );
      })}
    </>
  );
};

export default FOVIndicator;
