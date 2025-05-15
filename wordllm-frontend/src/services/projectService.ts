import axios from 'axios';

const API_URL = '/api'; // Adjust if your API base URL is different

export interface Project {
  id: number;
  // 原始字段
  title?: string;
  // 新增字段
  project_name?: string;
  template_name?: string;
  // 其他字段
  template_id: number;
  created_at: string;
  updated_at: string;
}

export interface PaginatedProjectsResponse {
  success: boolean;
  data: Project[];
  total: number;
  pages: number;
  current_page: number;
  per_page: number;
  has_next: boolean;
  has_prev: boolean;
  message?: string;
}

interface FetchProjectsParams {
  page: number;
  per_page: number;
  title?: string;
}

export const fetchProjects = async (page: number, perPage: number, title?: string): Promise<PaginatedProjectsResponse> => {
  try {
    const params: FetchProjectsParams = {
      page,
      per_page: perPage,
    };
    if (title && title.trim() !== '') {
      params.title = title.trim();
    }
    const response = await axios.get<PaginatedProjectsResponse>(`${API_URL}/projects`, { params });
    return response.data;
  } catch (error) {
    console.error('Error fetching projects:', error);
    // Consider how you want to handle errors, e.g., rethrow, return a default, etc.
    // For now, rethrowing to be caught by the component.
    throw error;
  }
};

// Placeholder for create project - to be implemented
export const createProject = async (projectData: { title: string; templateId: number }) => {
  try {
    const response = await axios.post(`${API_URL}/projects`, projectData);
    return response.data;
  } catch (error) {
    console.error('Error creating project:', error);
    throw error;
  }
};

// Placeholder for delete project - to be implemented
export const deleteProject = async (projectId: number) => {
  try {
    const response = await axios.delete(`${API_URL}/projects/${projectId}`);
    return response.data;
  } catch (error) {
    console.error('Error deleting project:', error);
    throw error;
  }
};

// Placeholder for update project - to be implemented
export const updateProject = async (projectId: number, projectData: Partial<Project>) => {
  try {
    const response = await axios.put(`${API_URL}/projects/${projectId}`, projectData);
    return response.data;
  } catch (error) {
    console.error('Error updating project:', error);
    throw error;
  }
};

// Placeholder for fetching a single project - to be implemented
export const getProjectDetails = async (projectId: number) => {
  try {
    const response = await axios.get(`${API_URL}/projects/${projectId}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching project details:', error);
    throw error;
  }
};
