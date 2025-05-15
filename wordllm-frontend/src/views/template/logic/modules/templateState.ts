/**
 * 模板状态管理模块
 * 处理所有与模板相关的状态数据
 */
import { ref, reactive } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import type { Template } from '../../../../types/template'

/**
 * 创建并导出模板管理所需的各种状态
 */
export function createTemplateState() {
  // 列表状态
  const loading = ref(false)
  const templates = ref<Template[]>([])
  const total = ref(0)
  
  // 分页状态
  const currentPage = ref(1)
  const pageSize = ref(10)
  
  // 搜索状态
  const searchTitle = ref('')
  
  // 弹窗状态
  const formVisible = ref(false)
  const submitting = ref(false)
  const editMode = ref(false)
  const uploadNewFile = ref(false)
  const currentTemplate = ref<Template | null>(null)
  
  // 预览状态
  const previewVisible = ref(false)
  const previewDocId = ref<number | string>(0)
  
  // 表单引用
  const formRef = ref<FormInstance>()
  // 使用更准确的类型代替any
  const fileUploaderRef = ref<{ clearFile: () => void } | null>(null)
  
  // 表单数据
  const form = reactive({
    id: 0,
    title: '',
    content: '',
    outline_prompt: '',
    subchapter_prompt: '',
    content_prompt: '',
    file: null as File | null
  })
  
  // 表单验证规则
  const rules = reactive<FormRules>({
    title: [
      { required: true, message: '请输入标题', trigger: 'blur' },
      { min: 2, max: 50, message: '标题长度应在2-50个字符之间', trigger: 'blur' }
    ],
    file: [
      { 
        required: true, 
        validator: (_rule, _value, callback) => {
          if (!editMode.value || (editMode.value && uploadNewFile.value)) {
            if (!form.file) {
              callback(new Error('请选择文件'))
              return
            }
          }
          callback()
        }, 
        trigger: 'change' 
      }
    ]
  })

  return {
    // 列表状态
    loading,
    templates,
    total,
    
    // 分页状态
    currentPage,
    pageSize,
    
    // 搜索状态
    searchTitle,
    
    // 弹窗状态
    formVisible,
    submitting,
    editMode,
    uploadNewFile,
    currentTemplate,
    
    // 预览状态
    previewVisible,
    previewDocId,
    
    // 表单相关
    formRef,
    fileUploaderRef,
    form,
    rules
  }
}
