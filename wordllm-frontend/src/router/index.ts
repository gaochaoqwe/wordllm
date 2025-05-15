import { createRouter, createWebHistory } from 'vue-router'
import TemplateList from '../views/template/TemplateList.vue'
import TemplateEdit from '../views/template/TemplateEdit.vue'
import ProjectList from '../views/project/ProjectList.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.VITE_BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: TemplateList
    },
    {
      path: '/templates',
      name: 'templates',
      component: TemplateList
    },
    {
      path: '/templates/create',
      name: 'template-create',
      component: TemplateEdit
    },
    {
      path: '/templates/:id',
      name: 'template-edit',
      component: TemplateEdit,
      props: true
    },
    {
      path: '/templates/:id/preview',
      name: 'template-preview',
      component: TemplateList,
      props: route => ({ previewId: parseInt(route.params.id as string) })
    },

    {
      path: '/projects/create-by-template',
      name: 'project-create-by-template',
      component: () => import('../views/project/ProjectCreateByTemplate.vue'),
    },
    {
      path: '/document/outline-result',
      name: 'outline-result',
      component: () => import('@/views/document/outlineResult/index.vue'),
      props: (route) => ({
        projectId: route.query.projectId,
        templateId: route.query.templateId ? Number(route.query.templateId) : null,
        inputFileName: route.query.inputFileName
      })
    },
    {
      path: '/projects',
      name: 'projects',
      component: ProjectList
    },
    {
      path: '/document/editor',
      name: 'document-editor',
      component: () => import('../views/document/contentedit/DocumentEditorContainer.vue')
    }
  ]
})

export default router
