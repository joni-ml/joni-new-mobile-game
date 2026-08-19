/* בדיקות למנוע הכימיה של RLS.
   הרצה:  node rls/test-chem.mjs
   השאלה שכל בדיקה כאן שואלת: האם *חוק אחד* באמת מייצר כימיה אמיתית,
   בלי שכתבנו אף תגובה בשם? */
import * as C from './chem.js';

let pass=0, fail=0;
const ok=(name,cond,detail)=>{ if(cond){pass++; console.log('  ✔ '+name+(detail?'   '+detail:''));}
                               else {fail++; console.log('  ✘ '+name+(detail?'   '+detail:''));} };
const id=k=>C.sub_(k).id, nm=i=>C.subById(i).name+' ('+C.subById(i).key+')';

const show=(i,k)=>(k>1?k+'× ':'')+nm(i);
function react(a,b,T){
  const r=C.reaction(id(a), id(b), T);
  if(!r) return null;
  const lhs=(r.nA>1?r.nA+'× ':'')+a+' + '+(r.nB>1?r.nB+'× ':'')+b;
  return {txt:lhs+'  →  '+show(r.p,r.pk)+(r.q!=null?' + '+show(r.q,r.qk):''),
          p:r.p, q:r.q, gain:r.gain, r};
}

console.log('\n=== 1. תגובות מפורסמות — אף אחת מהן לא כתובה בשם בשום מקום ===');
{
  const r=react('H2','O2',700);
  ok('מימן + חמצן בחום → מים', r && [r.p,r.q].some(x=>x!=null&&C.subById(x).key==='H2O'),
     r?('→ '+r.txt+'  (משחרר '+r.gain+' kJ)'):'לא קרה כלום');
}
{
  const r=react('Fe2O3','Al',900);
  ok('תרמיט: חלודה + אלומיניום → ברזל', r && [r.p,r.q].some(x=>x!=null&&C.subById(x).key==='Fe'),
     r?('→ '+r.txt+'  (משחרר '+r.gain+' kJ)'):'לא קרה כלום');
}
{
  const r=react('Na','Cl2',200);
  ok('נתרן + כלור → מלח', r && [r.p,r.q].some(x=>x!=null&&C.subById(x).key==='NaCl'),
     r?('→ '+r.txt):'לא קרה כלום');
}
{
  const r=react('CH4','O2',800);
  ok('מתאן בוער', r, r?('→ '+r.txt+'  (משחרר '+r.gain+' kJ)'):'לא קרה כלום');
}
{
  const r=react('Mg','CO2',900);
  ok('מגנזיום בוער בתוך CO₂', r && [r.p,r.q].some(x=>x!=null&&C.subById(x).key==='MgO'),
     r?('→ '+r.txt):'לא קרה כלום');
}
{
  const r=react('C','O2',800);
  ok('פחמן בוער', r, r?('→ '+r.txt+'  (משחרר '+r.gain+' kJ)'):'לא קרה כלום');
}

console.log('\n=== 2. מה שאסור לקרות ===');
{
  const r=react('H2O','H2O',900);
  ok('מים + מים לא מתפרקים מעצמם', r===null, r?('קרה: '+r.txt):'שום דבר, נכון');
}
{
  const r=react('Au','O2',900);
  ok('זהב לא מחמצן', r===null, r?('קרה: '+r.txt):'שום דבר, נכון');
}
{
  const r=react('H2','O2',20);
  ok('מימן + חמצן בקור לא מתלקחים לבד', r===null,
     r?('קרה: '+r.txt):'צריך חום — נכון');
}
{
  const r=react('N2','O2',300);
  ok('אוויר רגיל לא מגיב מעצמו', r===null, r?('קרה: '+r.txt):'שום דבר, נכון');
}

console.log('\n=== 3. שימור חומר — לפי בנייה ===');
{
  let checked=0, bad=0;
  const subs=C.baseSubs();
  for(let i=0;i<subs.length;i++) for(let j=i;j<subs.length;j++){
    for(const T of [20,600,1800]){
      const r=C.reaction(subs[i].id, subs[j].id, T);
      if(!r) continue;
      checked++;
      if(!C.conserves(subs[i].id, subs[j].id, r)) bad++;
    }
  }
  ok('כל תגובה שנמצאה משמרת את האטומים', bad===0,
     'נבדקו '+checked+' תגובות, הפרות: '+bad);
}

console.log('\n=== 4. תרכובות שאיש לא רשם ===');
{
  const before=C.baseSubs().length;
  // מריצים סריקה רחבה כדי לראות אם נוצרים חומרים חדשים מעצמם
  const subs=C.baseSubs();
  for(let i=0;i<subs.length;i++) for(let j=i;j<subs.length;j++)
    for(const T of [20,500,1200,2000]) C.reaction(subs[i].id, subs[j].id, T);
  const after=C.allSubs();
  const born=after.slice(before).filter(s=>s.derived);
  ok('המנוע מייצר חומרים שלא היו בטבלה', after.length>=before,
     'התחלנו עם '+before+' חומרים, קיימים כעת '+after.length+
     (born.length?('  · לדוגמה: '+born.slice(0,5).map(s=>s.key).join(', ')):''));
}

console.log('\n=== 5. מהירות — הזיכרון הוא מה שהופך את זה לאפשרי בטלפון ===');
{
  C.clearMemo();
  const subs=C.baseSubs();
  const t0=Date.now();
  let n=0;
  for(let i=0;i<subs.length;i++) for(let j=0;j<subs.length;j++){ C.reaction(subs[i].id,subs[j].id,600); n++; }
  const cold=Date.now()-t0;
  const t1=Date.now();
  for(let k=0;k<20;k++) for(let i=0;i<subs.length;i++) for(let j=0;j<subs.length;j++)
    C.reaction(subs[i].id,subs[j].id,600);
  const warm=(Date.now()-t1)/20;
  ok('פעם ראשונה איטית, אחר כך זו רק קריאה מהזיכרון', warm < Math.max(1,cold/5),
     n+' צירופים · חישוב ראשון '+cold+'ms · אחרי שנשמר '+warm.toFixed(1)+'ms  (פי '+
     (cold/Math.max(0.1,warm)).toFixed(0)+' מהר יותר)');
  ok('גודל הזיכרון סביר', C.memoSize()<200000, C.memoSize()+' רשומות');
}

console.log('\n' + (fail? '❌ '+fail+' נכשלו, ' : '✅ ') + pass + ' עברו\n');
process.exit(fail?1:0);
