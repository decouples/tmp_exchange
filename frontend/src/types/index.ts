export type UserRead = {
  id: number;
  email: string;
  name: string;
  is_active: boolean;
  created_at: string;
};

export type TokenResponse = {
  access_token: string;
  token_type: string;
  user: UserRead;
};

export type FileRead = {
  id: number;
  filename: string;
  content_type: string;
  size: number;
  md5: string;
  page_count: number;
  created_at: string;
};

export type BoundingBox = {
  x: number;
  y: number;
  w: number;
  h: number;
  page: number;
};

export type OCRMatch = {
  text: string;
  confidence: number;
  bbox: BoundingBox;
};

export type OCRResult = {
  matches: OCRMatch[];
  engine: string;
  elapsed_ms: number;
};

export type OCRTask = {
  id: number;
  task_id: string;
  file_id: number;
  query: string;
  status: "PENDING" | "QUEUED" | "PROCESSING" | "SUCCESS" | "FAILED" | "CANCELLED";
  progress: number;
  result: OCRResult | null;
  error: string | null;
  created_at: string;
  updated_at: string;
};
