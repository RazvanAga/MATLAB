# PRD — Live AI Demo: Chatbot care conduce MATLAB/Simulink prin MCP

> Schaeffler | Interviu pentru rolul *AI-Enhanced MBD Specialist* (echipa PMT) | Status: spec înghețat, gata de implementare
>
> Decizii arhitecturale cheie: MATLAB MCP Core Server e **binar Go standalone** (fără MATLAB Engine for Python), MATLAB rulează **vizibil** (sesiune `existing`), Simulink prin **Simulink Agentic Toolkit**, frontend custom cu **carduri timeline**.

---

## Problem Statement

Aplic pentru rolul de specialist AI într-o echipă de suport MATLAB/Simulink (PMT, Schaeffler). Din notițele mele cu Team Leaderul reies două probleme: (1) „AI" e mai mult buzzword decât direcție clară pentru echipă, și (2) experiența mea pe MATLAB e percepută ca limitată. Un pitch verbal despre „AI workflows" nu răstoarnă nici una.

Interviul e **online, pe Microsoft Teams, cu screen-share** — deci tot ce arăt trebuie să fie lizibil prin compresia video Teams și să meargă fiabil de la distanță, fără a putea interveni fizic.

## Solution

Un chatbot local care conduce live o instanță reală de MATLAB R2026a / Simulink prin Model Context Protocol — exact stack-ul (Claude + MCP) pe care MathWorks l-a lansat oficial (core server nov. 2025) și pe care îl folosesc zilnic. În loc să *vorbesc* despre AI workflows, **arăt unul rulând**: scriu în limbaj natural, agentul decide, cheamă tool-uri MCP care execută cod în MATLAB-ul real, iar rezultatele (output numeric + figuri) apar live în chat.

**Teza:** *„Nu vin să învăț AI workflows. Le construiesc deja. Iată unul care rulează pe MATLAB, acum."* Criteriul suprem: percepția trece de la „candidat cu MATLAB limitat" la „omul care poate ateriza partea de AI".

### Două artefacte, două axe (nu concurează)
Demonstrația finală constă din **două piese complementare**, pe axe diferite:

- **Web app-ul (acest PRD)** — prototipul unui *produs intern*: un asistent dedicat, cu suprafață îngustă de tool-uri, prompturi curate, guardrails și UI cu butoane, pe care un inginer de suport l-ar folosi fără IDE. Demonstrează că pot *construi* infrastructura agentică (FastAPI + MCP + tool_runner + SSE + UI), nu doar s-o consum — diferențiatorul pentru rolul „AI-Enhanced MBD Specialist".
- **Workflow-ul VSCode + Claude/Copilot + MATLAB MCP** (artefact separat, spec-uit ulterior) — *workflow-ul real de dezvoltare* pe care echipa l-ar adopta de mâine. Harness matur, efort mic, ancoră fiabilă.

**Ordine de construcție:** web app **întâi** (acest document), apoi workflow-ul VSCode.
**Ordine de prezentare (recomandată):** VSCode **întâi** ca ancoră sigură care aterizează ideea de bază („așa dezvoltăm modele"), apoi web app-ul ca diferențiator („și uite ce pot construi pe deasupra pentru echipă"). Dacă riscul forțează o tăiere live, VSCode e minimul garantat; web app-ul e piesa cu impact maxim dar mai fragilă.

> Acest PRD acoperă **doar web app-ul**. Workflow-ul VSCode va primi un spec separat, mai ușor, după ce web app-ul e gata.

### Criterii de succes
- **S1 — Fiabilitate live:** rulează end-to-end fără crash; 3 rulări consecutive reușite la repetiție.
- **S2 — MATLAB real:** agentul conduce MATLAB-ul real (nu mock) și întoarce output numeric + figură generată live.
- **S3 — Pas agentic vizibil:** UI-ul afișează fiecare decizie → tool call → rezultat.
- **S4 — Explicabilitate:** pot explica orice piesă din arhitectură la întrebări.
- **S5 — Setup reproductibil:** mediul se reface pe laptopul meu urmând checklist-ul de pre-flight.

## User Stories

