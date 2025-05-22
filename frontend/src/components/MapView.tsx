import React from "react";
import { MapContainer, ImageOverlay, Marker, Popup, Polygon } from "react-leaflet";
import L from "leaflet";

interface Det {
  _id?: string;
  cctv_id: string;
  pos: [number, number];      // [u,v] 0~1
  risk: "red" | "orange" | "yellow" | "green";
  frame_url?: string;
  fov?: [number, number][];   // [[u,v], …] (0~1 정규화)
}

const bounds: L.LatLngBoundsExpression = [[0, 0], [647, 1000]]; // 배경 해상도 세로, 가로
const API = process.env.REACT_APP_API_HTTP;   // http://localhost:8000

export default function MapView({ detections }: { detections: Det[] }) {
  return (
    <MapContainer
      crs={L.CRS.Simple}
      bounds={bounds}
      style={{ height: "90vh", width: "90vw" }}
    >
      <ImageOverlay url="/airport_bg.png" bounds={bounds} />

      {detections.map((d, i) => {
        // 1) 마커 위치 계산
        const markerPos: [number, number] = [d.pos[1] * 647, d.pos[0] * 1000];

        // 2) fov 좌표가 있을 때, 다각형용 좌표로 변환
        const polyCoords: [number, number][] | undefined = d.fov?.map(
          ([u, v]) => [v * 647, u * 1000] as [number, number]
        );

        return (
          <React.Fragment key={i}>
            {/* 마커 */}
            <Marker
              position={markerPos}
              icon={L.divIcon({ className: `risk-${d.risk}` })}
            >
              <Popup>
                CCTV {d.cctv_id}<br />
                Risk: {d.risk}<br />
                {d.frame_url && (
                  <img src={`${API}${d.frame_url}`} alt="frame" width={200} />
                )}
              </Popup>
            </Marker>

            {/* FOV 다각형 */}
            {polyCoords && (
              <Polygon
                positions={polyCoords}
                pathOptions={{
                  color:
                    d.risk === "red"
                      ? "#f03"
                      : d.risk === "orange"
                      ? "#f80"
                      : d.risk === "yellow"
                      ? "#fc0"
                      : "#0a0",
                  weight: 2,
                  fillOpacity: 0.1,
                }}
              />
            )}
          </React.Fragment>
        );
      })}
    </MapContainer>
  );
}
