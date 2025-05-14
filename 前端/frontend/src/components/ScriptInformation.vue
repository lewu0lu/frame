<script setup>
import {onMounted, ref, watch, reactive} from "vue";
import ScriptDrawer from "@/components/ScriptDrawer.vue";
import {getScriptAllVersion, getScriptCurrentVersion, runScript} from "@/api/script_api.js";
import { Message } from "@arco-design/web-vue";

const origin_version_info = ref({})
const script_versions_info = ref([]);
const drawer_visible = ref(false);
const script_info = ref([]);
const run_modal_visible = ref(false);
const script_parameters = ref({});
const script_result = ref(null);
const loading = ref(false);
const props = defineProps({
  script_url: String,
});

// 显示脚本抽屉并获取所有版本信息
function showScriptDrawer() {
  drawer_visible.value = true;
  getScriptAllVersion({script_url: props.script_url}).then(res => {
    script_versions_info.value = res["version_info"];
  }).catch(err => {
    console.log(err);
  });
}

const conversion_info = ref([]);
const show_conversion_modal = ref(false);

// 显示运行脚本对话框
function showRunScriptModal() {
  run_modal_visible.value = true;
  // 初始化参数为空对象
  script_parameters.value = {};
  script_result.value = null;
  conversion_info.value = [];
  
  // 如果脚本有输入参数，为每个参数创建默认值
  if (origin_version_info.value && origin_version_info.value.input) {
    const inputParams = origin_version_info.value.input;
    // 为每个输入参数设置空值或默认值
    inputParams.forEach(param => {
      if (typeof param === 'object' && param.name) {
        // 如果参数是对象并且有name属性
        script_parameters.value[param.name] = param.default && param.default !== 'null' && param.default !== 'NotNone' 
          ? param.default 
          : '';
      } else if (typeof param === 'string') {
        // 如果参数是字符串（兼容旧格式）
        script_parameters.value[param] = '';
      }
    });
  }
}

// 确认参数转换并执行脚本
function confirmAndRunScript() {
  show_conversion_modal.value = false;
  // 使用force_run标记执行脚本
  executeScript(true);
}

// 执行脚本
function executeScript(forceRun = false) {
  if (!props.script_url) return;
  
  loading.value = true;
  script_result.value = null;
  
  runScript(props.script_url, script_parameters.value, forceRun)
    .then(res => {
      script_result.value = res;
      
      if (res.status) {
        Message.success('脚本执行成功');
        // 如果有参数转换，显示转换信息
        if (res.conversions && res.conversions.length > 0) {
          conversion_info.value = res.conversions;
        }
      } else if (res.require_confirmation && res.conversions) {
        // 需要确认参数转换
        conversion_info.value = res.conversions;
        show_conversion_modal.value = true;
      } else {
        // 处理参数校验失败的错误
        if (res.message && res.message.includes('参数校验失败')) {
          // 解析参数校验失败的详细信息
          const errorMsg = res.message.replace('参数校验失败：', '');
          const errors = errorMsg.split('; ');
          
          // 创建格式化的错误消息
          let formattedError = '<div style="text-align:left"><strong>参数校验错误:</strong><ul style="padding-left:20px;margin-top:5px">';
          errors.forEach(err => {
            // 处理类型不匹配的错误，改为更友好的格式
            if (err.includes('转换类型失败')) {
              const parts = err.split('，');
              const paramName = parts[0].replace('参数 ', '');
              const fromType = parts[1].replace('从 ', '').replace(' 到', '');
              const toType = parts[2].split('，')[0];
              const value = parts.length > 3 ? parts[3].replace('值: ', '') : '';
              
              formattedError += `<li>参数 <strong>${paramName}</strong>: 应为 <strong>${toType}</strong> 类型，实为 <strong>${fromType}</strong> 类型，需改正 ${value ? '(当前值: ' + value + ')' : ''}</li>`;
            } 
            // 处理缺少参数的错误
            else if (err.includes('缺少必需参数')) {
              const paramName = err.replace('缺少必需参数 ', '');
              formattedError += `<li>缺少必需参数 <strong>${paramName}</strong>，请提供该参数</li>`;
            }
            // 其他错误
            else {
              formattedError += `<li>${err}</li>`;
            }
          });
          formattedError += '</ul></div>';
          
          Message.error({
            content: formattedError,
            duration: 8000,
            dangerouslyUseHTMLString: true
          });
        } 
        // 处理类型转换错误
        else if (res.message && (res.message.includes('类型错误') || res.message.includes('转换类型失败'))) {
          // 尝试解析错误信息，提取类型信息
          const errorMsg = res.message;
          let formattedError = '<div style="text-align:left"><strong>参数校验错误:</strong><ul style="padding-left:20px;margin-top:5px">';
          
          // 尝试匹配类型转换错误格式
          if (errorMsg.includes('从') && errorMsg.includes('到')) {
            const parts = errorMsg.split('，');
            const paramName = parts[0].includes('参数') ? parts[0].replace('参数 ', '') : '未知参数';
            const fromType = parts.find(p => p.includes('从'))?.replace('从 ', '').replace(' 到', '') || '未知类型';
            const toType = parts.find(p => p.includes('到'))?.split(' ')[1] || '未知类型';
            const value = parts.find(p => p.includes('值:'))?.replace('值: ', '') || '';
            
            formattedError += `<li>参数 <strong>${paramName}</strong>: 应为 <strong>${toType}</strong> 类型，实为 <strong>${fromType}</strong> 类型，需改正 ${value ? '(当前值: ' + value + ')' : ''}</li>`;
          } else {
            formattedError += `<li>${errorMsg}</li>`;
          }
          
          formattedError += '</ul></div>';
          
          Message.error({
            content: formattedError,
            duration: 5000,
            dangerouslyUseHTMLString: true
          });
        } 
        // 其他错误
        else {
          Message.error('脚本执行失败: ' + res.message);
        }
      }
    })
    .catch(err => {
      console.error(err);
      // 显示更明确的错误信息
      const errorMessage = '参数校验错误: 类型不匹配，请检查参数类型';
      Message.error({
        content: errorMessage,
        duration: 5000
      });
      script_result.value = { status: false, message: errorMessage };
    })
    .finally(() => {
      loading.value = false;
    });
}

