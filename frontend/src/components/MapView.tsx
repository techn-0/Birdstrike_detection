import React from "react";
import { MapContainer, TileLayer, Marker, Popup, Polygon, Tooltip, useMapEvents } from "react-leaflet";
import L from "leaflet";
import { CctvMeta } from "../types";
import FOVIndicator from "./FOVIndicator";

// 인천공항 실제 좌표 (위도, 경도)
const INCHEON_AIRPORT_CENTER: [number, number] = [37.4631, 126.4407];

const API = process.env.REACT_APP_API_HTTP;

// 지도 클릭 이벤트 핸들러 컴포넌트
function MapClickHandler({ onMapClick }: { onMapClick?: (lat: number, lng: number) => void }) {
  useMapEvents({
    click: (e) => {
      if (onMapClick) {
        onMapClick(e.latlng.lat, e.latlng.lng);
      }
    },
  });
  return null;
}

export default function MapView({
  cctvs,
  detections,
  onCctvClick,
  onMapClick,
  onCctvNameClick,
}: {
  cctvs: CctvMeta[];
  detections: any[];
  onCctvClick?: (cctvId: string) => void;
  onMapClick?: (lat: number, lng: number) => void;
  onCctvNameClick?: (cctvId: string) => void;
}) {
  const deg2rad = (deg: number) => (deg * Math.PI) / 180;

  // CCTV별로 가장 최근 탐지 결과만 추출
  const latestDetectionByCctv: { [cctvId: string]: any } = {};
  detections.forEach((d) => {
    if (
      !latestDetectionByCctv[d.cctv_id] ||
      new Date(d.captured_at) > new Date(latestDetectionByCctv[d.cctv_id].captured_at)
    ) {
      latestDetectionByCctv[d.cctv_id] = d;
    }
  });

  // 동그란 마커 스타일 동적 생성
  function getCctvIcon(color: string) {
    return L.divIcon({
      className: "",
      html: `<div style="
        width:22px;height:22px;
        background:${color};
        border-radius:50%;
        border:2px solid #fff;
        box-shadow:0 0 4px #0003;
        display:flex;align-items:center;justify-content:center;
      "></div>`,
      iconSize: [22, 22],
      iconAnchor: [11, 11],
    });
  }

  return (
    <div style={{ width: "100%", height: "100%" }}>
      <MapContainer
        center={INCHEON_AIRPORT_CENTER}
        zoom={14}         // 공항이 잘 보이는 줌 레벨
        style={{ height: "100%", width: "100%" }}
      >
        {/* OpenStreetMap 타일 레이어 */}
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {/* 지도 클릭 이벤트 핸들러 */}
        <MapClickHandler 
          onMapClick={(lat, lng) => {
            if (onMapClick) {
              onMapClick(lat, lng);
            }
          }} 
        />

        {/* CCTV 마커와 FOV */}
        {cctvs.map((c) => {
          // pos가 이미 [lat, lng] 형태라고 가정
          const markerPos: [number, number] = [c.pos[0], c.pos[1]];
          const center: [number, number] = [c.pos[0], c.pos[1]];
          
          // FOV 계산을 위한 거리(미터 단위)
          const distance = c.length; // length는 이미 미터 단위
          const half = c.angle / 2;
          const rad1 = deg2rad(c.direction - half);
          const rad2 = deg2rad(c.direction + half);
          
          // 위도/경도에서 거리 계산 (간단한 근사)
          const latOffset = (distance / 111320); // 1도 = 약 111,320m
          const lngOffset = (distance / (111320 * Math.cos(deg2rad(center[0]))));
          
          const left: [number, number] = [
            center[0] + latOffset * Math.cos(rad1),
            center[1] + lngOffset * Math.sin(rad1),
          ];
          const right: [number, number] = [
            center[0] + latOffset * Math.cos(rad2),
            center[1] + lngOffset * Math.sin(rad2),
          ];
          const polyCoords = [center, left, right];
          const color = c.color || "#007bff";

          return (
            <React.Fragment key={c.id}>
              <Marker
                position={markerPos}
                icon={getCctvIcon(color)}
                eventHandlers={{
                  click: () => onCctvClick && onCctvClick(c.id),
                }}
              >
                <Tooltip direction="bottom" offset={[0, 12]} permanent>
                  <span 
                    style={{ 
                      color: "#222", 
                      fontWeight: "bold", 
                      background: "#fff8", 
                      padding: "2px 6px", 
                      borderRadius: 4
                    }}
                  >
                    {c.name}
                  </span>
                </Tooltip>
                <Popup>
                  CCTV {c.name} ({c.id})
                </Popup>
              </Marker>
              <Polygon
                positions={polyCoords}
                pathOptions={{
                  color: color,
                  weight: 2,
                  fillOpacity: 0.15,
                  fillColor: color,
                }}
              />
            </React.Fragment>
          );
        })}

        {/* 각 CCTV별로 가장 최근 탐지 결과만 위험도 마커로 표시 */}
        {Object.values(latestDetectionByCctv).map((d: any, i) => {
          const cctv = cctvs.find((c) => c.id === d.cctv_id);
          if (!cctv) return null;
          const markerPos: [number, number] = [cctv.pos[0], cctv.pos[1]];
          return (
            <Marker
              key={i}
              position={markerPos}
              icon={L.divIcon({ className: `risk-${d.risk}` })}
            >
              <Popup>
                <b>탐지!</b>
                <br />
                CCTV {d.cctv_id}
                <br />
                Risk: {d.risk}
                <br />
                {d.frame_url && (
                  <img src={`${API}${d.frame_url}`} alt="frame" width={200} />
                )}
              </Popup>
            </Marker>
          );
        })}

        {/* AirBirds 탐지 결과 표시 - 실제 저장된 탐지 데이터 사용 */}
        {cctvs.map((cctv) => {
          // 해당 CCTV의 탐지 결과 필터링
          const cctvDetections = detections.filter(det => det.cctv_id === cctv.id);
          if (cctvDetections.length === 0) return null;
          
          // Detection 데이터를 ProcessedDetection 형식으로 변환
          const processedDetections = cctvDetections.map(det => ({
            cctv_id: det.cctv_id,
            pos: det.pos, // [u, v] 상대좌표
            class: "bird",
            confidence: det.confidence || 0.5,
            timestamp: det.captured_at,
            original_bbox: {
              x1: det.bbox[0],
              y1: det.bbox[1], 
              x2: det.bbox[0] + det.bbox[2],
              y2: det.bbox[1] + det.bbox[3]
            }
          }));
          
          return (
            <FOVIndicator
              key={`fov-${cctv.id}`}
              cameraLat={cctv.pos[0]}
              cameraLon={cctv.pos[1]}
              direction={cctv.direction}
              angle={cctv.angle}
              length={cctv.length}
              detections={processedDetections}
            />
          );
        })}
      </MapContainer>
    </div>
  );
}
