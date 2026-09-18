<template>
  <el-container class="layout">
    <el-aside width="210px" class="aside">
      <div class="logo">知识库 Agent</div>
      <el-menu :default-active="$route.path" router class="menu">
        <el-menu-item index="/">
          <el-icon><ChatDotRound /></el-icon>
          <span>智能问答</span>
        </el-menu-item>
        <el-menu-item index="/docs">
          <el-icon><FolderOpened /></el-icon>
          <span>知识库管理</span>
        </el-menu-item>
      </el-menu>
      <div class="hint">RAG · LangChain · Milvus</div>
    </el-aside>
    <el-main class="main">
      <router-view />
    </el-main>
  </el-container>
</template>

<style scoped>
.layout {
  height: 100vh;
}
.aside {
  background: #fff;
  border-right: 1px solid #e4e3dd;
  display: flex;
  flex-direction: column;
}
.logo {
  font-size: 17px;
  font-weight: 700;
  color: #1a1b1c;
  padding: 20px 18px 12px;
}
.menu {
  border-right: none;
}
.hint {
  margin-top: auto;
  padding: 16px 18px;
  font-size: 11px;
  color: #9aa0aa;
}
.main {
  padding: 0;
  background: #f7f8fa;
  overflow: hidden;
}
</style>
