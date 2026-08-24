/* ============================================================================
   RLS — מעבדה תלת-ממדית ליוניטי.  קובץ אחד. אין מה להרכיב.

   התקנה:
     1. גררו את RLSLab.cs לתוך Assets בפרויקט יוניטי.
     2. לחצו Play.

   זה הכל. הסקריפט בונה את החדר, השולחן, הכלים, השחקן, התאורה והממשק
   בעצמו בזמן ריצה. אין סצנה להכין, אין פריפאב לגרור, אין שכבות להגדיר.

   שליטה:
     WASD          הליכה          Shift  ריצה         רווח  קפיצה
     עכבר          מבט            E      הרמה/הנחה     Q     שפיכה
     גלגלת         עוצמת הלהבה (כשמסתכלים על המבער)
     1 2 3 4       בחירת חומר     F      מזיגה לכלי שמולך
     V             מצג אמיתי / מולקולות
     G             הצגת מולקולות האוויר
     Esc           שחרור העכבר    לחיצה  החזרת העכבר

   מה שיוניטי עושה כאן: השחקן, ההתנגשויות, הכלים שנופלים ומתגלגלים,
   התאורה והצללים. מה שהיא לא יודעת לעשות ולכן כתוב כאן במפורש: חום
   שעובר משכנה לשכנה, שינויי מצב צבירה עם חום כמוס, ציפה לפי הפרש
   צפיפות, אוויר שמקרר את הזכוכית, ומזיגה שנשפכת מכוח כובד.
   ============================================================================ */

using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Rendering;
#if ENABLE_INPUT_SYSTEM
using UnityEngine.InputSystem;
#endif

public class RLSLab : MonoBehaviour
{
    /* ======================================================================
       0)  אתחול אוטומטי
       ====================================================================== */
    static bool booted;

