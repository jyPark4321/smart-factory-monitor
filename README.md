# smartfactory-monitor
스마트팩토리의 생산 데이터 및 계획을 관리하는 node.js 기반 웹페이지


## 개발 기간
23.04.20~23.06.20


## 실행 방법
우선 실행 조건이 필요합니다
- Node.js
- Python

이 저장소를 클론합니다:
`git clone https://github.com/ihh0/smartfactory-monitor.git`

클론한 저장소로 이동해 프로젝트 종속성을 설치합니다:
`cd smartfactory-monitor`
`npm install`

프로젝트를 실행합니다:
`node app.js`

웹 브라우저에서 http://localhost:3000으로 접속하여 웹사이트를 확인합니다.


## 주요 기능
- 생산 주문을 볼수 있고 이를 수집해 최적화된 생산계획을 세웁니다
- 원하는 기간 내의 주문에 대해 생산계획 최적화 수행을 요청할 수 있습니다.
