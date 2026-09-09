export interface MorphRule {
  ending: string;
  grammemes: Record<string, string>;
}

export interface LemmaEntry {
  lemma: string;
  stem: string;
  pos: string;
  rules: MorphRule[];
  frequency: number;
  meta?: string;
}

export interface AnalysisResult {
  total_tokens: number;
  unique_lemmas: number;
  lemmas: LemmaEntry[];
  processing_time_ms: number;
}

export interface GenerateRequest {
  lemma: string;
  grammemes: Record<string, string>;
}

export interface GenerateResponse {
  form: string | null;
  source_rule?: MorphRule;
}

export const api = {
  analyze: (_file: File) => {/* POST /api/analyze */},
  getDictionary: (_search?: string, _pos?: string) => {/* GET /api/dictionary */},
  generateForm: (_req: GenerateRequest) => {/* POST /api/generate */},
  getHelp: () => {/* GET /api/help */},
};