### Demonstrator (eu, în timpul demo-ului)
1. Ca demonstrator, vreau butoane cu prompturile exacte ale scriptului, ca să nu tastez nimic live și să elimin riscul de input netestat.
2. Ca demonstrator, vreau ca butoanele să rămână vizibile și re-clickabile, ca să pot repeta orice pas dacă mă roagă „mai arată o dată".
3. Ca demonstrator, vreau un buton „extra sigur" cu un al doilea prompt testat, pentru când intervievatorul cere „pot să încerc și eu?".
4. Ca demonstrator, vreau un buton de reset care curăță timeline-ul ȘI rulează `close all; clear` în MATLAB, ca fiecare din cele 3 rulări de repetiție să pornească din stare identică.
5. Ca demonstrator, vreau un script de pre-flight care verifică ce poate (MATLAB partajat? server răspunde? folder figuri există?) și pornește backend-ul + browser-ul, ca să reduc eroarea live.
6. Ca demonstrator, vreau o înregistrare video + screenshot-uri de la o rulare reușită, ca să am plasă de siguranță dacă pică ceva live.
7. Ca demonstrator, vreau ca serverul să eșueze zgomotos la pornire dacă MATLAB-ul meu nu e pornit+partajat, ca să prind problema la pre-flight, nu în fața audienței.
8. Ca demonstrator, vreau să rulez totul pe laptopul meu pre-configurat, ca mediul testat la repetiție să fie identic cu cel de la interviu.

### Audiență (Team Leader PMT + intervievatori tehnici)
9. Ca intervievator, vreau să văd codul MATLAB pe care agentul îl generează, ca să mă conving că nu e un mock.
10. Ca intervievator, vreau să văd fiecare pas agentic distinct (decizie → tool call → rezultat), ca să înțeleg cum funcționează agentul.
11. Ca intervievator, vreau să văd output-ul real din Command Window și figurile generate, ca să verific că MATLAB-ul rulează cu adevărat.
12. Ca intervievator, vreau să văd că agentul conduce și Simulink pe un model `.slx`, ca să leg demonstrația de munca de MBD a echipei.
13. Ca intervievator, vreau să văd că agentul își verifică propriul cod (`check_matlab_code`) înainte să-l ruleze, ca semnal de rigoare de calitate relevant pentru MBD.
14. Ca intervievator pe Teams, vreau ca textul și figurile să fie lizibile prin screen-share, ca să urmăresc demo-ul de la distanță fără să mă chinui.
15. Ca intervievator, vreau să întreb „cum funcționează piesa X" și să primesc un răspuns clar, ca să-mi confirm că demonstratorul stăpânește arhitectura.

### Utilizator final ipotetic (proiecție, menționat verbal)
16. Ca inginer Schaeffler care cere suport MATLAB, aș vrea un asistent care triază problemele comune, ca să nu aștept suport manual.

### Agent (comportament intern)
17. Ca agent, vreau să primesc doar submulțimea relevantă de tool-uri MCP, ca să rămân focusat și predictibil în demo.
18. Ca agent, vreau instrucțiuni clare să exportez orice figură la o cale fixă cu timestamp, ca backend-ul să o poată detecta și afișa inline.
19. Ca agent, vreau să refolosesc variabilele din base workspace dacă există, dar să re-rulez simularea dacă lipsesc, ca follow-up-urile să meargă fără să cadă.
20. Ca agent, vreau un guardrail explicit read-only pe Simulink și fără operații distructive, ca să nu modific modele și să păstrez narațiunea de siguranță.

## Implementation Decisions

