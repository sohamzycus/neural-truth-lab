
export type RunRow = {
  run_id: string; status: string; parameter_count: number; tokens_trained: number;
  batch_size: number; sequence_length: number; tokens_per_sec: number; final_loss: number;
  peak_memory_gb: number; reversible_method: string; loss_history?: {tokens:number;loss:number}[];
};
export async function loadResults(): Promise<RunRow[]> {
  try {
    const r = await fetch("/data/results.json");
    return await r.json();
  } catch { return []; }
}
