export interface Benchmark {
  test_name: string;
  score: number;
  unit: string;
  source_url: string;
}

export interface PackageStats {
  total_packages: number;
  outdated_packages: number;
  vulnerable_packages: number;
  newest_packages: number;
  problematic_packages: number;
  source_url: string;
}

export interface Distro {
  id: number;
  slug: string;
  url: string;
  name: string;
  based_on: string[];
  origin: string | null;
  architecture: string[];
  desktop: string[];
  category: string[];
  status: string | null;
  latest_version: string | null;
  description: string | null;
  popularity_rank: number | null;
  hits_per_day: number | null;
  use_cases: string[];
  difficulty: number;
  min_ram_gb: number | null;
  min_storage_gb: number | null;
  recommended_for: string[];
  architectures: string[];
  package_manager?: string | null;
  init_system?: string | null;
  release_model?: string | null;
  technical_notes?: string | null;
  benchmarks?: Benchmark[];
  package_stats?: PackageStats | null;
}

export interface RecommendResult {
  distro: Distro;
  similarity: number;
  source: "database" | "ai_cache" | "llm";
  ai_reason?: string | null;
}

export interface RecommendRequest {
  ram_gb?: number | null;
  storage_gb?: number | null;
  use_cases?: string[];
  architecture?: string | null;
  difficulty?: number[];
  free_text?: string;
  limit?: number;
}