    [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
    static void Boot()
    {
        if (booted) return;
        /* אם מישהו כבר גרר את הסקריפט על אובייקט בסצנה, לא בונים פעמיים */
        if (FindObjectOfType<RLSLab>() != null) { booted = true; return; }
        booted = true;
        var go = new GameObject("RLS Lab");
        go.AddComponent<RLSLab>();
    }

    /* ======================================================================
       1)  קלט — עובד גם עם מנהל הקלט הישן וגם עם החדש
       ====================================================================== */
    static class In
    {
        public static float MoveX, MoveZ;
        public static Vector2 Look;
        public static float Scroll;
        public static bool Sprint, Jump, Use, Pour, Fill, Esc, Click;
        public static bool ToggleView, ToggleAir;
        public static int Digit;          /* 0 = לא נלחץ */
        public static float LookScale = 1f;

        public static void Poll()
        {
            MoveX = MoveZ = 0; Look = Vector2.zero; Scroll = 0; Digit = 0;
            Sprint = Jump = Use = Pour = Fill = Esc = Click = false;
            ToggleView = ToggleAir = false;

#if ENABLE_INPUT_SYSTEM
            var kb = Keyboard.current; var ms = Mouse.current;
            if (kb != null)
            {
                if (kb.dKey.isPressed) MoveX += 1;
                if (kb.aKey.isPressed) MoveX -= 1;
                if (kb.wKey.isPressed) MoveZ += 1;
                if (kb.sKey.isPressed) MoveZ -= 1;
                Sprint = kb.leftShiftKey.isPressed;
                Jump   = kb.spaceKey.wasPressedThisFrame;
                Use    = kb.eKey.wasPressedThisFrame;
                Pour   = kb.qKey.isPressed;
                Fill   = kb.fKey.wasPressedThisFrame;
                Esc    = kb.escapeKey.wasPressedThisFrame;
                ToggleView = kb.vKey.wasPressedThisFrame;
                ToggleAir  = kb.gKey.wasPressedThisFrame;
                if (kb.digit1Key.wasPressedThisFrame) Digit = 1;
                if (kb.digit2Key.wasPressedThisFrame) Digit = 2;
                if (kb.digit3Key.wasPressedThisFrame) Digit = 3;
                if (kb.digit4Key.wasPressedThisFrame) Digit = 4;
            }
            if (ms != null)
            {
                Look = ms.delta.ReadValue();
                Scroll = ms.scroll.ReadValue().y / 120f;
                Click = ms.leftButton.wasPressedThisFrame;
            }
            LookScale = 0.09f;         /* דלתא גולמית בפיקסלים */
#else
            MoveX = Input.GetAxisRaw("Horizontal");
            MoveZ = Input.GetAxisRaw("Vertical");
            Sprint = Input.GetKey(KeyCode.LeftShift);
            Jump   = Input.GetKeyDown(KeyCode.Space);
            Use    = Input.GetKeyDown(KeyCode.E);
            Pour   = Input.GetKey(KeyCode.Q);
            Fill   = Input.GetKeyDown(KeyCode.F);
            Esc    = Input.GetKeyDown(KeyCode.Escape);
            Click  = Input.GetMouseButtonDown(0);
            ToggleView = Input.GetKeyDown(KeyCode.V);
            ToggleAir  = Input.GetKeyDown(KeyCode.G);
            for (int d = 1; d <= 4; d++)
                if (Input.GetKeyDown(KeyCode.Alpha0 + d)) Digit = d;
            Look = new Vector2(Input.GetAxisRaw("Mouse X"), Input.GetAxisRaw("Mouse Y"));
            Scroll = Input.GetAxisRaw("Mouse ScrollWheel") * 10f;
            LookScale = 1.6f;          /* לציר הישן כבר יש רגישות משלו */
#endif
        }
    }

    /* ======================================================================
       2)  חומרים — עובד גם ב-URP וגם בצנרת המובנית
       ====================================================================== */
    static Shader litShader;

    static Shader Lit()
    {
        if (litShader != null) return litShader;
        /* פרויקט URP יצייר מג'נטה עם Standard, ולהפך. שואלים את יוניטי
           איזו צנרת פעילה במקום לנחש. */
        if (GraphicsSettings.currentRenderPipeline != null)
        {
            litShader = Shader.Find("Universal Render Pipeline/Lit");
            if (litShader == null) litShader = Shader.Find("HDRP/Lit");
        }
        if (litShader == null) litShader = Shader.Find("Standard");
        if (litShader == null) litShader = Shader.Find("Diffuse");
        return litShader;
    }

    static bool IsURP { get { return GraphicsSettings.currentRenderPipeline != null; } }

    static Material Mat(Color c, float smoothness = 0.35f, float metallic = 0f)
    {
        var m = new Material(Lit());
        m.SetColor(IsURP ? "_BaseColor" : "_Color", c);
        if (m.HasProperty("_Smoothness")) m.SetFloat("_Smoothness", smoothness);
        if (m.HasProperty("_Glossiness")) m.SetFloat("_Glossiness", smoothness);
        if (m.HasProperty("_Metallic")) m.SetFloat("_Metallic", metallic);
        m.enableInstancing = true;
        return m;
    }

    /* שקיפות היא המקום שבו שתי הצנרות הכי שונות זו מזו, ולכן היא כתובה
       כאן פעם אחת ובמפורש. בלי זה זכוכית יוצאת אטומה או ורודה. */
    static Material Glass(Color c, float smoothness = 0.95f)
    {
        var m = Mat(c, smoothness, 0f);
        if (IsURP)
        {
            m.SetFloat("_Surface", 1);            /* Transparent */
            m.SetFloat("_Blend", 0);              /* Alpha */
            m.SetFloat("_ZWrite", 0);
            m.SetFloat("_SrcBlend", (float)BlendMode.SrcAlpha);
            m.SetFloat("_DstBlend", (float)BlendMode.OneMinusSrcAlpha);
            m.EnableKeyword("_SURFACE_TYPE_TRANSPARENT");
            m.DisableKeyword("_ALPHATEST_ON");
            m.EnableKeyword("_ALPHAPREMULTIPLY_ON");
        }
        else
        {
            m.SetFloat("_Mode", 3);               /* Transparent */
            m.SetInt("_SrcBlend", (int)BlendMode.SrcAlpha);
            m.SetInt("_DstBlend", (int)BlendMode.OneMinusSrcAlpha);
            m.SetInt("_ZWrite", 0);
            m.DisableKeyword("_ALPHATEST_ON");
            m.EnableKeyword("_ALPHABLEND_ON");
            m.DisableKeyword("_ALPHAPREMULTIPLY_ON");
        }
        m.renderQueue = 3000;
        return m;
    }

    static Material mGlass, mWood, mSteel, mWhite, mFloor, mWall, mFlame, mLiquid;
    static Material[] mAtom;     /* לפי יסוד: O, H, N */

    /* ======================================================================
       3)  בניית רשתות — הכל נוצר בקוד, אין מודלים לייבא
       ====================================================================== */

    /* משטח סיבוב. profile הוא (רדיוס, גובה) בסדר יורד מהשפה למטה. */
    static void LatheInto(List<Vector3> V, List<Vector3> N, List<int> I,
                          Vector2[] p, int segs, bool flip)
    {
        int b = V.Count;
        for (int i = 0; i < p.Length; i++)
            for (int s = 0; s <= segs; s++)
            {
                float a = s / (float)segs * Mathf.PI * 2f;
                float ca = Mathf.Cos(a), sa = Mathf.Sin(a);
                V.Add(new Vector3(p[i].x * ca, p[i].y, p[i].x * sa));

                /* הנורמל ניצב למשיק הפרופיל. גוזרים אותו מהשכנים כדי
                   שהכיפות והצוואר יתחברו חלק ולא בפאות. */
                Vector2 t = (p[Mathf.Min(i + 1, p.Length - 1)] - p[Mathf.Max(i - 1, 0)]);
                if (t.sqrMagnitude < 1e-12f) t = new Vector2(0, 1);
                t.Normalize();
                Vector2 nr = new Vector2(t.y, -t.x);
                var n = new Vector3(nr.x * ca, nr.y, nr.x * sa).normalized;
                N.Add(flip ? -n : n);
            }
        for (int i = 0; i < p.Length - 1; i++)
            for (int s = 0; s < segs; s++)
            {
                int a = b + i * (segs + 1) + s, c = a + segs + 1;
                if (flip) { I.Add(a); I.Add(a + 1); I.Add(c); I.Add(a + 1); I.Add(c + 1); I.Add(c); }
                else { I.Add(a); I.Add(c); I.Add(a + 1); I.Add(a + 1); I.Add(c); I.Add(c + 1); }
            }
    }

    static Mesh Lathe(Vector2[] p, int segs = 40, bool flip = false)
    {
        var V = new List<Vector3>(); var N = new List<Vector3>(); var I = new List<int>();
        LatheInto(V, N, I, p, segs, flip);
        return Finish(V, N, I);
    }

    /* זכוכית חלולה: קליפה חיצונית, קליפה פנימית הפוכה, וטבעת שפה
       שסוגרת ביניהן. בלי השפה רואים את עובי הדופן כחור. */
    static Mesh HollowLathe(Vector2[] outer, float t, int segs = 40)
    {
        var inner = new Vector2[outer.Length];
        for (int i = 0; i < outer.Length; i++)
        {
            Vector2 tan = (outer[Mathf.Min(i + 1, outer.Length - 1)] - outer[Mathf.Max(i - 1, 0)]);
            if (tan.sqrMagnitude < 1e-12f) tan = new Vector2(0, 1);
            tan.Normalize();
            Vector2 nr = new Vector2(tan.y, -tan.x);
            inner[i] = new Vector2(Mathf.Max(0.0004f, outer[i].x - nr.x * t), outer[i].y - nr.y * t);
        }
        var V = new List<Vector3>(); var N = new List<Vector3>(); var I = new List<int>();
        LatheInto(V, N, I, outer, segs, false);
        LatheInto(V, N, I, inner, segs, true);
        LatheInto(V, N, I, new[] { outer[0], inner[0] }, segs, false);
        return Finish(V, N, I);
    }

    static Mesh Finish(List<Vector3> V, List<Vector3> N, List<int> I)
    {
        var m = new Mesh();
        if (V.Count > 65000) m.indexFormat = IndexFormat.UInt32;
        m.SetVertices(V); m.SetNormals(N); m.SetTriangles(I, 0);
        m.RecalculateBounds();
        return m;
    }

    /* כדור בעל מעט פאות. מצוירים ממנו עשרות אלפי עותקים, ולכן כל
       משולש מיותר עולה. */
    static Mesh sphereMesh;
    static Mesh Sphere()
    {
        if (sphereMesh != null) return sphereMesh;
        int rings = 8, segs = 12;
        var V = new List<Vector3>(); var N = new List<Vector3>(); var I = new List<int>();
        for (int r = 0; r <= rings; r++)
        {
            float phi = r / (float)rings * Mathf.PI;
            for (int s = 0; s <= segs; s++)
            {
                float th = s / (float)segs * Mathf.PI * 2f;
                var v = new Vector3(Mathf.Sin(phi) * Mathf.Cos(th), Mathf.Cos(phi), Mathf.Sin(phi) * Mathf.Sin(th));
                V.Add(v * 0.5f); N.Add(v);
            }
        }
        for (int r = 0; r < rings; r++)
            for (int s = 0; s < segs; s++)
            {
                int a = r * (segs + 1) + s, c = a + segs + 1;
                I.Add(a); I.Add(c); I.Add(a + 1);
                I.Add(a + 1); I.Add(c); I.Add(c + 1);
            }
        sphereMesh = Finish(V, N, I);
        return sphereMesh;
    }

    static GameObject Box(string name, Vector3 size, Material mat, Transform parent,
                          Vector3 pos, bool collide = true)
    {
        var go = GameObject.CreatePrimitive(PrimitiveType.Cube);
        go.name = name;
        go.transform.SetParent(parent, false);
        go.transform.localPosition = pos;
        go.transform.localScale = size;
        go.GetComponent<MeshRenderer>().sharedMaterial = mat;
        if (!collide) Destroy(go.GetComponent<Collider>());
        return go;
    }

    static GameObject Cyl(string name, float r, float h, Material mat, Transform parent,
                          Vector3 pos, bool collide = true)
    {
        var go = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
        go.name = name;
        go.transform.SetParent(parent, false);
        go.transform.localPosition = pos;
        go.transform.localScale = new Vector3(r * 2f, h * 0.5f, r * 2f);
        go.GetComponent<MeshRenderer>().sharedMaterial = mat;
        if (!collide) Destroy(go.GetComponent<Collider>());
        return go;
    }

    /* ======================================================================
       4)  כלים
       ====================================================================== */

    /* הפרופיל הפנימי הוא מה שהחומר מרגיש. הוא נשמר בנפרד מהרשת המצוירת,
       כי הכליאה חייבת להיות מדויקת גם כשהכלי מוטה או נופל. */
    public class Vessel
    {
        public string name;
        public Transform tr;
        public Rigidbody rb;
        public float[] py, pr;     /* גובה מקומי, רדיוס פנימי */
        public float rimY;         /* גובה השפה, מקומי */
        public float mouthR;
        public float[] cumVol;     /* נפח מצטבר עד כל גובה — למפלס הנוזל */
        public float wallT = 20f;  /* טמפרטורת הזכוכית */
        public int held = 0;
        public Transform liquidTr; /* רשת הנוזל במצג האמיתי */
        public MeshFilter liquidMF;
        public MeshRenderer liquidMR;
        public int count;          /* כמה חלקיקים בפנים — לתצוגה */
        public float lastFill = -1f;
        public float meanT = 20f;

        public float InnerR(float y)
        {
            if (y <= py[0]) return pr[0];
            if (y >= py[py.Length - 1]) return pr[pr.Length - 1];
            for (int i = 1; i < py.Length; i++)
                if (y <= py[i])
                {
                    float u = (y - py[i - 1]) / Mathf.Max(1e-6f, py[i] - py[i - 1]);
                    return Mathf.Lerp(pr[i - 1], pr[i], u);
                }
            return pr[pr.Length - 1];
        }

        public void BuildVolumeTable()
        {
            cumVol = new float[py.Length];
            cumVol[0] = 0;
            for (int i = 1; i < py.Length; i++)
            {
                float h = py[i] - py[i - 1];
                float a = pr[i - 1], b = pr[i];
                /* נפח קטע חרוט קטום — מדויק יותר מגליל, וזה חשוב בבקבוק
                   הכדורי שבו הרדיוס משתנה מהר */
                cumVol[i] = cumVol[i - 1] + Mathf.PI * h * (a * a + a * b + b * b) / 3f;
            }
        }

        public float FillHeight(float volume)
        {
            if (cumVol == null || volume <= 0) return py[0];
            for (int i = 1; i < cumVol.Length; i++)
                if (volume <= cumVol[i])
                {
                    float u = (volume - cumVol[i - 1]) / Mathf.Max(1e-9f, cumVol[i] - cumVol[i - 1]);
                    return Mathf.Lerp(py[i - 1], py[i], u);
                }
            return py[py.Length - 1];
        }
    }

    readonly List<Vessel> vessels = new List<Vessel>();

    Vessel MakeVessel(string name, Vector2[] outerProfile, float[] innerY, float[] innerR,
                      float wallThick, Vector3 worldPos, float mass)
    {
        var go = new GameObject(name);
        go.transform.position = worldPos;

        var mesh = HollowLathe(outerProfile, wallThick, 36);
        var vis = new GameObject("glass");
        vis.transform.SetParent(go.transform, false);
        vis.AddComponent<MeshFilter>().sharedMesh = mesh;
        var mr = vis.AddComponent<MeshRenderer>();
        mr.sharedMaterial = mGlass;

        /* המתנגש הוא הקמור של הצורה החיצונית. לכליאת החומר משתמשים
           בפרופיל הפנימי ולא בו, ולכן הקירוב הזה לא פוגע בכלום. */
        var mc = go.AddComponent<MeshCollider>();
        mc.sharedMesh = Lathe(outerProfile, 20);
        mc.convex = true;

        var rb = go.AddComponent<Rigidbody>();
        rb.mass = mass;
        rb.collisionDetectionMode = CollisionDetectionMode.ContinuousDynamic;
        rb.interpolation = RigidbodyInterpolation.Interpolate;

        var v = new Vessel
        {
            name = name,
            tr = go.transform,
            rb = rb,
            py = innerY,
            pr = innerR,
            rimY = innerY[innerY.Length - 1],
            mouthR = innerR[innerR.Length - 1],
        };
        v.BuildVolumeTable();

        /* רשת הנוזל. נבנית מחדש כשהמפלס משתנה. */
        var lq = new GameObject("liquid");
        lq.transform.SetParent(go.transform, false);
        v.liquidMF = lq.AddComponent<MeshFilter>();
        v.liquidMR = lq.AddComponent<MeshRenderer>();
        v.liquidMR.sharedMaterial = mLiquid;
        v.liquidTr = lq.transform;

        vessels.Add(v);
        return v;
    }

    /* ---- הפרופילים. הכל במטרים, בגודל אמיתי של כלי מעבדה. ---- */

    Vessel MakeBeaker(Vector3 pos)      /* כוס 400 מ״ל */
    {
        float r = 0.043f, h = 0.115f;
        var outer = new[]{ new Vector2(r,h), new Vector2(r,0.006f),
                           new Vector2(r*0.94f,0.0015f), new Vector2(r*0.8f,0f), new Vector2(0,0f) };
        var iy = new[] { 0.004f, 0.010f, h };
        var ir = new[] { r * 0.72f, r - 0.002f, r - 0.002f };
        return MakeVessel("Beaker", outer, iy, ir, 0.0022f, pos, 0.20f);
    }

    Vessel MakeFlask(Vector3 pos)       /* בקבוק כדורי 500 מ״ל עם צוואר */
    {
        float R = 0.048f, cy = 0.052f, neck = 0.0125f, top = 0.155f;
        var pts = new List<Vector2>();
        pts.Add(new Vector2(neck, top));
        pts.Add(new Vector2(neck, 0.108f));
        pts.Add(new Vector2(neck * 1.5f, 0.098f));
        pts.Add(new Vector2(R * 0.62f, 0.086f));
        for (float a = 0.72f; a <= Mathf.PI + 1e-4f; a += (Mathf.PI - 0.72f) / 16f)
            pts.Add(new Vector2(R * Mathf.Sin(a), cy + R * Mathf.Cos(a)));
        var outer = pts.ToArray();

        var iy = new List<float>(); var ir = new List<float>();
        for (float y = 0.004f; y <= top; y += 0.004f)
        {
            float rr;
            if (y >= 0.108f) rr = neck - 0.0015f;
            else if (y <= 0.086f)
            {
                float d = y - cy;
                rr = Mathf.Sqrt(Mathf.Max(0, R * R - d * d)) - 0.0018f;
            }
            else
            {
                float u = (y - 0.086f) / 0.022f;
                rr = Mathf.Lerp(R * 0.62f, neck, u) - 0.0015f;
            }
            iy.Add(y); ir.Add(Mathf.Max(0.001f, rr));
        }
        return MakeVessel("Flask", outer, iy.ToArray(), ir.ToArray(), 0.0018f, pos, 0.24f);
    }

    Vessel MakeTube(Vector3 pos)        /* מבחנה */
    {
        float r = 0.0085f, h = 0.15f;
        var pts = new List<Vector2>();
        pts.Add(new Vector2(r, h));
        pts.Add(new Vector2(r, r));
        for (float a = 0f; a <= Mathf.PI / 2f + 1e-4f; a += Mathf.PI / 16f)
            pts.Add(new Vector2(r * Mathf.Cos(a), r - r * Mathf.Sin(a)));
        var iy = new[] { 0.002f, r, h };
        var ir = new[] { r * 0.55f, r - 0.0012f, r - 0.0012f };
        return MakeVessel("TestTube", pts.ToArray(), iy, ir, 0.0012f, pos, 0.04f);
    }

    Vessel MakeErlen(Vector3 pos)       /* ארלנמאייר */
    {
        float baseR = 0.045f, neck = 0.013f, h = 0.135f;
        var outer = new[]{ new Vector2(neck,h), new Vector2(neck,0.095f),
                           new Vector2(baseR*0.55f,0.075f), new Vector2(baseR,0.016f),
                           new Vector2(baseR,0.002f), new Vector2(baseR*0.85f,0f), new Vector2(0,0f) };
        var iy = new[] { 0.003f, 0.016f, 0.075f, 0.095f, h };
        var ir = new[] { baseR * 0.8f, baseR - 0.002f, baseR * 0.55f - 0.002f, neck - 0.0015f, neck - 0.0015f };
        return MakeVessel("Erlenmeyer", outer, iy, ir, 0.0018f, pos, 0.22f);
    }

    /* ======================================================================
       5)  חומרים כימיים
       ====================================================================== */
    class Species
    {
        public string key, label;
        public float boil, melt;       /* מעלות צלזיוס */
        public float liqRho, gasRho;   /* יחסי, מים = 1 */
        public float latent;           /* חום כמוס, בשווה-ערך מעלות */
        public Color tint;
        public int[] atoms;            /* אינדקס יסוד לכל אטום במודל */
        public Vector3[] offs;         /* מיקום האטום במולקולה */
    }

    const int EL_O = 0, EL_H = 1, EL_N = 2;
    static readonly Color[] elCol = {
        new Color(0.91f,0.26f,0.21f),      /* חמצן */
        new Color(0.95f,0.95f,0.97f),      /* מימן */
        new Color(0.24f,0.45f,0.92f),      /* חנקן */
    };
    static readonly float[] elR = { 0.0021f, 0.0014f, 0.0020f };

    Species[] SP;

    void BuildSpecies()
    {
        float d = 0.0026f;   /* אורך הקשר במודל המצויר */
        SP = new[]
        {
            new Species{ key="H2O", label="Water  H2O", boil=100f, melt=0f,
                liqRho=1.00f, gasRho=0.0006f, latent=540f,
                tint=new Color(0.55f,0.75f,0.95f,0.55f),
                atoms=new[]{EL_O,EL_H,EL_H},
                offs=new[]{ Vector3.zero,
                            new Vector3( 0.76f*d, 0.59f*d, 0),
                            new Vector3(-0.76f*d, 0.59f*d, 0)} },

            new Species{ key="O2", label="Oxygen  O2", boil=-183f, melt=-219f,
                liqRho=1.14f, gasRho=0.00133f, latent=232f,
                tint=new Color(0.85f,0.45f,0.40f,0.40f),
                atoms=new[]{EL_O,EL_O},
                offs=new[]{ new Vector3(-0.5f*d,0,0), new Vector3(0.5f*d,0,0)} },

            new Species{ key="H2", label="Hydrogen  H2", boil=-253f, melt=-259f,
                liqRho=0.071f, gasRho=0.00008f, latent=31f,
                tint=new Color(0.9f,0.9f,0.95f,0.30f),
                atoms=new[]{EL_H,EL_H},
                offs=new[]{ new Vector3(-0.38f*d,0,0), new Vector3(0.38f*d,0,0)} },

            new Species{ key="N2", label="Nitrogen  N2", boil=-196f, melt=-210f,
                liqRho=0.807f, gasRho=0.00116f, latent=191f,
                tint=new Color(0.5f,0.6f,0.9f,0.35f),
                atoms=new[]{EL_N,EL_N},
                offs=new[]{ new Vector3(-0.5f*d,0,0), new Vector3(0.5f*d,0,0)} },
        };
    }

    /* ======================================================================
       6)  החלקיקים
       ====================================================================== */
    const int MAXP = 9000;
    const float R0 = 0.0042f;             /* מרווח אריזה, מטר */
    const float RANGE = R0 * 1.7f;
    const float AMBIENT = 20f;
    const int GAS = 0, LIQ = 1, SOL = 2;

    /* המודל המצויר קטן מהמרווח, ולכן רואים רווח בין מולקולות בנוזל,
       רווח גדול בגז וכמעט כלום במוצק — כמו במציאות. */
    static readonly float[] MODEL = { 0.42f, 0.62f, 0.88f };
    static readonly float[] COND = { 0.20f, 1.0f, 1.35f };   /* מוליכות לפי מצב */

    Vector3[] px = new Vector3[MAXP], pv = new Vector3[MAXP];
    float[] pT = new float[MAXP], pCool = new float[MAXP], pRho = new float[MAXP], pAround = new float[MAXP];
    float[] pWet = new float[MAXP];
    byte[] pSp = new byte[MAXP], pPhase = new byte[MAXP];
    bool[] pAir = new bool[MAXP];
    int[] pVes = new int[MAXP];           /* -1 = חופשי באוויר */
    int nP = 0;

    void Spawn(int sp, Vector3 pos, int vessel, bool air = false)
    {
        if (nP >= MAXP) return;
        int i = nP++;
        px[i] = pos;
        pv[i] = new Vector3(Random.Range(-.02f, .02f), Random.Range(-.02f, .02f), Random.Range(-.02f, .02f));
        pT[i] = AMBIENT; pSp[i] = (byte)sp; pPhase[i] = LIQ; pVes[i] = vessel;
        pAir[i] = air; pCool[i] = 0; pAround[i] = 0; pWet[i] = 0;
        if (air) pPhase[i] = GAS;
    }

    void Kill(int i)
    {
        int j = --nP;
        if (i != j)
        {
            px[i] = px[j]; pv[i] = pv[j]; pT[i] = pT[j]; pSp[i] = pSp[j];
            pPhase[i] = pPhase[j]; pVes[i] = pVes[j]; pAir[i] = pAir[j];
            pCool[i] = pCool[j]; pRho[i] = pRho[j]; pAround[i] = pAround[j]; pWet[i] = pWet[j];
        }
    }

    float DensityOf(int i)
    {
        var s = SP[pSp[i]];
        /* צפיפות גז תלויה בטמפרטורה. בלי זה אדים חמים לא עולים. */
        return pPhase[i] == GAS
            ? s.gasRho * 293f / Mathf.Max(pT[i] + 273.15f, 60f)
            : s.liqRho;
    }

    /* ---- רשת מרחבית שטוחה, מיון־ספירה ---- */
    int GNX = 1, GNY = 1, GNZ = 1;
    Vector3 gridMin;
    int[] cellStart = new int[1], cellCur = new int[1], cellOf = new int[MAXP], order = new int[MAXP];
    int[] pairs = new int[1 << 18];
    int nPairs = 0;

    void BuildPairs()
    {
        if (nP == 0) { nPairs = 0; return; }
        Vector3 lo = px[0], hi = px[0];
        for (int i = 1; i < nP; i++)
        {
            lo = Vector3.Min(lo, px[i]); hi = Vector3.Max(hi, px[i]);
        }
        gridMin = lo - Vector3.one * RANGE;
        Vector3 span = (hi - lo) + Vector3.one * RANGE * 3f;
        GNX = Mathf.Clamp(Mathf.CeilToInt(span.x / RANGE), 1, 220);
        GNY = Mathf.Clamp(Mathf.CeilToInt(span.y / RANGE), 1, 220);
        GNZ = Mathf.Clamp(Mathf.CeilToInt(span.z / RANGE), 1, 220);
        int nc = GNX * GNY * GNZ;
        if (cellStart.Length < nc + 1) { cellStart = new int[nc + 1]; cellCur = new int[nc + 1]; }
        else System.Array.Clear(cellStart, 0, nc + 1);

        for (int i = 0; i < nP; i++)
        {
            pRho[i] = 0; pAround[i] = 0; pWet[i] = 0;
            var d = px[i] - gridMin;
            int cx = Mathf.Clamp((int)(d.x / RANGE), 0, GNX - 1);
            int cy = Mathf.Clamp((int)(d.y / RANGE), 0, GNY - 1);
            int cz = Mathf.Clamp((int)(d.z / RANGE), 0, GNZ - 1);
            int c = (cz * GNY + cy) * GNX + cx;
            cellOf[i] = c; cellStart[c + 1]++;
        }
        for (int c = 0; c < nc; c++) cellStart[c + 1] += cellStart[c];
        System.Array.Copy(cellStart, cellCur, nc);
        for (int i = 0; i < nP; i++) order[cellCur[cellOf[i]]++] = i;

        nPairs = 0;
        float r2 = RANGE * RANGE;
        for (int i = 0; i < nP; i++)
        {
            int c = cellOf[i];
            int cx = c % GNX, cy = (c / GNX) % GNY, cz = c / (GNX * GNY);
            Vector3 xi = px[i];
            for (int dz = -1; dz <= 1; dz++)
            {
                int z = cz + dz; if (z < 0 || z >= GNZ) continue;
                for (int dy = -1; dy <= 1; dy++)
                {
                    int y = cy + dy; if (y < 0 || y >= GNY) continue;
                    int row = (z * GNY + y) * GNX;
                    int lo2 = cx > 0 ? cx - 1 : 0, hi2 = cx < GNX - 1 ? cx + 1 : GNX - 1;
                    int q0 = cellStart[row + lo2], q1 = cellStart[row + hi2 + 1];
                    for (int q = q0; q < q1; q++)
                    {
                        int j = order[q];
                        if (j <= i) continue;
                        if ((xi - px[j]).sqrMagnitude > r2) continue;
                        if (nPairs * 2 + 2 > pairs.Length)
                        {
                            var g = new int[pairs.Length * 2];
                            System.Array.Copy(pairs, g, pairs.Length); pairs = g;
                        }
                        pairs[nPairs * 2] = i; pairs[nPairs * 2 + 1] = j; nPairs++;
                    }
                }
            }
        }
    }

    Vector3[] prevPos = new Vector3[MAXP];

    void Separate()
    {
        for (int k = 0; k < nPairs; k++)
        {
            int i = pairs[k * 2], j = pairs[k * 2 + 1];
            Vector3 e = px[i] - px[j];
            float d = e.magnitude;
            Vector3 u;
            if (d < 1e-7f)
            {
                u = new Vector3(Random.value - .5f, Random.value - .5f, Random.value - .5f).normalized;
                d = 0;
            }
            else if (d < R0) u = e / d;
            else continue;
            float push = (R0 - d) * 0.5f;
            px[i] += u * push; px[j] -= u * push;
            float rel = Vector3.Dot(pv[i] - pv[j], u) * 0.16f;
            pv[i] -= u * rel; pv[j] += u * rel;
        }
    }

    /* ======================================================================
       7)  צעד הפיזיקה
       ====================================================================== */
    float flame = 0f;              /* 0..1 */
    Vector3 flamePos;
    bool showAir = false, realView = true;

    void SimStep(float dt)
    {
        BuildPairs();

        for (int i = 0; i < nP; i++) prevPos[i] = px[i];
        for (int it = 0; it < 3; it++) Separate();

        /* המהירות חייבת ללמוד על תיקון המיקום. בלי זה חלקיק שנח על
           הערימה נדחף למעלה במיקום וממשיך לצבור מהירות למטה, והנוזל
           רותח בלי שאיש חימם אותו. */
        float inv = 1f / dt;
        for (int i = 0; i < nP; i++)
        {
            Vector3 c = (px[i] - prevPos[i]) * inv;
            if (c.sqrMagnitude > 36f) c = c.normalized * 6f;
            pv[i] = pv[i] * 0.55f + c * 0.45f;
        }

        /* צפיפות מקומית, הולכת חום וחום כמוס — הכל בסריקה אחת של הזוגות.
           חום עובר רק בין שכנות ממש. אין דרך שנר בפינה אחת של החדר
           יחמם את הפינה השנייה, אלא שכנה אחרי שכנה. */
        float kCond = dt * 2.6f;
        for (int k = 0; k < nPairs; k++)
        {
            int i = pairs[k * 2], j = pairs[k * 2 + 1];
            pRho[i] += DensityOf(j); pAround[i]++;
            pRho[j] += DensityOf(i); pAround[j]++;
            if (pPhase[j] != GAS) pWet[i]++;
            if (pPhase[i] != GAS) pWet[j]++;

            float cw = Mathf.Min(COND[pPhase[i]], COND[pPhase[j]]) * kCond;
            float dT = (pT[j] - pT[i]) * cw;
            pT[i] += dT; pT[j] -= dT;

            /* בועה שנולדה גובה את החום הכמוס שלה מהשכנות. זה מה שמחזיק
               נוזל רותח על נקודת הרתיחה במקום לטפס לאלף מעלות. */
            if (pCool[i] > 0) pT[j] -= pCool[i] / Mathf.Max(6f, pAround[i]);
            if (pCool[j] > 0) pT[i] -= pCool[j] / Mathf.Max(6f, pAround[j]);
        }
        System.Array.Clear(pCool, 0, nP);

        WallExchange(dt);

        for (int i = 0; i < nP; i++)
        {
            UpdatePhase(i, dt);
            int ph = pPhase[i];

            /* כובד וציפה בצעד אחד: מה שדוחף גוף מעלה או מטה הוא ההפרש
               בין צפיפותו לצפיפות מה שמקיף אותו. שמן צף על מים בלי
               שאף אחד כתב "שמן צף". */
            float mine = DensityOf(i);
            float amb = pAround[i] > 2 ? pRho[i] / pAround[i] : mine;
            float lift = Mathf.Clamp((amb - mine) / Mathf.Max(mine, 1e-4f), -6f, 6f);
            float g = ph == GAS ? 1.6f : 9.81f;
            /* אוויר חופשי לא נופל: משקלו נישא בידי האוויר שמתחתיו,
               וגובה הסקאלה של האטמוספירה הוא שמונה קילומטר. */
            float weight = pAir[i] && pVes[i] < 0 ? 0f : g;
            float conv = (ph == GAS && pVes[i] >= 0)
                ? Mathf.Clamp01((pT[i] - AMBIENT) / 120f) * 1.8f : 0f;
            pv[i] += Vector3.up * ((-weight + g * lift + conv) * dt);

            /* הלהבה מחממת רק את מה שיושב מעליה. משם החום מטפס פנימה
               שכנה־שכנה, ולכן הרתיחה מתחילה למטה. */
            if (flame > 0.001f)
            {
                Vector3 d = px[i] - flamePos;
                float rr = new Vector2(d.x, d.z).magnitude;
                if (rr < 0.055f && d.y > -0.01f && d.y < 0.10f)
                    pT[i] += flame * 55f * (1f - d.y / 0.10f) * (1f - rr / 0.055f) * dt;
            }

            float therm = ph == GAS ? Mathf.Clamp((pT[i] - SP[pSp[i]].boil) / 260f, 0.25f, 3.2f)
                        : ph == LIQ ? 0.16f : 0.02f;
            pv[i] += new Vector3(Random.Range(-1f, 1f), Random.Range(-1f, 1f), Random.Range(-1f, 1f))
                     * (therm * dt * 0.30f);

            float damp = Mathf.Exp(-(ph == GAS ? 0.55f : ph == LIQ ? 3.4f : 11.0f) * dt);
            pv[i] *= damp;
            px[i] += pv[i] * dt;

            Contain(i, dt);
        }
    }

    void UpdatePhase(int i, float dt)
    {
        var s = SP[pSp[i]];
        float T = pT[i];
        int ph = pPhase[i];

        if (ph == LIQ && T > s.boil)
        {
            /* הרתיחה אינה סף חד. מולקולה עמוקה נמצאת תחת לחץ ומתאדה
               פחות; קודם כל 240 המולקולות התהפכו בפריים אחד ולא נראה
               כמו רתיחה אלא כמו מתג. */
            float over = Mathf.Clamp01((T - s.boil) / 25f);
            float depth = Mathf.Clamp01(pWet[i] / 14f);
            if (Random.value < over * (1f - depth * 0.55f) * dt * 6f)
            {
                pPhase[i] = GAS;
                pCool[i] = s.latent;
                pT[i] -= s.latent * 0.12f;
            }
        }
        else if (ph == GAS && T < s.boil - 1f)
        {
            float under = Mathf.Clamp01((s.boil - T) / 25f);
            if (Random.value < under * dt * 5f) { pPhase[i] = LIQ; pT[i] += s.latent * 0.08f; }
        }
        else if (ph == LIQ && T < s.melt) { if (Random.value < dt * 3f) pPhase[i] = SOL; }
        else if (ph == SOL && T > s.melt) { if (Random.value < dt * 3f) pPhase[i] = LIQ; }
    }

    /* ----------------------------------------------------------------------
       הזכוכית איננה גבול מתמטי אלא גוף עם טמפרטורה. החומר שבפנים מחמם
       אותה, אוויר החדר מקרר אותה, והיא באמצע. לכן כלי בלי אוויר סביבו
       לא מתקרר — וזה בדיוק תרמוס.
       ---------------------------------------------------------------------- */
    const float K_IN = 2.6f, K_OUT = 0.10f, K_AIR = 0.9f;

    void WallExchange(float dt)
    {
        for (int vi = 0; vi < vessels.Count; vi++)
        {
            var v = vessels[vi];
            float sum = 0; int n = 0;
            for (int i = 0; i < nP; i++)
                if (pVes[i] == vi && !pAir[i]) { sum += pT[i]; n++; }
            v.count = n;
            v.meanT = n > 0 ? sum / n : v.wallT;

            float Ti = n > 0 ? sum / n : v.wallT;
            float kIn = n > 0 ? K_IN : 0f;
            float s = Mathf.Min(1f, (kIn + K_OUT) * dt) / Mathf.Max(kIn + K_OUT, 1e-6f);
            v.wallT += ((Ti - v.wallT) * kIn + (AMBIENT - v.wallT) * K_OUT) * s;

            /* הלהבה מחממת גם את הזכוכית עצמה, לא רק את מה שבתוכה */
            if (flame > 0.001f)
            {
                Vector3 d = v.tr.position - flamePos;
                if (new Vector2(d.x, d.z).magnitude < 0.06f && d.y > -0.02f && d.y < 0.08f)
                    v.wallT += flame * 40f * dt;
            }

            float k = Mathf.Min(0.9f, K_IN * dt);
            for (int i = 0; i < nP; i++)
                if (pVes[i] == vi) pT[i] += (v.wallT - pT[i]) * k;
        }

        /* אוויר חופשי חוזר לאט לטמפרטורת החדר: מעבר לפינה יש עוד מעבדה,
           והיא גדולה מכדי להתחמם. */
        for (int i = 0; i < nP; i++)
            if (pVes[i] < 0) pT[i] += (AMBIENT - pT[i]) * Mathf.Min(0.9f, 0.35f * dt);
    }

    /* ----------------------------------------------------------------------
       כליאה. נעשית במרחב המקומי של הכלי, ולכן היא נכונה גם כשהכלי מוטה,
       נופל או מתגלגל — והמזיגה יוצאת מזה בחינם: מטים את הכוס, החומר
       עובר את השפה, ומאותו רגע הוא נופל מכוח כובד.
       ---------------------------------------------------------------------- */
    void Contain(int i, float dt)
    {
        int vi = pVes[i];
        if (vi >= 0)
        {
            var v = vessels[vi];
            Vector3 L = v.tr.InverseTransformPoint(px[i]);
            float r = new Vector2(L.x, L.z).magnitude;

            if (L.y > v.rimY)
            {
                /* עבר את השפה — יצא. לא נועלים אותו בפנים. */
                pVes[i] = -1;
                return;
            }
            if (L.y < v.py[0])
            {
                L.y = v.py[0];
                Vector3 lv = v.tr.InverseTransformDirection(pv[i]);
                if (lv.y < 0) lv.y *= -0.25f;
                pv[i] = v.tr.TransformDirection(lv);
            }
            float maxR = v.InnerR(L.y) - R0 * 0.5f;
            if (maxR < 0.0005f) maxR = 0.0005f;
            if (r > maxR && r > 1e-6f)
            {
                float sc = maxR / r;
                L.x *= sc; L.z *= sc;
                Vector3 lv = v.tr.InverseTransformDirection(pv[i]);
                lv.x *= -0.35f; lv.z *= -0.35f;
                pv[i] = v.tr.TransformDirection(lv);
            }
            px[i] = v.tr.TransformPoint(L);
            return;
        }

        /* חופשי: נופל, ואולי נכנס לכלי שנמצא מתחתיו */
        for (int k = 0; k < vessels.Count; k++)
        {
            var v = vessels[k];
            Vector3 L = v.tr.InverseTransformPoint(px[i]);
            if (L.y < v.py[0] || L.y > v.rimY) continue;
            float r = new Vector2(L.x, L.z).magnitude;
            if (r <= v.InnerR(L.y)) { pVes[i] = k; return; }
        }

        /* השולחן והרצפה. חומר שנשפך על השולחן נשאר עליו. */
        float floorY = 0f;
        if (px[i].x > benchMin.x && px[i].x < benchMax.x &&
            px[i].z > benchMin.z && px[i].z < benchMax.z) floorY = benchTopY;
        if (px[i].y < floorY + R0 * 0.5f)
        {
            px[i] = new Vector3(px[i].x, floorY + R0 * 0.5f, px[i].z);
            var vv = pv[i]; vv.y = Mathf.Abs(vv.y) * 0.18f; vv.x *= 0.7f; vv.z *= 0.7f;
            pv[i] = vv;
        }
    }

    /* ======================================================================
       8)  העולם
       ====================================================================== */
    Vector3 benchMin, benchMax;
    float benchTopY = 0.92f;
    Transform burnerTr;
    Transform flameTr;

    void BuildMaterials()
    {
        mGlass = Glass(new Color(0.80f, 0.88f, 0.93f, 0.16f), 0.97f);
        mWood = Mat(new Color(0.28f, 0.17f, 0.09f), 0.25f);
        mSteel = Mat(new Color(0.55f, 0.57f, 0.60f), 0.72f, 0.85f);
        mWhite = Mat(new Color(0.88f, 0.89f, 0.90f), 0.20f);
        mFloor = Mat(new Color(0.62f, 0.63f, 0.65f), 0.32f);
        mWall = Mat(new Color(0.84f, 0.85f, 0.86f), 0.10f);
        mFlame = Mat(new Color(1.0f, 0.55f, 0.15f), 0.0f);
        mLiquid = Glass(new Color(0.55f, 0.75f, 0.95f, 0.62f), 0.90f);
        mAtom = new Material[elCol.Length];
        for (int i = 0; i < elCol.Length; i++) mAtom[i] = Mat(elCol[i], 0.45f);
    }

    void BuildRoom()
    {
        var room = new GameObject("Room").transform;
        float W = 7f, D = 6f, H = 3.1f;

        Box("Floor", new Vector3(W, 0.1f, D), mFloor, room, new Vector3(0, -0.05f, 0));
        Box("Ceiling", new Vector3(W, 0.1f, D), mWhite, room, new Vector3(0, H, 0));
        Box("Wall-N", new Vector3(W, H, 0.1f), mWall, room, new Vector3(0, H / 2, D / 2));
        Box("Wall-S", new Vector3(W, H, 0.1f), mWall, room, new Vector3(0, H / 2, -D / 2));
        Box("Wall-E", new Vector3(0.1f, H, D), mWall, room, new Vector3(W / 2, H / 2, 0));
        Box("Wall-W", new Vector3(0.1f, H, D), mWall, room, new Vector3(-W / 2, H / 2, 0));

        /* שולחן העבודה */
        var bench = new GameObject("Bench").transform;
        bench.SetParent(room, false);
        float bw = 2.6f, bd = 0.9f;
        benchTopY = 0.92f;
        Box("Top", new Vector3(bw, 0.06f, bd), mWood, bench, new Vector3(0, benchTopY - 0.03f, 0.6f));
        for (int sx = -1; sx <= 1; sx += 2)
            for (int sz = -1; sz <= 1; sz += 2)
                Box("Leg", new Vector3(0.07f, benchTopY - 0.06f, 0.07f), mSteel, bench,
                    new Vector3(sx * (bw / 2 - 0.09f), (benchTopY - 0.06f) / 2, 0.6f + sz * (bd / 2 - 0.09f)));
        benchMin = new Vector3(-bw / 2, 0, 0.6f - bd / 2);
        benchMax = new Vector3(bw / 2, 0, 0.6f + bd / 2);

        /* מדף עם בקבוקים — רקע, לא משהו שאפשר להשתמש בו עדיין */
        var shelf = new GameObject("Shelf").transform;
        shelf.SetParent(room, false);
        for (int lvl = 0; lvl < 3; lvl++)
        {
            float y = 1.35f + lvl * 0.42f;
            Box("Board", new Vector3(2.4f, 0.035f, 0.28f), mWhite, shelf, new Vector3(2.0f, y, 2.6f));
            for (int b = 0; b < 14; b++)
            {
                var col = Color.HSVToRGB(Random.value, Random.Range(0.25f, 0.6f), Random.Range(0.45f, 0.8f));
                float hh = Random.Range(0.11f, 0.19f);
                Cyl("Bottle", Random.Range(0.026f, 0.038f), hh, Mat(col, 0.6f), shelf,
                    new Vector3(2.0f - 1.1f + b * 0.16f, y + 0.02f + hh / 2, 2.6f), false);
            }
        }

        /* מבער בונזן: בסיס, צינור, ולהבה שגדלה עם החוגה */
        var burner = new GameObject("Burner").transform;
        burner.SetParent(room, false);
        burner.position = new Vector3(-0.45f, benchTopY, 0.55f);
        burnerTr = burner;
        Cyl("Base", 0.055f, 0.014f, mSteel, burner, new Vector3(0, 0.007f, 0));
        Cyl("Barrel", 0.011f, 0.11f, mSteel, burner, new Vector3(0, 0.068f, 0));
        var fl = Cyl("Flame", 0.013f, 0.07f, mFlame, burner, new Vector3(0, 0.155f, 0), false);
        flameTr = fl.transform;
        flameTr.localScale = Vector3.zero;
        var fLight = new GameObject("FlameLight");
        fLight.transform.SetParent(burner, false);
        fLight.transform.localPosition = new Vector3(0, 0.16f, 0);
        var fL = fLight.AddComponent<Light>();
        fL.type = LightType.Point; fL.color = new Color(1f, 0.6f, 0.25f);
        fL.range = 1.2f; fL.intensity = 0f;
        flameLight = fL;
        flamePos = burner.position + Vector3.up * 0.13f;

        /* חצובה מעל הלהבה, שעליה מניחים את הכלי */
        var tri = new GameObject("Tripod").transform;
        tri.SetParent(burner, false);
        for (int i = 0; i < 3; i++)
        {
            float a = i * Mathf.PI * 2f / 3f;
            var leg = Cyl("Leg", 0.004f, 0.19f, mSteel, tri,
                new Vector3(Mathf.Cos(a) * 0.058f, 0.095f, Mathf.Sin(a) * 0.058f));
            leg.transform.localRotation = Quaternion.Euler(0, 0, 0);
        }
        var ring = new GameObject("Ring");
        ring.transform.SetParent(tri, false);
        ring.transform.localPosition = new Vector3(0, 0.19f, 0);
        var rm = TorusMesh(0.058f, 0.004f, 24, 8);
        ring.AddComponent<MeshFilter>().sharedMesh = rm;
        ring.AddComponent<MeshRenderer>().sharedMaterial = mSteel;
        var rc = ring.AddComponent<MeshCollider>();
        rc.sharedMesh = rm;
        /* טבעת אינה קמורה, ולכן היא נשארת מתנגש סטטי ולא קמור */

        /* גז לרעיון של מסך: רשת מתכת שטוחה על הטבעת, כדי שכלי לא יפול פנימה */
        Cyl("Gauze", 0.055f, 0.003f, mSteel, tri, new Vector3(0, 0.192f, 0));
    }

    Light flameLight;

    static Mesh TorusMesh(float R, float r, int seg, int side)
    {
        var V = new List<Vector3>(); var N = new List<Vector3>(); var I = new List<int>();
        for (int i = 0; i <= seg; i++)
        {
            float a = i / (float)seg * Mathf.PI * 2f;
            Vector3 c = new Vector3(Mathf.Cos(a) * R, 0, Mathf.Sin(a) * R);
            Vector3 outw = new Vector3(Mathf.Cos(a), 0, Mathf.Sin(a));
            for (int j = 0; j <= side; j++)
            {
                float b = j / (float)side * Mathf.PI * 2f;
                Vector3 nn = outw * Mathf.Cos(b) + Vector3.up * Mathf.Sin(b);
                V.Add(c + nn * r); N.Add(nn);
            }
        }
        for (int i = 0; i < seg; i++)
            for (int j = 0; j < side; j++)
            {
                int a = i * (side + 1) + j, c = a + side + 1;
                I.Add(a); I.Add(c); I.Add(a + 1);
                I.Add(a + 1); I.Add(c); I.Add(c + 1);
            }
        return Finish(V, N, I);
    }

    void BuildLights()
    {
        var sun = new GameObject("Sun").AddComponent<Light>();
        sun.type = LightType.Directional;
        sun.transform.rotation = Quaternion.Euler(48f, 35f, 0);
        sun.intensity = 1.05f;
        sun.color = new Color(1f, 0.97f, 0.92f);
        sun.shadows = LightShadows.Soft;

        for (int i = -1; i <= 1; i += 2)
        {
            var l = new GameObject("Strip").AddComponent<Light>();
            l.type = LightType.Point;
            l.transform.position = new Vector3(i * 1.6f, 2.75f, 0.8f);
            l.range = 7f; l.intensity = 1.1f;
            l.color = new Color(0.95f, 0.97f, 1f);
        }
        RenderSettings.ambientMode = AmbientMode.Trilight;
        RenderSettings.ambientSkyColor = new Color(0.42f, 0.45f, 0.50f);
        RenderSettings.ambientEquatorColor = new Color(0.32f, 0.33f, 0.35f);
        RenderSettings.ambientGroundColor = new Color(0.18f, 0.18f, 0.19f);
    }

    /* ======================================================================
       9)  השחקן
       ====================================================================== */
    CharacterController cc;
    Transform camTr;
    Camera cam;
    float pitch = 0f, yaw = 0f;
    Vector3 vel;
    Transform holdPoint;
    Vessel heldVessel;
    int selectedSpecies = 0;

    void BuildPlayer()
    {
        var p = new GameObject("Player");
        p.transform.position = new Vector3(0, 0.1f, -1.4f);
        cc = p.AddComponent<CharacterController>();
        cc.height = 1.72f; cc.radius = 0.28f; cc.center = new Vector3(0, 0.86f, 0);
        cc.slopeLimit = 50f; cc.stepOffset = 0.32f;

        var c = new GameObject("Camera");
        c.transform.SetParent(p.transform, false);
        c.transform.localPosition = new Vector3(0, 1.62f, 0);
        cam = c.AddComponent<Camera>();
        cam.nearClipPlane = 0.02f;   /* כדי שאפשר יהיה לקרב את הפנים לזכוכית */
        cam.farClipPlane = 60f;
        cam.fieldOfView = 68f;
        c.AddComponent<AudioListener>();
        camTr = c.transform;

        holdPoint = new GameObject("Hold").transform;
        holdPoint.SetParent(camTr, false);
        holdPoint.localPosition = new Vector3(0.19f, -0.17f, 0.34f);

        yaw = 0f;
    }

    void MovePlayer(float dt)
    {
        if (Cursor.lockState == CursorLockMode.Locked)
        {
            yaw += In.Look.x * In.LookScale * 1.4f;
            pitch = Mathf.Clamp(pitch - In.Look.y * In.LookScale * 1.4f, -88f, 88f);
        }
        transformYaw();

        Vector3 fwd = Quaternion.Euler(0, yaw, 0) * Vector3.forward;
        Vector3 right = Quaternion.Euler(0, yaw, 0) * Vector3.right;
        Vector3 dir = (fwd * In.MoveZ + right * In.MoveX);
        if (dir.sqrMagnitude > 1f) dir.Normalize();

        float speed = In.Sprint ? 3.9f : 1.9f;
        if (cc.isGrounded)
        {
            vel.y = -1f;
            if (In.Jump) vel.y = 4.1f;
        }
        else vel.y -= 15f * dt;

        Vector3 step = dir * speed + Vector3.up * vel.y;
        cc.Move(step * dt);
    }

    void transformYaw()
    {
        cc.transform.rotation = Quaternion.Euler(0, yaw, 0);
        camTr.localRotation = Quaternion.Euler(pitch, 0, 0);
    }

    /* ======================================================================
       10)  אינטראקציה
       ====================================================================== */
    string prompt = "";

    void Interact(float dt)
    {
        prompt = "";
        Ray ray = new Ray(camTr.position, camTr.forward);

        if (heldVessel != null)
        {
            prompt = "E  put down     Q  pour     F  fill with " + SP[selectedSpecies].label;
            /* מזיגה: מטים את הכלי קדימה. הכליאה עושה את השאר. */
            float tilt = In.Pour ? 118f : 0f;
            heldVessel.tr.rotation = Quaternion.Slerp(heldVessel.tr.rotation,
                camTr.rotation * Quaternion.Euler(tilt, 0, 0), 1f - Mathf.Exp(-11f * dt));
            heldVessel.tr.position = Vector3.Lerp(heldVessel.tr.position,
                holdPoint.position, 1f - Mathf.Exp(-18f * dt));

            if (In.Use) DropVessel();
            if (In.Fill) FillHeld();
            return;
        }

        RaycastHit hit;
        if (Physics.Raycast(ray, out hit, 2.4f))
        {
            var v = FindVessel(hit.collider.transform);
            if (v != null)
            {
                prompt = "E  pick up " + v.name + "     " + Mathf.Round(v.meanT) + "\u00B0C     " +
                         v.count + " particles";
                if (In.Use) PickUp(v);
                return;
            }
            if (hit.collider.transform.IsChildOf(burnerTr))
            {
                prompt = "Scroll  flame  (" + Mathf.RoundToInt(flame * 100f) + "%)";
                if (Mathf.Abs(In.Scroll) > 0.01f)
                    flame = Mathf.Clamp01(flame + In.Scroll * 0.09f);
                return;
            }
        }
    }

    Vessel FindVessel(Transform t)
    {
        for (int i = 0; i < vessels.Count; i++)
            if (t == vessels[i].tr || t.IsChildOf(vessels[i].tr)) return vessels[i];
        return null;
    }

    void PickUp(Vessel v)
    {
        heldVessel = v;
        v.rb.isKinematic = true;
        v.rb.detectCollisions = false;
    }

    void DropVessel()
    {
        if (heldVessel == null) return;
        var v = heldVessel;
        v.rb.isKinematic = false;
        v.rb.detectCollisions = true;
        v.rb.velocity = Vector3.zero;
        v.rb.angularVelocity = Vector3.zero;
        heldVessel = null;
    }

    /* ממלאים את הכלי שביד בחומר הנבחר, ליד השפה, ונותנים לו ליפול */
    void FillHeld()
    {
        var v = heldVessel;
        if (v == null) return;
        int vi = vessels.IndexOf(v);
        int add = 420;
        for (int k = 0; k < add && nP < MAXP; k++)
        {
            float y = Random.Range(v.py[0] + 0.004f, Mathf.Min(v.rimY, v.py[0] + 0.05f));
            float rr = v.InnerR(y) * Mathf.Sqrt(Random.value) * 0.9f;
            float a = Random.value * Mathf.PI * 2f;
            Vector3 L = new Vector3(Mathf.Cos(a) * rr, y, Mathf.Sin(a) * rr);
            Spawn(selectedSpecies, v.tr.TransformPoint(L), vi);
        }
    }

    /* אוויר בכל החדר. לא קישוט: הוא זה שמקרר את הזכוכית, ובלעדיו כלי
       חם נשאר חם לנצח. */
    void FillAir()
    {
        int n = 900;
        for (int k = 0; k < n && nP < MAXP; k++)
        {
            var pos = new Vector3(Random.Range(-1.6f, 1.6f), Random.Range(0.95f, 2.3f),
                                  Random.Range(-0.6f, 1.7f));
            Spawn(Random.value < 0.78f ? 3 : 1, pos, -1, true);
        }
    }

    /* ======================================================================
       11)  ציור החלקיקים
       ====================================================================== */
    Matrix4x4[] batch = new Matrix4x4[1023];
    List<int>[] byElement;

    void DrawParticles()
    {
        if (byElement == null)
        {
            byElement = new List<int>[elCol.Length];
            for (int i = 0; i < byElement.Length; i++) byElement[i] = new List<int>(4096);
        }

        if (realView)
        {
            /* במצג האמיתי לא מציירים מולקולות אלא נוזל: הנפח נקבע מספירת
               החלקיקים, וגובה המפלס מהפרופיל הפנימי של הכלי. בועה היא גז
               שנוזל עוטף אותו — לא כל גז. */
            DrawLiquidSurfaces();
            DrawBubbles();
            return;
        }

        for (int e = 0; e < byElement.Length; e++) byElement[e].Clear();
        /* בונים את הרשימות פעם אחת, ואז ציור אחד לכל יסוד */
        for (int i = 0; i < nP; i++)
        {
            if (pAir[i] && !showAir) continue;
            var s = SP[pSp[i]];
            for (int a = 0; a < s.atoms.Length; a++) byElement[s.atoms[a]].Add(i * 8 + a);
        }

        for (int e = 0; e < byElement.Length; e++)
        {
            var list = byElement[e];
            int n = 0;
            for (int k = 0; k < list.Count; k++)
            {
                int i = list[k] / 8, a = list[k] % 8;
                var s = SP[pSp[i]];
                float md = MODEL[pPhase[i]];
                Vector3 pos = px[i] + s.offs[a] * md;
                float rad = elR[e] * md * 2f;
                batch[n++] = Matrix4x4.TRS(pos, Quaternion.identity, Vector3.one * rad);
                if (n == 1023)
                {
                    Graphics.DrawMeshInstanced(Sphere(), 0, mAtom[e], batch, n);
                    n = 0;
                }
            }
            if (n > 0) Graphics.DrawMeshInstanced(Sphere(), 0, mAtom[e], batch, n);
        }
    }

    /* נפח חלקיק בודד, מהמרווח שלו */
    const float PVOL = R0 * R0 * R0 * 0.74f;

    void DrawLiquidSurfaces()
    {
        for (int vi = 0; vi < vessels.Count; vi++)
        {
            var v = vessels[vi];
            int liq = 0; Color tint = Color.white; int domSp = 0; var spCount = new int[4];
            for (int i = 0; i < nP; i++)
                if (pVes[i] == vi && !pAir[i] && pPhase[i] != GAS) { liq++; spCount[pSp[i]]++; }
            for (int s = 1; s < 4; s++) if (spCount[s] > spCount[domSp]) domSp = s;

            /* כלי מוטה — פני הנוזל כבר לא ניצבים לצירו, והרשת הזאת תשקר.
               באותם רגעים מציירים את החלקיקים עצמם. */
            float tilt = Vector3.Angle(v.tr.up, Vector3.up);
            if (liq < 12 || tilt > 22f)
            {
                v.liquidMR.enabled = false;
                DrawVesselParticles(vi);
                continue;
            }
            v.liquidMR.enabled = true;

            float fy = v.FillHeight(liq * PVOL);
            if (Mathf.Abs(fy - v.lastFill) > 0.0015f || v.liquidMF.sharedMesh == null)
            {
                v.lastFill = fy;
                v.liquidMF.sharedMesh = LiquidMesh(v, fy);
            }
            tint = SP[domSp].tint;
            /* צבע לפי מצב: קרח בהיר יותר ממים */
            if (v.meanT < SP[domSp].melt) tint = Color.Lerp(tint, Color.white, 0.45f);
            v.liquidMR.material.SetColor(IsURP ? "_BaseColor" : "_Color", tint);
        }
    }

    void DrawVesselParticles(int vi)
    {
        int n = 0;
        var mat = mAtom[EL_O];
        for (int i = 0; i < nP; i++)
        {
            if (pVes[i] != vi || pAir[i]) continue;
            batch[n++] = Matrix4x4.TRS(px[i], Quaternion.identity, Vector3.one * R0 * 1.15f);
            if (n == 1023) { Graphics.DrawMeshInstanced(Sphere(), 0, mat, batch, n); n = 0; }
        }
        if (n > 0) Graphics.DrawMeshInstanced(Sphere(), 0, mat, batch, n);
    }

    void DrawBubbles()
    {
        int n = 0;
        for (int i = 0; i < nP; i++)
        {
            if (pAir[i] && !showAir) continue;
            if (pPhase[i] != GAS) continue;
            /* בועה היא גז שנוזל עוטף אותו. גז שפרץ אל מעל פני הנוזל הוא
               אדים, ואדים אינם כדורים — הם מתפזרים ונעלמים. */
            bool bubble = pWet[i] >= 4;
            if (!bubble && pVes[i] < 0) continue;
            float rad = bubble ? R0 * 1.5f : R0 * 0.8f;
            batch[n++] = Matrix4x4.TRS(px[i], Quaternion.identity, Vector3.one * rad);
            if (n == 1023) { Graphics.DrawMeshInstanced(Sphere(), 0, mGlass, batch, n); n = 0; }
        }
        if (n > 0) Graphics.DrawMeshInstanced(Sphere(), 0, mGlass, batch, n);
    }

    Mesh LiquidMesh(Vessel v, float fillY)
    {
        var pts = new List<Vector2>();
        pts.Add(new Vector2(Mathf.Max(0.0006f, v.InnerR(fillY) - 0.0004f), fillY));
        for (int i = v.py.Length - 1; i >= 0; i--)
            if (v.py[i] < fillY) pts.Add(new Vector2(Mathf.Max(0.0006f, v.pr[i] - 0.0004f), v.py[i]));
        pts.Add(new Vector2(0.0006f, v.py[0]));
        var m = Lathe(pts.ToArray(), 32);
        /* מכסה שטוח לפני הנוזל, אחרת רואים לתוך גוף חלול */
        var V = new List<Vector3>(); var N = new List<Vector3>(); var I = new List<int>();
        float r = Mathf.Max(0.0006f, v.InnerR(fillY) - 0.0004f);
        V.Add(new Vector3(0, fillY, 0)); N.Add(Vector3.up);
        int segs = 32;
        for (int s = 0; s <= segs; s++)
        {
            float a = s / (float)segs * Mathf.PI * 2f;
            V.Add(new Vector3(Mathf.Cos(a) * r, fillY, Mathf.Sin(a) * r)); N.Add(Vector3.up);
        }
        for (int s = 0; s < segs; s++) { I.Add(0); I.Add(s + 1); I.Add(s + 2); }
        var cap = Finish(V, N, I);

        var comb = new CombineInstance[2];
        comb[0].mesh = m; comb[0].transform = Matrix4x4.identity;
        comb[1].mesh = cap; comb[1].transform = Matrix4x4.identity;
        var outm = new Mesh();
        outm.CombineMeshes(comb, true, true);
        return outm;
    }

    /* ======================================================================
       12)  מחזור החיים
       ====================================================================== */
    void Awake()
    {
        Application.targetFrameRate = 60;
        BuildSpecies();
        BuildMaterials();
        BuildLights();
        BuildRoom();
        BuildPlayer();

        /* הכלים על השולחן */
        MakeFlask(new Vector3(-0.45f, benchTopY + 0.21f, 0.55f));   /* על החצובה */
        MakeBeaker(new Vector3(0.10f, benchTopY + 0.01f, 0.55f));
        MakeErlen(new Vector3(0.45f, benchTopY + 0.01f, 0.70f));
        MakeTube(new Vector3(0.72f, benchTopY + 0.01f, 0.45f));

        /* מים בבקבוק, ואוויר בכל החדר */
        var flask = vessels[0];
        for (int k = 0; k < 1500 && nP < MAXP; k++)
        {
            float y = Random.Range(flask.py[0] + 0.003f, 0.055f);
            float rr = flask.InnerR(y) * Mathf.Sqrt(Random.value) * 0.92f;
            float a = Random.value * Mathf.PI * 2f;
            Spawn(0, flask.tr.TransformPoint(new Vector3(Mathf.Cos(a) * rr, y, Mathf.Sin(a) * rr)), 0);
        }
        FillAir();

        Cursor.lockState = CursorLockMode.Locked;
        Cursor.visible = false;
    }

    float bank = 0f;
    const float FIXED = 1f / 90f;

    void Update()
    {
        In.Poll();

        if (In.Esc) { Cursor.lockState = CursorLockMode.None; Cursor.visible = true; }
        if (In.Click && Cursor.lockState != CursorLockMode.Locked)
        { Cursor.lockState = CursorLockMode.Locked; Cursor.visible = false; }

        if (In.ToggleView) realView = !realView;
        if (In.ToggleAir) showAir = !showAir;
        if (In.Digit > 0) selectedSpecies = In.Digit - 1;

        float dt = Mathf.Min(Time.deltaTime, 0.05f);
        MovePlayer(dt);
        Interact(dt);

        /* להבה: גודל, אור וריצוד */
        float fs = flame;
        flameTr.localScale = new Vector3(0.026f * (0.6f + fs), 0.035f * fs * (0.9f + 0.1f * Mathf.Sin(Time.time * 27f)), 0.026f * (0.6f + fs));
        flameLight.intensity = fs * 2.6f * (0.92f + 0.08f * Mathf.Sin(Time.time * 31f));

        /* צעד קבוע: מכשיר איטי מפיל פריימים, אבל הזמן בעולם ממשיך
           באותו קצב, והפיזיקה לא משנה התנהגות לפי חוזק המחשב. */
        bank += dt;
        int steps = 0;
        while (bank >= FIXED && steps < 4) { SimStep(FIXED); bank -= FIXED; steps++; }
        if (bank > FIXED * 4) bank = FIXED * 4;

        DrawParticles();
    }

    /* ======================================================================
       13)  ממשק
       ====================================================================== */
    GUIStyle st, stBig, stLeft;

    void OnGUI()
    {
        if (st == null)
        {
            st = new GUIStyle(GUI.skin.label) { fontSize = 15, alignment = TextAnchor.MiddleCenter };
            st.normal.textColor = Color.white;
            stBig = new GUIStyle(GUI.skin.label) { fontSize = 21, fontStyle = FontStyle.Bold };
            stBig.normal.textColor = Color.white;
            stLeft = new GUIStyle(st) { alignment = TextAnchor.MiddleLeft };
        }

        float w = Screen.width, h = Screen.height;

        /* כוונת */
        GUI.color = new Color(1, 1, 1, 0.75f);
        GUI.DrawTexture(new Rect(w / 2 - 1.5f, h / 2 - 1.5f, 3, 3), Texture2D.whiteTexture);
        GUI.color = Color.white;

        /* שורת מצב עליונה */
        GUI.Box(new Rect(w / 2 - 250, 12, 500, 30), "");
        string top = SP[selectedSpecies].label +
                     "     flame " + Mathf.RoundToInt(flame * 100) + "%" +
                     "     " + nP + " particles" +
                     "     " + (realView ? "Real" : "Molecules") +
                     (showAir ? " + air" : "");
        GUI.Label(new Rect(w / 2 - 250, 12, 500, 30), top, st);

        /* מדחום לכל כלי שמונח מול השחקן */
        float yy = 56;
        for (int i = 0; i < vessels.Count; i++)
        {
            var v = vessels[i];
            if (v.count == 0) continue;
            string line = v.name + "   " + Mathf.Round(v.meanT) + "\u00B0C    glass " + Mathf.Round(v.wallT) + "\u00B0C    " + v.count;
            GUI.Label(new Rect(14, yy, 460, 24), line, stLeft);
            yy += 22;
        }

        /* הודעת פעולה */
        if (prompt != "")
        {
            GUI.Box(new Rect(w / 2 - 260, h - 92, 520, 30), "");
            GUI.Label(new Rect(w / 2 - 260, h - 92, 520, 30), prompt, st);
        }

        /* עזרה */
        GUI.Label(new Rect(w / 2 - 320, h - 52, 640, 26),
            "WASD move  ·  Shift run  ·  E pick up  ·  Q pour  ·  F fill  ·  1-4 substance  ·  V view  ·  G air  ·  scroll flame", st);
    }
}
