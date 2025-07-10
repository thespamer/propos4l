export interface PerformanceMetric {
  avg_duration: number;
  max_duration: number;
  min_duration: number;
  avg_memory: number;
  avg_cpu: number;
  count: number;
  last_execution: string;
}

export interface SystemMetric {
  cpu_percent: number;
  memory_percent: number;
  memory_available: number;
  disk_usage: number;
}

export interface ProcessingStats {
  documents: {
    total: number;
    processed: number;
    processing_rate: number;
  };
  blocks: {
    total: number;
    by_type: Record<string, number>;
    avg_length: number;
    confidence_scores: {
      high: number;
      medium: number;
      low: number;
    };
  };
}

export interface NLPMetrics {
  entity_types: Record<string, number>;
  avg_key_phrases: number;
  avg_technical_terms: number;
  complexity_scores: {
    high: number;
    medium: number;
    low: number;
  };
}

export interface DashboardData {
  performance: Record<string, PerformanceMetric>;
  system_health: {
    current: SystemMetric;
    history: Array<{
      timestamp: string;
      metrics: SystemMetric;
    }>;
  };
}

export interface ProcessingData {
  processing_stats: ProcessingStats;
  nlp_metrics: NLPMetrics;
}

export interface TreemapItem {
  name: string;
  size: number;
  duration: number;
  memory: number;
  cpu: number;
}

export interface HeatmapItem {
  name: string;
  x: number;
  y: number;
  z: number;
  value: number;
}

export interface TooltipProps {
  payload?: Array<{
    payload: HeatmapItem;
  }>;
}

export interface TreemapContentProps {
  root: any;
  depth: number;
  x: number;
  y: number;
  width: number;
  height: number;
  index: number;
  payload: any;
  colors: string[];
  rank: number;
  name: string;
}
