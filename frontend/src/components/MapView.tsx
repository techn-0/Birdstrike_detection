import { MapContainer, ImageOverlay, Marker, Popup } from "react-leaflet";
import L from "leaflet";

interface Det {
  _id?: string;
  cctv_id: string;
  pos: [number, number];      // [u,v] 0~1
  risk: string;
  frame_url?: string;
}

const bounds: L.LatLngBoundsExpression = [[0, 0], [647, 1000]]; // 배경 해상도 세로, 가로
const API = process.env.REACT_APP_API_HTTP;   // http://localhost:8000

export default function MapView({ detections }: { detections: Det[] }) {
  return (
    <MapContainer
      crs={L.CRS.Simple}
      bounds={bounds}
      style={{ height: "100vh", width: "100vw" }}
    >
      <ImageOverlay url="/airport_bg.png" bounds={bounds} />
      {detections.map((d, i) => (
        <Marker
          key={i}
          position={[d.pos[1] * 647, d.pos[0] * 1000]}
          icon={L.divIcon({ className: `risk-${d.risk}` })}
        >
          <Popup>
            CCTV {d.cctv_id}<br />
            Risk: {d.risk}<br />
            {d.frame_url && (
              <img
              src={`${API}${d.frame_url}`}
              alt="frame"
              width={200}
              />
            )}
          </Popup>
        </Marker>
      ))}
    </MapContainer>
  );
}