### Arhitectură & mediu
- **Lanțul:** Browser (chat) ⇄ SSE ⇄ FastAPI ⇄ Anthropic SDK (`tool_runner`) ⇄ MCP `ClientSession` (stdio) ⇄ **MATLAB MCP Core Server (binar Go standalone)** ⇄ MATLAB R2026a/Simulink. **NU există strat „MATLAB Engine for Python"** — core server-ul nu îl folosește.
- **Backend Python 3.13** (`anthropic[mcp]` cere doar 3.10+; nicio constrângere de Engine-for-Python, fiindcă core server-ul e binar standalone).
- **MATLAB rulează vizibil**, sesiune `--matlab-session-mode existing` **strict** (eșuează zgomotos dacă nu găsește sesiunea — evită pornirea unei sesiuni noi invizibile în care „dispare" figura). MATLAB-ul tău deschis trebuie pus pe `matlab.engine.shareEngine`.
- **Install unic:** `simulink-agentic-toolkit` (`.mltbx` → `setupAgenticToolkit("install")`), care descarcă automat și MATLAB MCP Core Server în `~/.matlab/agentic-toolkits/`. Acoperă ambele dependențe într-un pas.
- **Model:** `claude-opus-4-8`, `effort: medium` + adaptive thinking. Fallback testat: `claude-sonnet-4-6` (o linie de cod), decis la repetiție dacă latența opus deranjează.
- **Auth:** `anthropic.Anthropic()` fără argumente — preia automat profilul de la `ant auth login` (rezolvă din env: `ANTHROPIC_API_KEY` → `ANTHROPIC_AUTH_TOKEN` → profil OAuth).

### Bucla agentică & streaming
- **`client.beta.messages.tool_runner()`** cu tool-uri MCP convertite din `anthropic.lib.tools.mcp`, peste `stdio_client` → `ClientSession`. Granularitate **per-mesaj** (confirmat de doc: tool runner-ul Python întoarce mesaje complete) — exact ce vrem pentru a face vizibil pasul agentic.
- **Wrapper propriu peste fiecare tool MCP** ca punct unic de instrumentare: emite eveniment SSE „tool_use start" → cheamă tool-ul MCP → emite „tool_result" + verifică folderul de figuri → întoarce rezultatul runner-ului. Același choke-point servește streaming-ul SSE (vizibilitatea pasului agentic, S3) ȘI detecția figurilor.
- **Figuri:** system prompt-ul cere `exportgraphics(gcf, fullfile("<cale absolută>", sprintf("fig_%s.png", datestr(now,"HHMMSSFFF"))))`; backend-ul face **watch pe folder** și emite pe SSE (base64) orice PNG nou apărut după un `tool_result`. Decuplat de numele exact, fără re-afișarea figurilor vechi.
- **Stare workspace (hibrid):** follow-up-urile folosesc variabilele existente dacă există, dar system prompt-ul instruiește agentul să re-ruleze simularea dacă nu le găsește. Demonstrează continuitatea „aceleași date" fără să cadă dacă un apel anterior a eșuat. (De validat la F2 că modul `existing` nu curăță base workspace-ul între apeluri.)

### Tool-uri & comportament agent (system prompt focusat)
- **Suprafață de tool-uri restrânsă:** din cele ~12 disponibile (5 core + 7 Simulink), agentul primește doar submulțimea de demo (`evaluate_matlab_code`, `check_matlab_code`, tool-urile Simulink de read/sim).
- **System prompt focusat (nu agresiv** — opus-4-8 urmează literal și narează mult): instrucțiunea de export figuri, ghidarea selecției de tool-uri, guardrail read-only Simulink / fără operații distructive, re-derivarea defensivă a workspace-ului.
- **Skills-urile toolkit-ului (9 markdown) NU se auto-încarcă** în harness-ul custom — sunt pentru agenți cu suport de filesystem. Dacă vrem „expertiza" lor, o injectăm manual în system prompt.
- **`check_matlab_code` ca beat vizibil:** un pas scriptat în care agentul își verifică codul înainte de rulare.

### Simulink
- Folosim **Simulink Agentic Toolkit complet** (7 tool-uri MCP dedicate + skills), dar în demo arătăm **doar read + simulate** (deschide model → `sim` → citește semnalul) — păstrăm narațiunea ISO 26262 read-only, deși toolkit-ul are și capabilități de scriere pe care alegem să nu le folosim.
- **`demo.slx`:** **același sistem mass-spring-damper** ca în primul prompt MATLAB, dar ca bloc-diagramă (continuitate narativă „aceeași fizică, acum ca MBD"). Semnal logat explicit cu bloc **To Workspace** → trivial de citit, nu depinde de structura `out.yout`.

### Frontend (UI)
- **Tech:** vanilla HTML/JS, fără build step. **highlight.js** (cod) + **marked** (markdown text agent) **vendate local** — zero CDN, fără dependență de internet în afară de API-ul Anthropic.
- **Layout:** o coloană (header + timeline + input cu butoane). Browser-ul e doar chat-ul; MATLAB e fereastra de alături.
- **Estetică:** consolă tehnică light, contrast mare, font mare — calibrat pentru compresia Teams (evită fonturi subțiri și gri-uri low-contrast).
- **Branding:** logo Schaeffler discret sus (`public/Schaeffler_logo.svg.png`) + liniuță „internal demo tool"; accent **verde Schaeffler ~#009B3D** (eșantionat din logo). Opțional: logo-urile MATLAB/Simulink discret pe carduri/footer (`public/MATLAB-logo.png`, `public/Simulink_Logo.png`).
- **Cardul de pas (S3) — trei zone:** text agent (decizia) → card tool (🔧 nume + cod MATLAB vizibil cu syntax highlight) → rezultat (output + figură). Mapează exact decizie→tool→rezultat.
- **Feedback așteptare:** la „tool_use start" cardul apare imediat în stare „running" cu spinner („rulează în MATLAB…") → se umple la „tool_result". Face latența vizibilă, nu înghețată.
- **Figuri:** inline la lățimea coloanei + **click pentru lightbox full-screen** (esențial la 50/50 pe Teams).
- **Erori:** card curat cu accent roșu sobru + traceback real ascuns sub un expand (susține S4).
- **Butoane prompt:** secvență numerotată (1: mass-spring-damper, 2: overshoot/settling, 3: Simulink), toate vizibile și re-clickabile, + un buton „extra sigur".
- **Reset:** curăță timeline + trimite `close all; clear` în MATLAB.
- **Empty state:** titlu + butoane + o linie de context („chatbot care conduce MATLAB/Simulink live prin MCP").
- **Default-uri presupuse:** auto-scroll care urmărește ultimul card (fără smucitură dacă derulezi sus), font sans de sistem + mono pentru cod, scroll orizontal pe blocurile de cod lungi.

### Staging Teams (screen-share)
- Partajezi **ecran complet, browser + MATLAB 50/50** (alegere asumată: maxim „ambele live", cu condițiile de mai jos).
- **Obligatoriu la repetiție** ca 50/50 să fie lizibil prin Teams: font MATLAB Command Window ~16-18pt (+ Editor), carduri funcționale în coloană îngustă, și test pe un apel Teams de probă văzând ce ajunge la celălalt capăt.

## Testing Decisions

### Seam-ul principal de testare: Mock MCP (**Must**)
Cel mai înalt seam din sistem. Un server MCP fals (stdio) cu un tool `echo` permite validarea **întregului lanț** (browser → FastAPI → SSE → tool_runner → wrapper → UI carduri) **fără MATLAB**. Dacă lanțul merge cu mock-ul, singura necunoscută rămasă e binarul real — izolăm riscul devreme. Acesta e și pivotul fazei F1.

### Ce face un test bun aici
- Testează **comportamentul extern observabil**, nu detalii de implementare: „un mesaj trimis din UI produce evenimente SSE `tool_use`/`tool_result` în ordinea corectă", nu „funcția X a fost apelată".
- Wrapper-ul de tool e un seam natural: poate fi testat că emite evenimentele SSE corecte și declanșează detecția de figuri, injectând un client MCP fals.

### Module testate
- **Backend ↔ MCP (prin Mock MCP):** mesaj → bucla tool_runner → evenimente SSE. Fără MATLAB, fără API real (sau cu un stub de model).
- **Wrapper-ul de tool:** emite `tool_use start` + `tool_result`, detectează un PNG nou în folderul de figuri.
- **Detecția de figuri:** un fișier nou apărut în folder după un tool_result e emis o singură dată pe SSE (nu re-emis).
- **Validare manuală la F2 (nu automat):** că modul `existing` prinde sesiunea R2026a după `shareEngine`; că base workspace-ul persistă între apeluri `evaluate`; latența opus-4-8 la prima repetiție.

### Prior art
Greenfield — nu există cod încă. Testele backend-ului urmează patternul standard de test SSE/async pentru FastAPI; Mock MCP-ul e un server `mcp` minimal cu un singur tool.

## Out of Scope
- Autentificare multi-user, conturi, sesiuni persistente.
- Deployment pe server / containerizare.
- **Modificarea/scrierea de modele `.slx` de către agent** — deși toolkit-ul o permite, demo-ul e read+simulate (mai sigur și aliniat ISO 26262). Menționat ca direcție viitoare, nu construit.
- Streaming token-cu-token (rămâne Could/faza 2; granularitatea per-mesaj e *intenționat* ideală pentru a arăta pasul agentic).
- Rularea pe instanța MATLAB a firmei — rulăm pe laptopul meu; conectarea la instanța lor o menționez ca opțiune viitoare.
- Integrare cu Polarion/Jira/AWS Bedrock — menționate verbal ca viziune.
- Branding complet cu logo Schaeffler proeminent — folosim doar accent discret, pentru a evita aerul prezumțios și riscul de folosire neautorizată a mărcii.
- **Workflow-ul VSCode + agent + MATLAB MCP** — artefact separat (Demo 1 în prezentare), spec-uit ulterior după ce web app-ul e gata. Acest PRD nu îl acoperă; vezi §Solution → „Două artefacte".

## Further Notes

### Faze & milestone-uri
- **F0 — Prerechizite:** install `simulink-agentic-toolkit` (aduce și core server-ul) + `ant auth login` + construiește `demo.slx` (mass-spring-damper cu To Workspace) + verifică toolbox-urile cu `detect_matlab_toolboxes`.
- **F1 — Schelet end-to-end + Mock MCP (Must):** FastAPI + UI cu carduri timeline + SSE + tool_runner + wrapper, validate cu Mock MCP `echo`. **Fără MATLAB.** Criteriu: un mesaj din browser → agentul cheamă `echo` → cardul apare „running" apoi se umple, prin SSE.
- **F2 — MATLAB live:** core server real, `existing` strict, validează persistența workspace + promptul mass-spring-damper rulează și întoarce output.
- **F3 — Wow factor:** figuri inline (wrapper + watch + lightbox) + demo Simulink read/sim pe `demo.slx` + `check_matlab_code` ca beat vizibil.
- **F4 (opțional):** standarde de cod explicite în system prompt, polish UI, streaming token-cu-token.

### Riscuri & mitigări
| Risc | Impact | Mitigare |
|------|--------|----------|
| Install toolkit eșuează | Blocant F2 | F1 cu Mock MCP elimină dependența până e gata; testez `.mltbx` izolat înainte. |
| Demo live pică | Catastrofal (S1) | Mock MCP izolează riscul; repet 3x; înregistrare video + screenshot de rezervă. |
| 50/50 pe Teams ilizibil | Slăbește S3/S1 | Font MATLAB mărit, carduri în coloană îngustă, test pe apel Teams de probă. |
| Latență opus-4-8 mare | Slăbește impactul | Fallback sonnet-4-6; effort medium; model Simulink mic; prompturi scurte. |
| Workspace curățat între apeluri | Cade follow-up-ul | Re-derivare defensivă în system prompt (hibrid). |
| `existing` nu prinde sesiunea | Figura „dispare" | Mod strict (eșec zgomotos la pre-flight) + pas `shareEngine` în checklist. |
| Cod arbitrar nedorit | Risc de imagine | Demo scriptat, butoane fixe; guardrail read-only/no-destructive în system prompt. |
| Confidențialitate IP | Obiecție la firmă auto | Argument pregătit: core server local, codul nu părăsește rețeaua. |

### De definit înainte de build (verificări, nu decizii de design)
- Textul precis al celor 3 prompturi scriptate + promptul „extra sigur".
- Conținutul exact al system prompt-ului.
- Structura scriptului de pre-flight.
- Lista exactă de toolbox-uri cerute de `demo.slx`.
