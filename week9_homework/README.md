# 통합 물리 시뮬레이터 (Integrated Physics Simulator)

이 프로젝트는 고전 역학의 주요 개념들을 수치 시뮬레이션으로 구현한 통합 도구입니다.

## 🚀 주요 기능
1. **수치 적분 비교**: 오일러(Euler) 방법과 RK4 방법의 정확도 차이 분석
2. **행성 운동**: 만유인력 법칙을 기반으로 한 케플러 법칙 검증
3. **혼돈 시스템**: 이중 진자를 통한 초기 조건 민감성(나비 효과) 시연
4. **역학 정식화**: 뉴턴, 라그랑지안, 해밀토니안 역학의 결과 동등성 확인
5. **3체 문제**: 천체 역학의 난제 중 하나인 Figure-8 궤도 재현

## 💻 사용 방법
이 프로그램은 명령행 인자(CLI)와 대화형 메뉴를 모두 지원합니다.

### 1. 모든 실험 일괄 실행
```bash
python integrated_physics_sim.py --all
```

### 2. 특정 실험(Lab)만 실행
```bash
python integrated_physics_sim.py --lab [1-5]
# 예: Lab 3(혼돈 시스템) 실행
python integrated_physics_sim.py --lab 3
```

### 3. 대화형 메뉴 사용
아무 인자 없이 실행하면 메뉴가 나타납니다.
```bash
python integrated_physics_sim.py
```

## 📂 결과 확인
모든 시뮬레이션 결과(그래프)는 `outputs/` 폴더 내의 각 실험별 하위 폴더에 저장됩니다.
- `outputs/lab1/`: 수치 적분 비교
- `outputs/lab2/`: 행성 궤도
- `outputs/lab3/`: 혼돈 시스템
- `outputs/lab4/`: 역학 정식화
- `outputs/lab5/`: 3체 문제
