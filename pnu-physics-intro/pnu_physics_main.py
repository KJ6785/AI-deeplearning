import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from jinja2 import Template

# 1. FastAPI 애플리케이션 정의
app = FastAPI(title="Pusan National University Physics - Global Intro")

# 2. 하이엔드 UI (Tailwind CSS 3.4+ 디자인 대시보드)
# 부산대학교 브랜드 컬러: PNU Blue (#005BAA), Natural Science Gold (#B97C24)
PNU_PHYSICS_HTML = """
<!DOCTYPE html>
<html lang="ko" class="scroll-smooth">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>부산대학교 물리학과 | Department of Physics, PNU</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@100;300;400;600;700;800&family=Noto+Sans+KR:wght@100;300;400;700;900&family=Libre+Baskerville:ital@0;1&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Inter', 'Noto Sans KR', sans-serif; background-color: #ffffff; }
        .serif { font-family: 'Libre+Baskerville', serif; }
        .pnu-blue { color: #005BAA; }
        .bg-pnu-blue { background-color: #005BAA; }
        .pnu-gold { color: #B97C24; }
        .bg-pnu-gold { background-color: #B97C24; }
        .glass-card { background: rgba(255, 255, 255, 0.85); backdrop-filter: blur(20px); border: 1px solid rgba(255, 255, 255, 0.2); }
        .hero-zoom:hover img { transform: scale(1.05); }
        .section-fade { transition: all 1s ease-out; }
        .gradient-text { background: linear-gradient(135deg, #005BAA 0%, #B97C24 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    </style>
</head>
<body class="text-slate-900 antialiased overflow-x-hidden">

    <!-- Navigation -->
    <nav class="fixed top-0 w-full z-[100] transition-all duration-300 glass-card border-b border-slate-100">
        <div class="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
            <div class="flex items-center gap-4">
                <div class="w-12 h-12 bg-pnu-blue rounded-full flex items-center justify-center shadow-lg">
                    <svg class="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z"></path></svg>
                </div>
                <div>
                    <h1 class="text-lg font-black tracking-tighter pnu-blue leading-none">PNU PHYSICS</h1>
                    <p class="text-[10px] font-bold text-slate-400 uppercase tracking-widest mt-1">EST. 1954</p>
                </div>
            </div>
            <div class="hidden lg:flex items-center gap-10 text-sm font-bold tracking-tight">
                <a href="#vision" class="hover:text-pnu-blue transition-colors">VISION</a>
                <a href="#research" class="hover:text-pnu-blue transition-colors">RESEARCH</a>
                <a href="#labs" class="hover:text-pnu-blue transition-colors">LABORATORIES</a>
                <a href="#contact" class="hover:text-pnu-blue transition-colors">CONTACT</a>
                <a href="https://phys.pusan.ac.kr/phys/index.do" target="_blank" class="px-5 py-2.5 bg-pnu-blue text-white rounded-full hover:bg-blue-700 transition-all shadow-md shadow-blue-200">PORTAL</a>
            </div>
        </div>
    </nav>

    <!-- Hero Section -->
    <header class="relative w-full h-screen flex items-center justify-center overflow-hidden bg-slate-950">
        <!-- Abstract Physics Background -->
        <div class="absolute inset-0 opacity-40">
            <div class="absolute inset-0 bg-gradient-to-b from-slate-950 via-slate-950 to-pnu-blue/30"></div>
            <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-pnu-blue/20 blur-[150px] rounded-full"></div>
            <div class="absolute top-1/4 right-1/4 w-[400px] h-[400px] bg-pnu-gold/10 blur-[120px] rounded-full"></div>
        </div>
        
        <div class="relative z-10 max-w-6xl mx-auto px-6 text-center space-y-8">
            <div class="inline-block px-4 py-1.5 rounded-full border border-pnu-gold/30 bg-pnu-gold/5 text-pnu-gold text-xs font-black tracking-[0.3em] uppercase mb-4 animate-bounce">
                Exploring the Universe's Order
            </div>
            <h2 class="text-5xl md:text-8xl font-black text-white tracking-tighter leading-none">
                질서와 진리, <br><span class="gradient-text">물리학의 미래</span>
            </h2>
            <p class="max-w-2xl mx-auto text-lg md:text-xl text-slate-400 font-light leading-relaxed">
                1954년 개설 이래, 부산대학교 물리학과는 우주의 근본 원리를 탐구하며 대한민국 기초 과학의 발전을 이끌어왔습니다. 우리는 이제 지식의 경계를 넘어 기술 혁신을 주도합니다.
            </p>
            <div class="flex flex-col md:flex-row items-center justify-center gap-6 pt-10">
                <a href="#research" class="group relative px-10 py-5 bg-white text-pnu-blue rounded-2xl font-black text-lg transition-all hover:scale-105 active:scale-95 shadow-2xl">
                    연구 분야 살펴보기
                </a>
                <a href="https://phys.pusan.ac.kr/phys/index.do" class="px-10 py-5 border border-white/20 text-white rounded-2xl font-black text-lg hover:bg-white/5 transition-all">
                    공식 홈페이지 방문
                </a>
            </div>
        </div>

        <!-- Scroll Indicator -->
        <div class="absolute bottom-10 left-1/2 -translate-x-1/2 text-white/30 animate-bounce">
            <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 14l-7 7m0 0l-7-7m7 7V3"></path></svg>
        </div>
    </header>

    <!-- Section: Vision -->
    <section id="vision" class="py-32 px-6 bg-white">
        <div class="max-w-7xl mx-auto">
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-20 items-center">
                <div class="space-y-10">
                    <div class="space-y-4">
                        <span class="text-sm font-black pnu-blue tracking-widest uppercase">Our Mission</span>
                        <h3 class="text-4xl md:text-6xl font-black pnu-blue tracking-tighter">진리를 향한 <br>끊임없는 도전</h3>
                    </div>
                    <p class="text-lg text-slate-600 leading-relaxed">
                        부산대학교 물리학과는 <b>진리 탐구, 자유로운 사고, 사회 봉사</b>의 정신을 바탕으로, 이론과 실험의 조화로운 교육을 지향합니다. 인공지능, 퀀텀 컴퓨팅, 신소재 등 미래 산업의 핵심 동력이 될 차세대 리더를 양성합니다.
                    </p>
                    <div class="grid grid-cols-2 gap-8 pt-6">
                        <div class="space-y-2">
                            <p class="text-4xl font-black pnu-gold serif italic tracking-tighter">01</p>
                            <h4 class="font-bold text-slate-900 uppercase tracking-widest text-xs">창의적 인재 양성</h4>
                            <p class="text-sm text-slate-500 font-light">물리적 직관과 논리적 사고를 갖춘 전문가</p>
                        </div>
                        <div class="space-y-2">
                            <p class="text-4xl font-black pnu-gold serif italic tracking-tighter">02</p>
                            <h4 class="font-bold text-slate-900 uppercase tracking-widest text-xs">글로벌 연구 경쟁력</h4>
                            <p class="text-sm text-slate-500 font-light">세계 최고 수준의 연구 성과 창출</p>
                        </div>
                    </div>
                </div>
                <div class="relative group">
                    <div class="absolute -inset-4 bg-gradient-to-tr from-pnu-blue/20 to-pnu-gold/20 rounded-3xl blur-2xl group-hover:blur-3xl transition-all duration-500"></div>
                    <div class="relative aspect-square rounded-3xl overflow-hidden shadow-2xl">
                        <img src="https://images.unsplash.com/photo-1532094349884-543bc11b234d?q=80&w=2070&auto=format&fit=crop" alt="Lab Vision" class="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110">
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Section: Research Areas -->
    <section id="research" class="py-32 px-6 bg-slate-50">
        <div class="max-w-7xl mx-auto space-y-20">
            <div class="text-center space-y-6">
                <span class="text-sm font-black pnu-blue tracking-widest uppercase">Major Research</span>
                <h3 class="text-4xl md:text-6xl font-black pnu-blue tracking-tighter">연구의 지평을 넓히다</h3>
                <div class="w-20 h-1 bg-pnu-gold mx-auto"></div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
                <!-- Research Card 1 -->
                <div class="group bg-white p-8 rounded-[2.5rem] border border-slate-100 shadow-sm hover:shadow-2xl hover:-translate-y-2 transition-all duration-500">
                    <div class="w-16 h-16 bg-pnu-blue/5 rounded-2xl flex items-center justify-center mb-8 group-hover:bg-pnu-blue group-hover:text-white transition-colors duration-500">
                        <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
                    </div>
                    <h4 class="text-xl font-black pnu-blue mb-4 tracking-tight uppercase">High Energy Physics</h4>
                    <p class="text-sm text-slate-500 leading-relaxed font-light">
                        입자 가속기를 활용한 표준 모형 검증 및 새로운 물리 현상을 탐구하는 소립자 물리 연구의 정점.
                    </p>
                </div>
                <!-- Research Card 2 -->
                <div class="group bg-white p-8 rounded-[2.5rem] border border-slate-100 shadow-sm hover:shadow-2xl hover:-translate-y-2 transition-all duration-500">
                    <div class="w-16 h-16 bg-pnu-blue/5 rounded-2xl flex items-center justify-center mb-8 group-hover:bg-pnu-blue group-hover:text-white transition-colors duration-500">
                        <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z"></path></svg>
                    </div>
                    <h4 class="text-xl font-black pnu-blue mb-4 tracking-tight uppercase">Condensed Matter</h4>
                    <p class="text-sm text-slate-500 leading-relaxed font-light">
                        신소재, 초전도체, 나노 소자 연구를 통해 차세대 반도체 및 에너지 혁명을 주도하는 응집물리학.
                    </p>
                </div>
                <!-- Research Card 3 -->
                <div class="group bg-white p-8 rounded-[2.5rem] border border-slate-100 shadow-sm hover:shadow-2xl hover:-translate-y-2 transition-all duration-500">
                    <div class="w-16 h-16 bg-pnu-blue/5 rounded-2xl flex items-center justify-center mb-8 group-hover:bg-pnu-blue group-hover:text-white transition-colors duration-500">
                        <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 10l-2 1m0 0l-2-1m2 1v2.5M20 7l-2 1m0 0l-2-1m2 1v2.5M14 4l-2 1m0 0l-2-1m2 1v2.5M4 7l-2 1m0 0l-2-1m2 1v2.5M7 10l-2 1m0 0l-2-1m2 1v2.5M7 4l-2 1m0 0l-2-1m2 1v2.5"></path></svg>
                    </div>
                    <h4 class="text-xl font-black pnu-blue mb-4 tracking-tight uppercase">Nuclear Physics</h4>
                    <p class="text-sm text-slate-500 leading-relaxed font-light">
                        원자핵의 구조와 성질을 이해하고, 청정 에너지원인 핵융합 연구의 핵심 난제를 해결하는 원자핵 물리.
                    </p>
                </div>
                <!-- Research Card 4 -->
                <div class="group bg-white p-8 rounded-[2.5rem] border border-slate-100 shadow-sm hover:shadow-2xl hover:-translate-y-2 transition-all duration-500">
                    <div class="w-16 h-16 bg-pnu-blue/5 rounded-2xl flex items-center justify-center mb-8 group-hover:bg-pnu-blue group-hover:text-white transition-colors duration-500">
                        <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path></svg>
                    </div>
                    <h4 class="text-xl font-black pnu-blue mb-4 tracking-tight uppercase">Applied Physics</h4>
                    <p class="text-sm text-slate-500 leading-relaxed font-light">
                        양자 역학적 원리를 실생활에 적용하는 양자 정보, 광학, 바이오 물리 등 융합 연구의 최전선.
                    </p>
                </div>
            </div>
        </div>
    </section>

    <!-- Section: Statistics / Achievement -->
    <section class="py-32 px-6 bg-pnu-blue text-white relative overflow-hidden">
        <div class="absolute inset-0 opacity-10">
            <svg class="w-full h-full" viewBox="0 0 100 100" preserveAspectRatio="none">
                <path d="M0 50 Q 25 40, 50 50 T 100 50" fill="none" stroke="white" stroke-width="0.5" />
                <path d="M0 60 Q 25 50, 50 60 T 100 60" fill="none" stroke="white" stroke-width="0.5" />
            </svg>
        </div>
        <div class="relative z-10 max-w-7xl mx-auto grid grid-cols-2 lg:grid-cols-4 gap-12 text-center">
            <div class="space-y-4">
                <p class="text-5xl md:text-7xl font-black serif italic">70+</p>
                <p class="text-xs font-bold tracking-[0.3em] text-blue-200 uppercase">Years of History</p>
            </div>
            <div class="space-y-4">
                <p class="text-5xl md:text-7xl font-black serif italic">25+</p>
                <p class="text-xs font-bold tracking-[0.3em] text-blue-200 uppercase">Faculty Members</p>
            </div>
            <div class="space-y-4">
                <p class="text-5xl md:text-7xl font-black serif italic">12+</p>
                <p class="text-xs font-bold tracking-[0.3em] text-blue-200 uppercase">Research Labs</p>
            </div>
            <div class="space-y-4">
                <p class="text-5xl md:text-7xl font-black serif italic">3k+</p>
                <p class="text-xs font-bold tracking-[0.3em] text-blue-200 uppercase">Global Alumni</p>
            </div>
        </div>
    </section>

    <!-- Footer -->
    <footer id="contact" class="bg-white pt-24 pb-12 px-6 border-t border-slate-100">
        <div class="max-w-7xl mx-auto">
            <div class="grid grid-cols-1 lg:grid-cols-3 gap-16 mb-24">
                <div class="space-y-8">
                    <div class="flex items-center gap-3">
                        <div class="w-10 h-10 bg-pnu-blue rounded-xl flex items-center justify-center">
                            <span class="text-white font-black">P</span>
                        </div>
                        <h5 class="text-xl font-black pnu-blue tracking-tighter">Department of Physics, PNU</h5>
                    </div>
                    <p class="text-slate-500 text-sm leading-relaxed max-w-sm">
                        부산대학교 물리학과는 세계적 수준의 연구와 창의적 교육을 통해 물리학의 발전을 선도하고 인류의 지식 지평을 넓히는 데 기여하고 있습니다.
                    </p>
                </div>
                <div class="grid grid-cols-2 gap-8 lg:col-span-2">
                    <div class="space-y-6">
                        <h6 class="text-xs font-black pnu-blue uppercase tracking-widest">Resources</h6>
                        <ul class="space-y-4 text-sm text-slate-500">
                            <li><a href="#" class="hover:text-pnu-blue transition-colors">학과 행정실</a></li>
                            <li><a href="#" class="hover:text-pnu-blue transition-colors">학생회 및 커뮤니티</a></li>
                            <li><a href="#" class="hover:text-pnu-blue transition-colors">입학 가이드</a></li>
                            <li><a href="#" class="hover:text-pnu-blue transition-colors">장학 제도</a></li>
                        </ul>
                    </div>
                    <div class="space-y-6">
                        <h6 class="text-xs font-black pnu-blue uppercase tracking-widest">Contact Us</h6>
                        <p class="text-sm text-slate-500 leading-relaxed">
                            (46241) 부산광역시 금정구 부산대학로63번길 2 <br>
                            부산대학교 제1물리관 201호 <br>
                            TEL: 051-510-1881 <br>
                            FAX: 051-513-7664
                        </p>
                    </div>
                </div>
            </div>
            <div class="pt-12 border-t border-slate-100 flex flex-col md:flex-row justify-between items-center gap-6">
                <p class="text-[10px] font-bold text-slate-400 tracking-widest uppercase">© 2026 PUSAN NATIONAL UNIVERSITY. DEPARTMENT OF PHYSICS.</p>
                <div class="flex gap-8 text-[10px] font-bold text-slate-400 tracking-widest uppercase">
                    <a href="#" class="hover:text-pnu-blue transition-colors">Privacy Policy</a>
                    <a href="#" class="hover:text-pnu-blue transition-colors">Terms of Service</a>
                </div>
            </div>
        </div>
    </footer>

</body>
</html>
"""

# 3. 엔드포인트 정의
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    template = Template(PNU_PHYSICS_HTML)
    return template.render()

# 4. 서버 실행
if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 Pusan National University Physics Dept Intro Page is Live!")
    print("🔗 Access URL: http://127.0.0.1:8000")
    print("="*60 + "\n")
    uvicorn.run(app, host="127.0.0.1", port=8000)
