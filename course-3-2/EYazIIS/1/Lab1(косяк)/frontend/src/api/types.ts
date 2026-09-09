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

// API client stubs
export const api = {
  analyze: (file: File) => {/* POST /api/analyze */},
  getDictionary: (search?: string, pos?: string) => {/* GET /api/dictionary */},
  generateForm: (req: GenerateRequest) => {/* POST /api/generate */},
  getHelp: () => {/* GET /api/help */},
};