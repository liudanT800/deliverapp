// 测试图标导入
try {
  const { ChevronForward, Add, List, Refresh, TrendingUp, TrendingDown, Cash } = await import('@vicons/ionicons5');
  console.log('✅ 图标导入成功:', {
    ChevronForward,
    Add,
    List,
    Refresh,
    TrendingUp,
    TrendingDown,
    Cash
  });
} catch (error) {
  console.error('❌ 图标导入失败:', error);
}
