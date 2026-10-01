import { Navigate, Route, Routes } from "react-router-dom";
import { AppLayout } from "./layouts/AppLayout";
import { DashboardPage } from "./pages/DashboardPage";
import { DevicesPage } from "./pages/DevicesPage";
import { EncryptionLabPage } from "./pages/EncryptionLabPage";
import { LiveIotPage } from "./pages/LiveIotPage";
import { SecurityEventsPage } from "./pages/SecurityEventsPage";
import { PlaceholderPage } from "./pages/PlaceholderPage";

export default function App() {
  return <Routes>
    <Route element={<AppLayout />}>
      <Route index element={<DashboardPage />} />
      <Route path="devices" element={<DevicesPage />} />
      <Route path="encryption-lab" element={<EncryptionLabPage />} />
      <Route path="live-iot" element={<LiveIotPage />} />
      <Route path="security-events" element={<SecurityEventsPage />} />
      <Route path="benchmarks" element={<PlaceholderPage title="Benchmarks" />} />
      <Route path="audit-logs" element={<PlaceholderPage title="Audit Logs" />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Route>
  </Routes>;
}
