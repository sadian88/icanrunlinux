import { useCallback } from "react";
import { Routes, Route, useNavigate } from "react-router-dom";
import type { RecommendRequest } from "./types/distro";
import HomePage from "./pages/HomePage";
import ResultsPage from "./pages/ResultsPage";

export default function App() {
  const navigate = useNavigate();

  const handleSearch = useCallback(
    (req: RecommendRequest) => {
      navigate("/results", { state: { request: req } });
    },
    [navigate],
  );

  return (
    <Routes>
      <Route path="/" element={<HomePage onSubmit={handleSearch} />} />
      <Route path="/results" element={<ResultsPage />} />
    </Routes>
  );
}
