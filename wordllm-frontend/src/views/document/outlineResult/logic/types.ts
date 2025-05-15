// 定义类型
export interface Chapter {
  id?: number | null;
  chapter_number?: string; // 后端返回的是这个
  chapterNumber?: string; // 前端可能用这个
  title: string;
  children: Chapter[];
  requirement?: string;
  // 其他可能的章节属性
  // [key: string]: any; // Removed to address lint error and enforce stricter typing
}

export interface OutlineState {
  chapters: Chapter[];
  templateId: number | null;
  templateTitle: string;
  inputFileName: string;
  inputFilePath: string | null;
  projectId: string | null;
  allChecked: boolean;
  hasGeneratedSubchapters: boolean;
  isGeneratingDocument: boolean;
}

export interface PreviewState {
  previewVisible: boolean;
  previewTitle: string;
  previewDocId: number | null;
  previewFilePath: string | null;
}

import { Ref } from 'vue'

export interface RegenerateState {
  isRegenerating: Ref<boolean>;
  regenerateRequirement: Ref<string>;
  currentChapterId: Ref<number | null>;
}
