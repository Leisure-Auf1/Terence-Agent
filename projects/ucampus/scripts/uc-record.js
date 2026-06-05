const p = require("puppeteer");
const U = "http://127.0.0.1:9222";
function s(m){return new Promise(r=>setTimeout(r,m))}

(async()=>{
  const b=await p.connect({browserURL:U});
  const [pg]=await b.pages();
  
  // 点击"学习记录"标签
  await pg.evaluate(()=>{
    const tabs = document.querySelectorAll('.ant-tabs-tab');
    for(const tab of tabs){
      if(tab.innerText.trim()==='学习记录' && tab.offsetParent!==null){
        const keys=Object.keys(tab);const pk=keys.find(k=>k.startsWith('__reactProps'));
        if(pk&&tab[pk]?.onClick)tab[pk].onClick({preventDefault(){},stopPropagation(){}});
        tab.click();return;
      }
    }
    console.log("未找到学习记录tab");
  });
  await s(6000);
  
  const record = await pg.evaluate(()=>{
    const body = document.body.innerText;
    // 找百分比、已学/总课时等信息
    const pctMatch = body.match(/(\\d+\\.?\\d*)%/g);
    const progressMatch = body.match(/已学[\s\S]*?\//g);
    const scoreMatch = body.match(/\\d+\\.?\\d*分/g);
    return {
      body: body.substring(0,3000),
      percentages: pctMatch || [],
      progresses: progressMatch || [],
      scores: scoreMatch || []
    };
  });
  
  console.log("=== 学习记录 ===");
  console.log(record.body);
  if(record.percentages.length>0) console.log("\n百分比:", record.percentages);
  if(record.scores.length>0) console.log("分数:", record.scores);
  
  await b.disconnect();
})().catch(e=>console.error("❌",e.message));
