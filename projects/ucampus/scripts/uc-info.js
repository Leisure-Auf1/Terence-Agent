const p = require("puppeteer");
const U = "http://127.0.0.1:9222";
function s(m){return new Promise(r=>setTimeout(r,m))}

(async()=>{
  const b=await p.connect({browserURL:U});
  const [pg]=await b.pages();
  await pg.setViewport({width:1280,height:900});

  // 截取页面完整信息
  const info = await pg.evaluate(()=>{
    // 找单元标题
    const allH = document.querySelectorAll('h1,h2,h3,h4,h5,h6,[class*="title"],[class*="header"],[class*="heading"]');
    const headings = Array.from(allH).filter(h=>h.offsetParent!==null).map(h=>({tag:h.tagName,text:h.innerText.trim()}));

    // 检查是否有单元选择器
    const selectors = document.querySelectorAll('select, [class*="dropdown"], [class*="select"], [class*="picker"]');
    const selects = Array.from(selectors).filter(s=>s.offsetParent!==null).map(s=>({tag:s.tagName,text:s.innerText.trim()}));

    // 左边菜单/树 - 找单元切换
    const menuItems = document.querySelectorAll('[class*="menu-item"],[class*="MenuItem"],[data-menu-id]');
    const menus = Array.from(menuItems).filter(m=>m.offsetParent!==null).map(m=>m.innerText.trim());

    // 找侧边栏
    const sideText=document.querySelector('.ant-layout-sider')?.innerText?.substring(0,500)||'no sider';

    // 页面最显眼的标题
    const pageTitle = document.title;

    return {headings,selects,menus,sideText,pageTitle};
  });

  console.log("=== 页面结构 ===");
  console.log("Title:", info.pageTitle);
  console.log("\n-- 标题元素 --");
  info.headings.forEach(h=>console.log(`  ${h.tag}: ${h.text}`));
  console.log("\n-- 下拉/选择器 --");
  info.selects.forEach(s=>console.log(`  ${s.tag}: ${s.text}`));
  console.log("\n-- 侧边栏(前500字) --");
  console.log(info.sideText);

  await b.disconnect();
})().catch(e=>console.error("❌",e.message));
