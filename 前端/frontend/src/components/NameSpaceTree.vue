<script setup>
import {ref, computed} from 'vue';
import {Message} from "@arco-design/web-vue";
import {IconPlus} from "@arco-design/web-vue/es/icon";

const searchKey = ref('');
const treeData = computed(() => {
  if (!searchKey.value) return originTreeData.value;
  return searchData(searchKey.value);
});

const selectedKey = defineModel({default: ""});
const props = defineProps({
  origin_data: Array,
});
const originTreeData = computed(() => {
  if (!props.origin_data.length) return [];
  return getFormatTree(props.origin_data)
})
const emits = defineEmits(["refresh", "key_selected"]);

const isCallable = (nodeData) => {
  return props.origin_data.includes(nodeData.key);
}

// 搜索数据的函数
function searchData(keyword) {
  const loop = (data) => {
    const result = [];
    data.forEach(item => {
      if (item.title.toLowerCase().indexOf(keyword.toLowerCase()) > -1) {
        result.push({...item});
      } else if (item.children) {
        const filterData = loop(item.children);
        if (filterData.length) {
          result.push({
            ...item,
            children: filterData
          })
        }
      }
    })
    return result;
  }
  return loop(originTreeData.value);
}

// 获取匹配索引的函数
function getMatchIndex(title) {
  if (!searchKey.value) return -1;
  return title.toLowerCase().indexOf(searchKey.value.toLowerCase());
}

// 图标点击事件处理函数
function onIconClick(nodeData) {
  const key = nodeData.key;
  emits("key_selected", key);
  Message.info({content: `You select ${key}`, showIcon: true});
}

// 树节点点击事件处理函数
function onTreeItemClick(selectedKeys) {
  const key = selectedKeys[0]
  if (props.origin_data.includes(key)) selectedKey.value = key;
  else selectedKey.value = "";
}

// 触发刷新事件的函数
function emitRefresh() {
  emits("refresh");
}

// 转换为树形结构的函数
function getFormatTree(data) {
  if (!data) return [];
  return data.reduce(
      (acc, item) => {
        const item_list = item.split("/")
        let cur = acc;
        let key = ""
        item_list.forEach((name, index) => {
          if (key) key += "/" + name;
          else key = name

          if (index === item_list.length - 1) {
            cur.push({title: name, key: key});
          } else {
            let pos = cur.findIndex(x => (x.title === name));
            if (pos < 0) {
              cur.push({title: name, key: key, children: []});
              pos = cur.length - 1;
            }
            cur = cur[pos].children;
          }
        });
        return acc;
      }, []);
}

</script>

<template>
  <div style="min-width: 20%">
    <div>
      <a-space>
        <a-button @click="emitRefresh">
          <icon-refresh/>
        </a-button>
        <a-input-search
            v-model="searchKey"
        />
      </a-space>
    </div>
    <a-tree
        :data="treeData"
        @select="onTreeItemClick"
        style="max-width: 240px">
      <template #title="nodeData">
        <template v-if="index = getMatchIndex(nodeData?.title), index < 0">{{ nodeData?.title }}</template>
        <span v-else>
          {{ nodeData?.title?.substr(0, index) }}
          <span style="color: var(--color-primary-light-4);">
            {{ nodeData?.title?.substr(index, searchKey.length) }}
          </span>{{ nodeData?.title?.substr(index + searchKey.length) }}
        </span>
      </template>
      <template #extra="nodeData">
        <icon-star-fill v-if="isCallable(nodeData)"/>
        <IconPlus
            style="position: absolute; right: 8px; font-size: 12px; top: 10px; color: #3370ff;"
            @click="() => onIconClick(nodeData)"
        />
      </template>
    </a-tree>
  </div>
</template>

<style scoped>

</style>

