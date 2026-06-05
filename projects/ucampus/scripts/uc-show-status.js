const p = require("puppeteer");
const U = "http://127.0.0.1:9222";
const C = "https://ucloud.unipus.cn/app/cmgt/resource-detail/20000975215";
function s(m){return new Promise(r=>setTimeout(r,m))}

(async()=>{
  const b=await p.connect({browserURL:U});
  const [pg]=await b.pages();

  // Step 1: 查看当前课程页面
  console.log("=== 🌟 第1步：当前页面状态 ===");
  console.log("URL:", await pg.evaluate(()=>window.location.href));
  console.log("Title:", await pg.evaluate(()=>document.title));

  // 等待课程树加载
  await s(3000);
  for(let i=0;i<20;i++){
    const n=await pg.evaluate(()=>document.querySelectorAll('[class*="taskItemInnerLayout"]').length);
    if(n>0)break;
    await s(1000);
  }

  // Step 2: 提取课程树 - 所有任务及其状态
  console.log("\n=== 🌟 第2步：课程完整进度树 ===");
  const tree = await pg.evaluate(()=>{
    const items=document.querySelectorAll('[class*="taskItemInnerLayout"]');
    const result=[];
    let currentSection='';
    for(const item of items){
      if(item.offsetParent===null)continue;
      const text=item.innerText.trim();
      // Section headers
      if(text==='Section A'||text==='Section B'||text==='Section C'){
        currentSection=text;
        continue;
      }
      const ne=item.querySelector('[class*="taskTypeName"]');
      const se=item.querySelector('[class*="nodePassStateTip"]');
      const name=ne?ne.innerText.trim():'?';
      const status=se?se.innerText.trim():'?';
      result.push({section:currentSection||'Top',name,status});
    }
    return result;
  });

  // 分组展示
  let current='';
  for(const t of tree){
    if(t.section!==current){
      console.log(`\n  📁 ${t.section}:`);
      current=t.section;
    }
    const icon=t.status==='已完成'?'✅':t.status==='未开始'?'⬜':t.status==='已锁定'?'🔒':'❓';
    console.log(`    ${icon} ${t.name.padEnd(30)} ${t.status}`);
  }

  // 统计
  const done=tree.filter(t=>t.status==='已完成').length;
  const pending=tree.filter(t=>t.status==='未开始').length;
  const locked=tree.filter(t=>t.status==='已锁定').length;
  const total=tree.length;
  console.log(`\n  ─────────────────────────────`);
  console.log(`  总计: ${total} | ✅ ${done} | ⬜ ${pending} | 🔒 ${locked}`);

  await b.disconnect();
})().catch(e=>console.error("❌",e.message));
