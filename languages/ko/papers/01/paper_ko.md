# SuperInstance: 보편적 셀 아키텍처
## AI 스프레드시트 시스템을 위한 새로운 패러다임

**저자:** POLLN 연구팀
**날짜:** 2026년 3월
**상태:** 초안 v0.1 - 3차 검토

---

## 초록

SuperInstance는 인공지능 시스템을 위한 스프레드시트 메타포의 근본적인 재개념화를 나타냅니다. 셀을 수동적인 데이터 컨테이너로 취급하는 대신, 우리는 모든 셀이 데이터 블록, 실행 중인 프로세스, AI 에이전트, 저장 시스템, API, 심지어 다른 SuperInstance까지 어떤 계산 타입의 인스턴스도 될 수 있는 타입 시스템을 소개합니다. 이 논문은 SuperInstance 시스템을 위한 형식 명세, 타입 계층 구조, 그리고 구현 아키텍처를 제시합니다.

**주요 기여:**
- 10개 이상의 인스턴스 타입을 지원하는 보편적 셀 타입 시스템
- 지능형 상태 추적을 위한 변화율 기반 변화 메커니즘
- 분산 컴퓨팅을 위한 기준점 중심 참조 시스템
- 안정적인 AI 운영을 위한 신뢰도 캐스케이드 아키텍처

---

## 1. 서론

전통적인 스프레드시트는 셀을 정적 데이터를 위한 수동적인 컨테이너로 취급합니다. SuperInstance 패러다임은 이 관계를 근본적으로 재구상합니다: 모든 셀은 어떤 타입의 인스턴스도 될 수 있는 능동적인 계산 엔티티입니다.

### 1.1 동기

AI와 스프레드시트 인터페이스의 융합(Claude-Excel 통합으로 예시됨)은 지능적이고 컨텍스트 인식 셀의 가치를 보여줍니다. 그러나 현재 구현은 특정 사용 사례에 제한되어 있습니다. SuperInstance는 어떤 셀이든 어떤 계산 엔티티로도 만들 수 있는 일반 목적 프레임워크를 제공합니다.

### 1.2 핵심 통찰: 변화율 기반 변화

우리의 LOG-Tensor 연구에서, 우리는 **변화율 기반 변화**가 절대적 위치 시스템에 비해 우수한 상태 추적을 제공한다는 것을 발견했습니다:

```
변화율 우선 형식주의: x(t) = x₀ + ∫r(τ)dτ
```

절대적 상태를 추적하는 대신, SuperInstance 셀은 변화율을 추적하여 다음을 가능하게 합니다:
- 예측적 상태 추정
- 데드밴드 트리거를 통한 이상 감지
- 알려진 상태 간의 부드러운 보간
- 희소 업데이트의 자연스러운 처리

---

## 2. 타입 시스템 아키텍처

### 2.1 핵심 타입 계층 구조

```typescript
// 핵심 SuperInstance 타입들
type CellType =
  | 'data'           // 전통적인 데이터 저장
  | 'process'        // 실행 중인 계산 프로세스
  | 'agent'          // 자율성을 가진 AI 에이전트
  | 'storage'        // 파일/폴더/ZIP 저장소
  | 'api'            // 외부 API 연결
  | 'terminal'       // PowerShell/Docker 셸
  | 'reference'      // 다른 셀에 대한 참조
  | 'superinstance'  // 중첩된 SuperInstance
  | 'tensor'         // 텐서 계산
  | 'observer';      // 모니터링 에이전트

interface SuperInstanceCell {
  id: CellId;
  type: CellType;
  content: CellContent;
  state: CellState;
  dependencies: CellId[];
  observers: CellId[];
  rateOfChange: RateVector;
  originReference: OriginPoint;
  confidence: ConfidenceScore;
}
```

### 2.2 기준점 중심 참조 시스템

각 셀은 자신의 기준점 참조 프레임을 유지합니다:

```typescript
interface OriginReference {
  // 이 셀의 기준점에 상대적인 위치
  relativePosition: Vector3D;

  // 이 관점에서의 변화율
  rateVector: RateVector;

  // 이 측정의 신뢰도
  confidence: number; // 0-1
}
```

이것은 다음을 가능하게 합니다:
- **분산 컴퓨팅:** 글로벌 좌표계가 필요 없음
- **확장 가능한 참조:** 각 셀이 자신에 상대적인 변화를 추적
- **자연스러운 연합:** 셀이 글로벌 재인덱싱 없이 참여/탈퇴 가능

### 2.3 변화율 기반 상태 추적

```typescript
interface RateBasedState {
  currentValue: any;
  rateOfChange: number;
  acceleration: number; // 2차 도함수
  lastUpdate: Timestamp;

  // 미래 시간의 상태 예측
  predictState(atTime: Timestamp): any {
    const dt = atTime - this.lastUpdate;
    return this.currentValue +
           this.rateOfChange * dt +
           0.5 * this.acceleration * dt * dt;
  }
}
```

---

## 3. 신뢰도 캐스케이드 아키텍처

### 3.1 데드밴드 트리거

셀은 변화가 구성된 데드밴드를 초과할 때 지능적 처리를 활성화합니다:

```typescript
interface DeadbandTrigger {
  threshold: number;
  deadband: number;

  shouldTrigger(newValue: number, oldValue: number): boolean {
    const change = Math.abs(newValue - oldValue);
    const relativeChange = change / Math.max(Math.abs(oldValue), 1);
    return relativeChange > this.deadband;
  }
}
```

### 3.2 캐스케이드 레벨

트리거가 발생하면 지능이 캐스케이딩 레벨에서 활성화됩니다:

```
레벨 1: 작은 에이전트들 (빠름, 저자원)
    ↓ 임계값 초과 시
레벨 2: 도메인 전문가들 (중간, 집중적)
    ↓ 복잡도 높을 시
레벨 3: 증류된 LLM (포괄적 분석)
```

### 3.3 신뢰도를 통한 안정성

```typescript
interface ConfidenceCascade {
  // 신뢰도는 안정적인 셀에서 종속 셀로 흐름
  propagateConfidence(source: CellId, target: CellId): void {
    const sourceConfidence = this.getCell(source).confidence;
    const dependencyStrength = this.getDependencyStrength(source, target);

    // 신뢰도는 거리에 따라 감쇠
    const propagatedConfidence = sourceConfidence * dependencyStrength;

    this.getCell(target).updateConfidence(propagated);
  }
}
```

---