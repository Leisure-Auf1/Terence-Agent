const p = require("puppeteer");
const U = "http://127.0.0.1:9222";
function s(m){return new Promise(r=>setTimeout(r,m))}

(async()=>{
  const b=await p.connect({browserURL:U});
  const [pg]=await b.pages();
  
  // 点击"教程目录"标签 - 看完整课程结构
  await pg.evaluate(()=>{
    const tabs = document.querySelectorAll('.ant-tabs-tab');
    for(const tab of tabs){
      if(tab.innerText.trim()==='教程目录' && tab.offsetParent!==null){
        const keys=Object.keys(tab);const pk=keys.find(k=>k.startsWith('__reactProps'));
        if(pk&&tab[pk]?.onClick)tab[pk].onClick({preventDefault(){},stopPropagation(){}});
        tab.click();
        return;
      }
    }
    console.log("未找到教程目录tab");
  });
  await s(5000);
  
  // 获取目录结构
  const catalog = await pg.evaluate(()=>document.body.innerText.substring(0,4000));
  console.log("=== 完整教程目录 ===");
  console.log(catalog);
  
  await b.disconnect();
})().catch(e=>console.error("❌",e.message));