// 运行脚本
function handleRunScript() {
  executeScript(false);
}

// 格式化脚本数据
function formatScriptData(data) {
  // todo 优化显示
  return JSON.stringify(data, null);
}

// 刷新脚本信息
function refreshScriptInfo() {
  if (!props.script_url) return [];
  getScriptCurrentVersion({script_url: props.script_url}).then(res => {
    origin_version_info.value = res["version_info"];
    script_info.value = Object.keys(res["version_info"]).map(key => {
      return {label: key, value: formatScriptData(res["version_info"][key])};
    });
  }).catch(err => {
    console.log(err);
  });
}

// 监听script_url的变化，触发刷新
watch(() => props.script_url, refreshScriptInfo);
onMounted(() => {
  refreshScriptInfo();
})
</script>

<template>
  <div class="description">
    <a-descriptions :data="script_info" title="Script Info" layout="vertical" :column="1"/>
    <a-divider/>
    <a-space>
      <a-button @click="showScriptDrawer">选择版本</a-button>
      <a-button type="primary" @click="showRunScriptModal">运行脚本</a-button>
    </a-space>
    
    <!-- 运行脚本对话框 -->
    <a-modal
      v-model:visible="run_modal_visible"
      title="运行脚本"
      :mask-closable="false"
      :unmount-on-close="true"
      :footer="false"
      width="700px">
      <a-spin :loading="loading">
        <a-form :model="script_parameters" layout="vertical">
          <a-form-item label="脚本路径">
            <a-input disabled :model-value="props.script_url" />
          </a-form-item>
          
          <a-divider>参数设置</a-divider>
          
          <!-- 动态参数输入 -->
          <template v-if="origin_version_info.input && origin_version_info.input.length > 0">
            <a-form-item 
              v-for="param in origin_version_info.input" 
              :key="typeof param === 'object' ? param.name : param" 
              :label="typeof param === 'object' ? param.name : param">
              <a-input 
                v-model="script_parameters[typeof param === 'object' ? param.name : param]" 
                :placeholder="`请输入参数 ${typeof param === 'object' ? param.name : param}${typeof param === 'object' && param.type ? ' (类型: ' + param.type + ')' : ''}`" />
              <template v-if="typeof param === 'object' && param.default && param.default !== 'null' && param.default !== 'NotNone'">
                <div class="param-default">默认值: {{ param.default }}</div>
              </template>
            </a-form-item>
          </template>
          <a-empty v-else description="该脚本无需参数" />
          
          <a-divider v-if="script_result">执行结果</a-divider>
          
          <!-- 结果展示 -->
          <template v-if="script_result">
            <a-alert :type="script_result.status ? 'success' : 'error'" banner>
              {{ script_result.message }}
            </a-alert>
            <a-card v-if="script_result.status && script_result.result" title="返回数据" style="margin-top: 16px;">
              <pre>{{ JSON.stringify(script_result.result, null, 2) }}</pre>
            </a-card>
          </template>
          
          <div style="margin-top: 24px; text-align: right;">
            <a-space>
              <a-button @click="run_modal_visible = false">关闭</a-button>
              <a-button type="primary" :loading="loading" @click="handleRunScript">执行</a-button>
            </a-space>
          </div>
        </a-form>
      </a-spin>
    </a-modal>

    <!-- 参数转换确认对话框 -->
    <a-modal
      v-model:visible="show_conversion_modal"
      title="参数类型转换确认"
      :mask-closable="false"
      :unmount-on-close="true"
      @cancel="show_conversion_modal = false"
      width="700px">
      <div>
        <a-alert type="warning" banner>
          以下参数需要进行类型转换才能执行脚本，请确认是否继续执行
        </a-alert>
        
        <a-table 
          :columns="[
            { title: '参数名', dataIndex: 'param_name' },
            { title: '原类型', dataIndex: 'from_type' },
            { title: '目标类型', dataIndex: 'to_type' },
            { title: '原始值', dataIndex: 'original_value' },
            { title: '转换后值', dataIndex: 'converted_value' }
          ]" 
          :data="conversion_info"
          :pagination="false"
          style="margin-top: 16px;">
        </a-table>
      </div>
      
      <template #footer>
        <a-space>
          <a-button @click="show_conversion_modal = false">取消</a-button>
          <a-button type="primary" @click="confirmAndRunScript">确认并执行</a-button>
        </a-space>
      </template>
    </a-modal>
  </div>
  <ScriptDrawer
      :title="'选择脚本版本'"
      :current="origin_version_info"
      :versions_info="script_versions_info"
      v-if="drawer_visible"
      v-model="drawer_visible"/>
</template>

<style scoped>
.description {
  margin: 20px 20px 20px 40px;
  justify-content: center;
  max-width: 80%;
}

.param-default {
  font-size: 12px;
  color: #666;
  margin-top: 4px;
  font-style: italic;
}
</style>
