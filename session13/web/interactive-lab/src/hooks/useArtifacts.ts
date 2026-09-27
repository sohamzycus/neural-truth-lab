import { useEffect, useState } from "react";

export type LossPoint = { tokens: number; loss: number };

export type RunRow = {
  run_id: string;
  tokens_per_sec: number;
  final_loss: number;
  peak_mps_gb: number;
  peak_rss_gb: number;
  cpu_time_s: number;
  batch_size: number;
  sequence_length: number;
  tokens_trained: number;
  training_time_s: number;
  reversible_method: string;
  reconstruction_error: number | null;
  timestamp: string;
  device: string;
  parameter_count: number;
  loss_history: LossPoint[];
  memory_label: string;
  status: string;
};

export type HostProfile = {
  captured_at: string;
  cpu_brand: string;
  physical_cpus: string;
  logical_cpus: string;
  ram_gb: number;
  pytorch: string;
  mps_available: boolean;
  platform: string;
};

export function useArtifacts() {
  const [runs, setRuns] = useState<RunRow[]>([]);
  const [host, setHost] = useState<HostProfile | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      fetch("/data/results.json").then((r) => r.json()),
      fetch("/data/host_profile.json").then((r) => r.json()),
    ])
      .then(([r, h]) => {
        setRuns(r);
        setHost(h);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  const baseline = runs.find((r) => r.run_id.includes("baseline"));
  const euler = runs.find((r) => r.run_id.includes("euler") && r.batch_size === 8);
  const midpoint = runs.find((r) => r.reversible_method === "midpoint");
  const maxBatch = runs.find((r) => r.run_id.startsWith("max_batch"));

  return { loading, runs, host, baseline, euler, midpoint, maxBatch };
}
