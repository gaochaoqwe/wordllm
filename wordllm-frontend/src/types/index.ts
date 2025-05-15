export type SimilarityType = 'COSINE' | 'EUCLIDEAN' | 'MANHATTAN' | 'DOT_PRODUCT';

export type VectorType = 'MILVUS' | 'PINECONE' | 'QDRANT';

export interface VectorConfig {
  type: VectorType;
  url: string;
  collection: string;
  dimension: number;
  similarity: SimilarityType;
}

export interface KnowledgeBase {
  type: string;
  url: string;
  collection: string;
  dimension: number;
  similarity: SimilarityType;
}

export interface Template {
  id?: string;
  name: string;
  description?: string;
  rules?: string;
  vectorConfig: VectorConfig;
  knowledgeBase?: KnowledgeBase;
  modelId?: string;
}

export interface Model {
  id: string;
  name: string;
  type: string;
  status: string;
}

export interface Chapter {
  id: string;
  title: string;
  content?: string;
  status: ChapterStatus;
  currentWords: number;
  requiredWords: number;
  parentId?: string;
  order?: number;
}

export type ChapterStatus = 'unwritten' | 'writing' | 'completed';
