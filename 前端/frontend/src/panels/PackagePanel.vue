<script setup>
import PackageColumns from "@/components/PackageColumns.vue";
import PackageInstall from "@/components/PackageInstall.vue";
import {ref} from "vue";
import {getAllPackageInfo} from "@/api/package_api.js";

const installed_packages = ref([]);
const visible = ref(false);
// 显示安装包弹窗
function showInstallModal() {
  visible.value = true;
}
// 获取已安装包列表
function getInstalledPackages() {
  getAllPackageInfo().then(res => {
    installed_packages.value = res["package_list"];
  }).catch(err => {
    console.log(err);
  });
}

</script>


<template>
  <a-layout>
    <PackageInstall v-model="visible"/>
    <div>
      <a-button-group>
        <a-space>
          <a-button @click="getInstalledPackages">
            <icon-refresh/>
          </a-button>
          <a-button @click="showInstallModal">
              安装包
          </a-button>
        </a-space>
      </a-button-group>
    </div>
    <a-divider/>
    <PackageColumns :installed_packages="installed_packages" />
  </a-layout>
</template>

