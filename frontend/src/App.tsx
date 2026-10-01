import { Navigate, Route, Routes } from "react-router-dom";
import { AppLayout } from "./layouts/AppLayout";
import { DashboardPage } from "./pages/DashboardPage";
import { DevicesPage } from "./pages/DevicesPage";
import { EncryptionLabPage } from "./pages/EncryptionLabPage";
import { LiveIotPage } from "./pages/LiveIotPage";
import { SecurityEventsPage } from "./pages/SecurityEventsPage";
import { BenchmarksPage } from "./pages/BenchmarksPage";
import { AuditLogsPage } from "./pages/AuditLogsPage";

export default function App() {
  return <Routes>
    <Route element={<AppLayout />}>
      <Route index element={<DashboardPage />} />
      <Route path="devices" element={<DevicesPage />} />
      <Route path="encryption-lab" element={<EncryptionLabPage />} />
      <Route path="live-iot" element={<LiveIotPage />} />
      <Route path="security-events" element={<SecurityEventsPage />} />
      <Route path="benchmarks" element={<BenchmarksPage />} />
      <Route path="audit-logs" element={<AuditLogsPage />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Route>
  </Routes>;
}
